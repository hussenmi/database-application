import random
from faker import Faker
from faker.providers import address
from create import Base, Agent, Office, Buyer, Seller, House, Sale
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

fake = Faker('en_US')

num_of_houses = 100
num_of_sales = int(num_of_houses * 0.8)  # about 80% of houses are sold
num_of_buyers = 200
num_of_sellers = 70
num_of_agents = 20
num_of_offices = 7

def generate_date(start_date=datetime.date(2022,1,1)):
    """
    Generate a random date between the start date (initialized to be Jan 1 2022) and the current date.
    returns:
        random_date: date object
    """
    end_date = datetime.date.today()
    delta = end_date - start_date
    days = delta.days

    # Generate a random number of days between 0 and the number of days
    random_date = start_date + datetime.timedelta(days=fake.random_int(min=0, max=days))

    return random_date

def generate_email(first_name, last_name):
    """
    Return a properly formatted email address using the first and last name.
    params:
        first_name: str
        last_name: str
    returns:
        email: str
    """
    email = f"{first_name.lower()}.{last_name.lower()}@email.com"
    
    return email

def generate_name(first_name, last_name):
    """
    Create a variable that combines the first_name and last_name with a space
    params:
        first_name: str
        last_name: str
    returns:
        full_name: str
    """
    full_name = f"{first_name} {last_name}"

    return full_name

# Generate fake data for agents
def generate_agents():
    """
    Generates fake data for agents.
    returns:
        agents: a list of Agent objects
    """
    agents = []
    for _ in range(num_of_agents):
        first_name = fake.first_name()
        last_name = fake.last_name()

        agent = Agent(name=generate_name(first_name, last_name), phone=fake.numerify('###-###-####'), email=generate_email(first_name, last_name))
        agents.append(agent)
    return agents

# Generate fake data for offices
def generate_offices():
    """
    Generates fake data for offices.
    returns:
        offices: a list of Office objects
    """
    offices = []
    for _ in range(num_of_offices):
        address = fake.address()
        tokens = address.split(' ')
        office = Office(phone=fake.numerify('###-###-####'), email=f"{tokens[1].lower()}@company.com", address=address)
        offices.append(office)
    return offices

# Populate the agent_office_association table
def populate_agent_office_association(session):
    """
    Populates the association table between agents and offices.

    This function takes all agents and all offices from the database and randomly creates connections between them.

    params:
        session: the database session
    returns:
        None
    """
    for agent in session.query(Agent).all():
        for office in session.query(Office).all():
            if fake.pybool():
                agent.offices.append(office)

# Generate fake data for buyers
def generate_buyers():
    """
    Generates fake data for buyers.
    returns:
        buyers: a list of Buyer objects
    """
    buyers = []
    for _ in range(num_of_buyers):
        first_name = fake.first_name()
        last_name = fake.last_name()

        buyer = Buyer(name=generate_name(first_name, last_name), phone=fake.numerify('###-###-####'), 
                      email=generate_email(first_name, last_name))
        buyers.append(buyer)
    return buyers

# Generate fake data for sellers
def generate_sellers():
    """
    Generates fake data for sellers.
    returns:
        sellers: a list of Seller objects
    """
    sellers = []
    for _ in range(num_of_sellers):
        first_name = fake.first_name()
        last_name = fake.last_name()

        seller = Seller(name=generate_name(first_name, last_name), phone=fake.numerify('###-###-####'), 
                        email=generate_email(first_name, last_name))
        sellers.append(seller)
    return sellers

# Generate fake data for houses
def generate_houses(session):
    """
    Generate fake data for houses.
    The seller, agent, and office need to exist in the database so that the data is consistent.
    params:
        session: the database session
    returns:
        houses: a list of House objects
    """
    houses = []
    
    for _ in range(num_of_houses):
        # generate random seller_id, agent_id, and office_id that exist in the database
        seller_ids = [seller.id for seller in session.query(Seller).all()]
        seller_id = random.choice(seller_ids)
        
        agent_ids = [agent.id for agent in session.query(Agent).all()]
        agent_id = random.choice(agent_ids)

        office_ids = [office.id for office in session.query(Office).all()]
        office_id = random.choice(office_ids)

        house = House(num_bedrooms=fake.pyint(min_value=1, max_value=5), num_bathrooms=fake.pyint(min_value=1, max_value=5), 
                      listing_price=fake.pyint(min_value=30000, max_value=2000000), zip_code=fake.zipcode(), 
                      date_of_listing=generate_date(), status='Not Sold', seller_id=seller_id, 
                      agent_id=agent_id, office_id=office_id)
        
        houses.append(house)
    return houses

# Generate fake data for sales
def generate_sales(session):
    """
    Generate fake data for sales.
    A house can't be sold more than once, so we have to take that into account when generating the data.
    Also, when a house is sold, we need to update the status of the house to 'Sold'.
    And when a seller sales a house, we need to add that to his/her list of sold houses.
    And when a buyer buys a house, we need to add that to his/her list of purchases.

    params:
        session: the database session
    returns:
        sales: a list of Sale objects
    """
    sales = []

    sold_houses = []
    for _ in range(num_of_sales):
        # generate a random house_id that hasn't been sold yet and exists in the database
        house_ids = [house.id for house in session.query(House).all()]
        house_id = random.choice(house_ids)

        while house_id in sold_houses:  # make sure the house hasn't been sold already
            house_id = random.choice(house_ids)
        sold_houses.append(house_id)

        # generate a random buyer_id and agent_id that exist in the database
        buyer_ids = [buyer.id for buyer in session.query(Buyer).all()]
        buyer_id = random.choice(buyer_ids)

        # we can get the agent_id and the seller_id from the house object
        house = session.query(House).filter_by(id=house_id).first()  # get the house object that was sold from the database
        agent_id = house.agent_id
        seller_id = house.seller_id
        office_id = house.office_id


        # sale price could be less than the listing price by a random amount. this is always less than 20%.
        negotiated_discount_percentage = random.randint(0, 20)
        sale_price = (1-negotiated_discount_percentage/100) * house.listing_price

        sale = Sale(house_id=house_id, buyer_id=buyer_id, seller_id=seller_id, agent_id=agent_id, office_id=office_id, date_of_sale=generate_date(house.date_of_listing), 
                    sale_price=sale_price)
        
        house.status = 'Sold'  # update the status of the house to 'Sold'

        # updates the houses of the buyer
        buyer = session.query(Buyer).filter_by(id=buyer_id).first()
        buyer.houses.append(house)

        # updates the sold houses of the seller
        seller = session.query(Seller).filter_by(id=house.seller_id).first()
        seller.houses.append(house)
        
        sales.append(sale)
    return sales

# Insert fake data into the database
def insert_data(engine = create_engine('sqlite:///real_estate.db')):
    """
    Inserts fake data into the database.
    """
    agents = generate_agents()
    offices = generate_offices()
    buyers = generate_buyers()
    sellers = generate_sellers()
    

    Session = sessionmaker(bind=engine)
    session = Session()

    session.add_all(agents)
    session.add_all(offices)
    session.add_all(buyers)
    session.add_all(sellers)

    # We generate the houses and sales after the agents, offices, buyers, and sellers have been added to the database
    # because the house needs to have a seller_id, agent_id, and office_id that exist in the database and the sale
    # needs to have a buyer_id and house_id that exist in the database.
    houses = generate_houses(session)
    session.add_all(houses)

    sales = generate_sales(session)
    session.add_all(sales)

    populate_agent_office_association(session)

    session.commit()


if __name__ == '__main__':
    insert_data()