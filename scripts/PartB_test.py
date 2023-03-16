import os
from dotenv import load_dotenv
from neo4j import GraphDatabase


# Load secrets from .env
#load_dotenv(dotenv_path='./env/.env')

# instantiate neo4j credentials
#URI = os.environ['NEO4J_URI']
#AUTH = (os.environ['NEO4J_USERNAME'], os.environ['NEO4J_PASSWORD'])
#DB_NAME = os.environ['DB_NAME']

# instantiate neo4j credentials
URI = 'neo4j://localhost:7687'
AUTH = ('neo4j', 'password')
DB_NAME = 'neo4j'

def cypher_query_read(query, driver):
    '''

    '''
    try:
        with driver.session(database=DB_NAME) as session:
            response = list(session.run(query))
        print('Transaction Completed Succesfully!')
        return response
    except Exception as e:
        print("Query failed: ", e)


def main():
    '''
    
    '''
    # initialize neo4j driver
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # run query_1 read transaction
        cypher_query_read(query_1, driver)
        # run query_1 read transaction
        cypher_query_read(query_2, driver)
        # run query_1 read transaction
        cypher_query_read(query_3, driver)
        # run query_1 read transaction
        cypher_query_read(query_4, driver)


# B.1 - extend graph nodes from CSV
query_1 = [
    
]

# B.2 - extend graph edges from CSV
query_2 = [
    
]
    
# B.3 - extend graph nodes from CSV
query_3 = [
    
]

# B.4 - extend graph edges from CSV
query_4 = [
    
]


if __name__=="__main__":
    main()