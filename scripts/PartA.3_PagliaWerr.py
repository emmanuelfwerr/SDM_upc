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

def cypher_query_write(query: str, driver: object):
    '''
        Opens a session using Neo4j driver and executes a write transaction.

            Parameters:
                query (str): Cypher query formatted as string
                driver (obj): Neo4j Driver object

            Returns:
                response (obj): query response as list
    '''
    try:
        # initialize neo4j session
        with driver.session(database=DB_NAME) as session:
            response = list(session.run(query))
        # print message if transaction successful and return query esponse
        print('Transaction Completed Succesfully!')
        return response
    except Exception as e: # error handling
        print("Query failed: ", e)


def main():
    '''
    Orchestrates main functionality of script. Initializes Neo4j driver and runs Cypher queries 
    as read transactions using custom function.
    '''
    # initialize neo4j driver
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # run query transactions to create all nodes
        for query in cypher_extend_nodes:
            cypher_query_write(query, driver)

        # run query transactions to create all relationships
        for query in cypher_extend_relations:
            cypher_query_write(query, driver)


# A.3 - extend graph nodes from CSV
cypher_extend_nodes = [
    ''' LOAD CSV with headers FROM 'file:///companies.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Company {ID: row.company_id, Name: row.company_name});''',

    ''' LOAD CSV with headers FROM 'file:///universities.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:University {ID: row.university_id, Name: row.university_name});'''
]

# A.3 - extend graph edges from CSV
cypher_extend_relations = [
    ''' LOAD CSV WITH HEADERS FROM "file:///person_TO_company.csv" AS row FIELDTERMINATOR ';' 
        MERGE (person:Person {ID: row.author_id})
        MERGE (company:Company {ID: row.company_id})
        MERGE (person)-[:Affiliation]->(company);''',

    ''' LOAD CSV WITH HEADERS FROM "file:///person_TO_university.csv" AS row FIELDTERMINATOR ';' 
        MERGE (person:Person {ID: row.author_id})
        MERGE (university:University {ID: row.university_id})
        MERGE (person)-[:Affiliation]->(university);''',

    ''' LOAD CSV WITH HEADERS FROM "file:///paper_TO_reviewer.csv" AS row FIELDTERMINATOR ';' 
        MATCH (Paper {ID: row.paper_id})-[review:ReviewedBy]->(Person {ID: row.reviewer_id})
        SET review.text = row.text, review.decision = row.decision;'''
]


if __name__=="__main__":
    main()