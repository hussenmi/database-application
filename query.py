from create import Sale, House, Agent, Office, MonthlyCommission
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker
from collections import defaultdict

engine = create_engine('sqlite:///real_estate.db')
Session = sessionmaker(bind=engine)
session = Session()


def get_top_five_offices(month, year):
    """
    Get the top five offices with the most sales for the month number.
    It orders it by the number of sales, not by the revenue generated. But the revenue is also printed for the top five offices.

    params month: The month number to get the top five offices for: str
           year: The year to get the top five offices for: str
    return: None
    """
    if month not in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        raise ValueError("The month number must be a string of two digits between '01' and '12'.")
    
    # take the month and year into account
    result = session.query(Sale.office_id, func.count(Sale.id).label('total_num_sales'), func.sum(Sale.sale_price).label(
        'total_revenue')).filter(func.strftime("%m", Sale.date_of_sale) == month).filter(
        func.strftime("%Y", Sale.date_of_sale) == year).group_by(
        Sale.office_id).order_by(desc('total_num_sales')).limit(5).all()
    
    for i, res in enumerate(result):
        # get the office object
        office = session.query(Office).filter(Office.id == res.office_id).first()
        # print the office id, number of houses sold, and revenue generated
        print(f"{i+1}. Office {office.id} has sold {res.total_num_sales} houses in {month}, {year} and generated ${round(res.total_revenue, 2)} in revenue.")

    

def get_top_five_agents(month, year):
    """
    Get the top five agents with the most sales for the month number.
    It orders it by the number of sales, not by the revenue generated. But the revenue is also printed for the top five agents.

    params month: The month number to get the top five agents for: str
           year: The year to get the top five agents for: str
    return: None
    """
    if month not in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        raise ValueError("The month number must be a string of two digits between '01' and '12'.")
    
    # get top five agents for the given month number and year
    result = session.query(Sale.agent_id, func.count(Sale.id).label('total_num_sales'), func.sum(Sale.sale_price).label(
        'total_revenue')).filter(func.strftime("%m", Sale.date_of_sale) == month).filter(
        func.strftime("%Y", Sale.date_of_sale) == year).group_by(
        Sale.agent_id).order_by(desc('total_num_sales')).limit(5).all()

    
    for i, res in enumerate(result):
        # get the agent object
        agent = session.query(Agent).filter(Agent.id == res.agent_id).first()
        # print the agent id, number of houses sold, and revenue generated
        print(f"{i+1}. {agent.name} ({agent.email}), Houses sold: {res.total_num_sales}, Revenue generated: ${round(res.total_revenue, 2)} in {month}, {year}.")
        

# Calculate the commission that each estate agent must receive and store the results in a separate table.
def get_commision_for_each_agent(month, year):
    """
    Get the commission for each agent for the month number.

    params month: The month number to get the commission for each agent for: str
           year: The year to get the commission for each agent for: str
    return: None
    """
    if month not in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        raise ValueError("The month number must be a string of two digits between '01' and '12'.")
    
    # get the sales for the given month number and year
    result = session.query(Sale).filter(func.strftime("%m", Sale.date_of_sale) == month).filter(
        func.strftime("%Y", Sale.date_of_sale) == year).all()
    
    agents = defaultdict(int)
    for sale in result:
        agents[sale.agent_id] += sale.agent_commission

    # print and store the results in a separate table
    for agent_id, total_commission in agents.items():
        monthly_commission = MonthlyCommission(agent_id=agent_id, month=int(month), year=int(year), total_commission=total_commission)
        session.add(monthly_commission)
        session.commit()

        print(f"Agent {agent_id} has earned ${round(total_commission, 2)} in commission for {month}, {year}.")

# For all houses that were sold that month, calculate the average number of days on the market.
def average_number_of_days(month, year):
    """
    Get the average number of days on the market for all houses that were sold that month.

    params month: The month number to get the average number of days on the market for: str
           year: The year to get the average number of days on the market for: str
    return: None
    """
    if month not in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        raise ValueError("The month number must be a string of two digits between '01' and '12'.")
    
    # get the sales for the given month number and year
    result = session.query(Sale).filter(func.strftime("%m", Sale.date_of_sale) == month).filter(
        func.strftime("%Y", Sale.date_of_sale) == year).all()
    
    total_days = 0
    for sale in result:
        # get the house object
        house = session.query(House).filter(House.id == sale.house_id).first()
        # get the number of days on the market by taking the difference between the date of listing and the date of sale
        number_of_days_on_market = sale.date_of_sale - house.date_of_listing
        total_days += number_of_days_on_market.days
    
    # print the average number of days on the market
    print(f"Average number of days on the market for {month}, {year} is {round(total_days / len(result), 2)} days.")

# For all houses that were sold that month, calculate the average selling price
def average_selling_price(month, year):
    """
    Get the average selling price for all houses that were sold that month.

    params month: The month number to get the average selling price for: str
           year: The year to get the average selling price for: str
    return: None
    """
    if month not in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        raise ValueError("The month number must be a string of two digits between '01' and '12'.")
    
    query = session.query(func.avg(Sale.sale_price)).filter(func.strftime("%m", Sale.date_of_sale) == month).filter(
        func.strftime("%Y", Sale.date_of_sale) == year).all()
    
    # get the average selling price from the query
    average_price = query[0][0]

    
    # print the average selling price
    print(f"Average selling price for {month}, {year} is ${round(average_price, 2)}.")

if __name__ == '__main__':
    get_top_five_offices('01', '2023')
    print('\n')
    get_top_five_agents('01', '2023')
    print('\n')
    get_commision_for_each_agent('01', '2023')
    print('\n')
    average_number_of_days('01', '2023')
    print('\n')
    average_selling_price('01', '2023')