from neo4j import GraphDatabase
from cypher_queries import *
from ..src.neo4j_conn import Neo4jConnection

# Neo4j Docker Credentials
URI="neo4j://localhost:7687"
AUTH = ("neo4j", "password")


def main():
    '''
    
    '''
    # 
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        



if __name__=="__main__":
    main()