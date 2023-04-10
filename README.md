The database I designed has 8 tables. Six of them are fully normalized and are in 3rd normal form. There is one table that is used to create a many-to-many relationship between offices and agents. The other one is created after one of the queries and is denormalized. It contains the commission that each agent must receive. For the queries, I also added an index on the `date_of_sale` and `sale_price` columns of the `Sale` table. This significantly improved the speed of the queries. I chose these columns to create an index because they are what we mostly use in our queries. There is a trade-off when creating indexes that inserting and updating will be slower, but that trade-off was worth it in my case. I tried the insertion using the fake data from `insert.py` using both with and without an index, and the speed wasn't very different. But for the queries, the speed was much different when I used the indexes vs without them.

I have written all of my code without using a single raw SQL; all of it is written in Python and SQLAlchemy. By using this, I achieve a really good layer of abstraction, especially when creating object attributes in connected tables by using `relationship` and the `backref` functionalities. For example, there is a many-to-many relationship between agents and offices, and when I created the tables, I used an association table to have the foreign keys for both the individual tables. I created an `offices` attribute for an `agent` object and `backref` would create an `agents` attribute for an office object. These attributes abstract the joins that we would have needed to make if we used raw SQL code. This is an example and there are a lot more of these in the `create.py` file.

In the `insert.py` file, I use the `faker` library to create and insert fake data into all of our tables. The code also takes into account all the dependencies that need to be met. For example, when creating a `sale` object for a house, it first needs to query a house, a seller, an agent, and an office, and they need to already exist in the database. This and other unit tests for properly populating the database are found in the `test_db.py` file.


Here is how to run the application after creating the virtual environment:

```
pip install -r requirements.txt
python create.py
python insert.py
python query.py
python test_db.py

```