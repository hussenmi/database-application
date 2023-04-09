from sqlalchemy import Table, create_engine, Column, Integer, String, Float, Numeric, Date, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

engine = create_engine('sqlite:///real_estate.db')
engine.connect() 


Base = declarative_base()


# Define the classes for the tables

class House(Base):
    __tablename__ = 'house'
    id = Column(Integer, primary_key=True)
    num_bedrooms = Column(Integer)
    num_bathrooms = Column(Integer)
    listing_price = Column(Numeric)
    zip_code = Column(String)
    date_of_listing = Column(Date)
    status = Column(Enum('Not Sold', 'Sold', name='status'))

    seller_id = Column(Integer, ForeignKey('seller.id'))  # a foreign key to the seller table
    buyer_id = Column(Integer, ForeignKey('buyer.id'))  # a foreign key to the buyer table

    # since one agent can have many houses, we need to add a foreign key. the same goes for an office
    agent_id = Column(Integer, ForeignKey('agent.id'))
    office_id = Column(Integer, ForeignKey('office.id'))

    def __repr__(self):
        return f"House('{self.id}', '{self.listing_price}', '{self.status}')"
    
# Define the association table for the many-to-many relationship between agents and offices
agent_office_association = Table('agent_office_association', Base.metadata, 
                          Column('agent_id', Integer, ForeignKey('agent.id')), 
                          Column('office_id', Integer, ForeignKey('office.id')))

    
class Agent(Base):
    __tablename__ = 'agent'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    email = Column(EmailType)

    # a one to many relationship between agent and house
    houses = relationship('House', backref='agent', lazy=True)

    # a one to many relationship between agent and sale
    sales = relationship('Sale', backref='agent', lazy=True)

    # since one office can have many agents and one agent can be apart of many offices, we need to add a many to many relationship
    offices = relationship('Office', secondary=agent_office_association, backref='agents', lazy=True)

    
    def __repr__(self):
        return f"Agent('{self.name}', '{self.email}')"
    
class Office(Base):
    __tablename__ = 'office'
    id = Column(Integer, primary_key=True)
    phone = Column(String)
    email = Column(EmailType)
    address = Column(String)

    # a one to many relationship between office and house
    houses = relationship('House', backref='office', lazy=True)

    # a one to many relationship between office and sale
    sales = relationship('Sale', backref='office', lazy=True)

    def __repr__(self):
        return f"Office('{self.id}', '{self.email}')"
    
class Buyer(Base):
    __tablename__ = 'buyer'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    email = Column(EmailType)

    # a one to many relationship between buyer and house because a buyer could buy many houses
    houses = relationship('House', backref='buyer', lazy=True)

    # a one to many relationship between buyer and sale because a buyer could make many purchases
    purchases = relationship('Sale', backref='buyer', lazy=True)


    def __repr__(self):
        return f"Buyer('{self.name}', '{self.email}')"
    
class Seller(Base):
    __tablename__ = 'seller'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    email = Column(EmailType)

    # a one to many relationship between seller and house because a seller could sell many houses
    houses = relationship('House', backref='seller', lazy=True)

    # a one to many relationship between seller and sale because a seller could sell many houses
    sales = relationship('Sale', backref='seller', lazy=True)

    def __repr__(self):
        return f"Seller('{self.name}', '{self.email}')"
    
class Sale(Base):
    __tablename__ = 'sale'
    id = Column(Integer, primary_key=True)
    house_id = Column(Integer, ForeignKey('house.id'))
    seller_id = Column(Integer, ForeignKey('seller.id'))
    buyer_id = Column(Integer, ForeignKey('buyer.id'))
    agent_id = Column(Integer, ForeignKey('agent.id'))
    office_id = Column(Integer, ForeignKey('office.id'))
    date_of_sale = Column(Date)
    sale_price = Column(Numeric)


    @property
    def agent_commission(self):
        """
        Returns the agent's commision based on the sale price
        Using the @property decorator allows us to call this method like an attribute and generate the commission dynamically
        """
        if self.sale_price < 100000:
            return 0.1 * float(self.sale_price)
        elif self.sale_price < 200000:
            return 0.075 * float(self.sale_price)
        elif self.sale_price < 500000:
            return 0.06 * float(self.sale_price)
        elif self.sale_price < 1000000:
            return 0.05 * float(self.sale_price)
        else:
            return 0.04 * float(self.sale_price)
        

    def __repr__(self):
        return f"Sale('{self.id}', '{self.house_id}', '{self.buyer_id}', '{self.agent_id}', '{self.sale_price}', '{self.date_of_sale}')"
    

class MonthlyCommission(Base):
    __tablename__ = 'monthly_sales'
    id = Column(Integer, primary_key=True)
    month = Column(Integer)
    year = Column(Integer)
    agent_id = Column(Integer, ForeignKey('agent.id'))
    total_commission = Column(Numeric)

    def __repr__(self):
        return f"MonthlyCommission('{self.month}', '{self.agent_id}', '{self.total_commission}')"
    

if __name__ == '__main__':
    Base.metadata.create_all(engine)  # this creates the tables in the database