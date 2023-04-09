from sqlalchemy import Table, create_engine, Column, Integer, String, Float, Numeric, Date, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine('sqlite:///real_estate.db')
engine.connect() 


Base = declarative_base()



# Define a class to validate email addresses

from sqlalchemy.types import TypeDecorator, String
from validate_email import validate_email

class EmailType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not validate_email(value):
                raise ValueError('Invalid email address')
        return value


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

    # since one agent can have many houses, we need to add a foreign key. the same goes for an office
    agent_id = Column(Integer, ForeignKey('agent.id'))
    office_id = Column(Integer, ForeignKey('office.id'))

    def __repr__(self):
        return f"House('{self.id}', '{self.seller_name}', '{self.seller_email}')"
    
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
    name = Column(String)
    phone = Column(String)
    email = Column(EmailType)
    address = Column(String)

    # a one to many relationship between office and house
    houses = relationship('House', backref='office', lazy=True)

    def __repr__(self):
        return f"Office('{self.id}', '{self.name}', '{self.email}')"
    
class Buyer(Base):
    __tablename__ = 'buyer'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    email = Column(EmailType)

    # a one to many relationship between buyer and sale because a buyer could buy many houses
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

    def __repr__(self):
        return f"Seller('{self.name}', '{self.email}')"
    
class Sale(Base):
    __tablename__ = 'sale'
    id = Column(Integer, primary_key=True)
    house_id = Column(Integer, ForeignKey('house.id'))
    buyer_id = Column(Integer, ForeignKey('buyer.id'))
    agent_id = Column(Integer, ForeignKey('agent.id'))
    date_of_sale = Column(Date)
    sale_price = Column(Numeric)


    def get_agent_commision(self):
        if self.sale_price < 100000:
            return 0.1 * self.sale_price
        elif 100000 <= self.sale_price < 200000:
            return 0.075 * self.sale_price
        elif 200000 <= self.sale_price < 500000:
            return 0.06 * self.sale_price
        elif 500000 <= self.sale_price < 1000000:
            return 0.05 * self.sale_price
        else:
            return 0.04 * self.sale_price
        

    def __repr__(self):
        return f"Sale('{self.id}', '{self.house_id}', '{self.buyer_id}', '{self.agent_id}')"
    

if __name__ == '__main__':
    Base.metadata.create_all(engine)  # this creates the tables in the database