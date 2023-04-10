import datetime
import unittest
from faker import Faker
from create import Base, MonthlyCommission, Office, Sale, House, Agent, Buyer, Seller
from insert import generate_date, generate_email, generate_name, generate_agents, generate_offices, generate_houses, generate_buyers, generate_sellers, generate_sales, populate_agent_office_association
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestModels(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)

    def tearDown(self):
        self.session.rollback()

    def test_create_agent(self):
        """
        Tests that an agent can be created and added to the database.
        """
        agent = Agent(name='John Doe', phone='123-456-5555', email='johndoe@example.com')
        self.session.add(agent)
        self.session.commit()

        result = self.session.query(Agent).filter_by(name='John Doe').first()
        self.assertEqual(result.name, 'John Doe')
        self.assertEqual(result.phone, '123-456-5555')
        self.assertEqual(result.email, 'johndoe@example.com')

    def test_agent_commission(self):
        """
        Tests that the agent commission is calculated correctly.
        """
        agent = Agent(name='John Doe', phone='123-456-5555', email='johndoe@example.com')
        sale = Sale(house_id=1, seller_id=1, buyer_id=1, agent=agent, office_id=1, date_of_sale=datetime.date(2022, 1, 1), sale_price=200000)
        self.session.add(agent)
        self.session.add(sale)
        self.session.commit()

        result = self.session.query(Sale).filter_by(agent_id=agent.id).first()
        self.assertEqual(result.agent_commission, 12000.0)

    def test_sale(self):
        """
        Tests that a sale can be created and added to the database.
        """
        house = House(num_bedrooms=3, num_bathrooms=2, listing_price=250000, zip_code='12345', date_of_listing=datetime.date(2022, 1, 1), status='Not Sold', seller_id=1, buyer_id=2, agent_id=3, office_id=4)
        self.session.add(house)
        self.session.commit()

        sale = Sale(house_id=1, seller_id=1, buyer_id=2, agent_id=3, office_id=4, date_of_sale=datetime.date(2022, 1, 1), sale_price=275000)
        self.session.add(sale)
        self.session.commit()

        result = self.session.query(Sale).first()
        self.assertEqual(result.house_id, 1)
        self.assertEqual(result.seller_id, 1)
        self.assertEqual(result.buyer_id, 2)
        self.assertEqual(result.agent_id, 3)
        self.assertEqual(result.office_id, 4)
        self.assertEqual(result.date_of_sale, datetime.date(2022, 1, 1))
        self.assertEqual(result.sale_price, 275000)
        self.assertEqual(result.agent_commission, 16500.0)

    def test_monthly_commission(self):
        """
        Tests that a monthly commission can be created and added to the database.
        """
        agent = Agent(name='John Doe', phone='555-555-5555', email='johndoe@example.com')
        self.session.add(agent)
        self.session.commit()

        monthly_commission = MonthlyCommission(month=1, year=2022, agent_id=1, total_commission=10000)
        self.session.add(monthly_commission)
        self.session.commit()

        result = self.session.query(MonthlyCommission).first()
        self.assertEqual(result.month, 1)
        self.assertEqual(result.year, 2022)
        self.assertEqual(result.agent_id, 1)
        self.assertEqual(result.total_commission, 10000)

class TestDataGenerator(unittest.TestCase):
    def setUp(self):
        self.fake = Faker('en_US')
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def test_generate_date(self):
        """
        Tests that the generate_date function returns a date between the start date and today.
        """
        start_date = datetime.date(2022, 1, 1)
        end_date = datetime.date.today()
        random_date = generate_date(start_date)
        self.assertGreaterEqual(random_date, start_date)
        self.assertLessEqual(random_date, end_date)

    def test_generate_email(self):
        """
        Tests that the generate_email function returns a valid email address.
        """
        first_name = 'John'
        last_name = 'Doe'
        email = generate_email(first_name, last_name)
        self.assertEqual(email, 'john.doe@email.com')

    def test_generate_name(self):
        """
        Tests that the generate_name function returns a valid name.
        """
        first_name = 'John'
        last_name = 'Doe'
        full_name = generate_name(first_name, last_name)
        self.assertEqual(full_name, 'John Doe')

    def test_generate_agents(self):
        """
        Tests that the generate_agents function returns a list of agents.
        """
        agents = generate_agents()
        self.assertEqual(len(agents), 20)
        for agent in agents:
            self.assertIsInstance(agent, Agent)

    def test_generate_offices(self):
        """
        Tests that the generate_offices function returns a list of offices.
        """
        offices = generate_offices()
        self.assertEqual(len(offices), 7)
        for office in offices:
            self.assertIsInstance(office, Office)

    def test_populate_agent_office_association(self):
        """
        Tests that the populate_agent_office_association function populates the agent_office_association table.
        """
        agents = generate_agents()
        offices = generate_offices()
        self.session.add_all(agents)
        self.session.add_all(offices)
        self.session.commit()
        populate_agent_office_association(self.session)
        for agent in agents:
            self.assertGreater(len(agent.offices), 0)

    def test_generate_buyers(self):
        """
        Tests that the generate_buyers function returns a list of buyers.
        """
        buyers = generate_buyers()
        self.assertEqual(len(buyers), 200)
        for buyer in buyers:
            self.assertIsInstance(buyer, Buyer)

    def test_generate_sellers(self):
        """
        Tests that the generate_sellers function returns a list of sellers.
        """
        sellers = generate_sellers()
        self.assertEqual(len(sellers), 70)
        for seller in sellers:
            self.assertIsInstance(seller, Seller)

    def test_generate_houses(self):
        """
        Tests that the generate_houses function returns a list of houses.
        """
        agents = generate_agents()
        offices = generate_offices()
        sellers = generate_sellers()
        self.session.add_all(agents)
        self.session.add_all(offices)
        self.session.add_all(sellers)
        self.session.commit()
        houses = generate_houses(self.session)
        self.assertEqual(len(houses), 100)
        for house in houses:
            self.assertIsInstance(house, House)
            self.assertIn(house.agent_id, [agent.id for agent in agents])
            self.assertIn(house.office_id, [office.id for office in offices])
            self.assertIn(house.seller_id, [seller.id for seller in sellers])


if __name__ == '__main__':
    unittest.main()