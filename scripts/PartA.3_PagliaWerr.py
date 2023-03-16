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

def cypher_query_write(query, driver):
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
        CREATE (:University {ID: row.university_id, Name: row.university_name});''',

    ''' NOT DONE *** LOAD CSV with headers FROM 'file:///paper_TO_reviewer.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Review {ID: row.review_id, Decision: row.decision, Review: row.text});'''
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

    ''' NOT DONE *** LOAD CSV WITH HEADERS FROM "file:///paper_TO_reviewer.csv" AS row FIELDTERMINATOR ';' 
        MERGE (review:Review {ID: row.review_id})
        MERGE (person:Person {ID: row.author_id})
        MERGE (review)-[:ReviewWritenBy]->(person);'''
]


if __name__=="__main__":
    main()