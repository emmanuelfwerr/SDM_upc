import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from cypher_queries import *


# Load secrets from .env
load_dotenv()

# instantiate neo4j credentials
URI = os.environ['NEO4J_URI']
AUTH = (os.environ['NEO4J_USERNAME'], os.environ['NEO4J_PASSWORD'])
DB_NAME = os.environ['DB_NAME']


def main():
    '''
    
    '''
    # 
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session(database=DB_NAME) as session:



if __name__=="__main__":
    main()