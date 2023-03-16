import os
import pandas as pd
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

def cypher_query_read(query: str, driver: object, query_name: str):
    '''
        Opens a session using Neo4j driver and executes a read transaction. Parses the query response and 
        formats into DataFrame in order to export to output CSV.

            Parameters:
                query (str): Cypher query formatted as string
                driver (obj): Neo4j Driver object
                query_name (str): desired name of query used for prints and output file names

            Returns:
                response (obj): query response as list
    '''
    try:
        # initialize neo4j session
        with driver.session(database=DB_NAME) as session:
            response = list(session.run(query))
            # parse query response and format into DataFrame for output
            output = pd.DataFrame([dict(obj) for obj in response])
            output.to_csv('./PartB_output/PartB_{}.csv'.format(query_name), index=False, sep=';')
        # print message if transaction successful and return query esponse
        print('{} Transaction Completed Succesfully!'.format(query_name))
        return response
    except Exception as e: # error handling
        print("{} failed: ".format(query_name), e)


def main():
    '''
    Orchestrates main functionality of script. Initializes Neo4j driver and runs Cypher queries 
    as read transactions using custom function.
    '''
    # initialize neo4j driver
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # run Query_1 read transaction
        cypher_query_read(query_1, driver, query_name='Query1')

        # run Query_2 read transaction
        cypher_query_read(query_2, driver, query_name='Query2')

        # run Query_3 read transaction
        cypher_query_read(query_3, driver, query_name='Query3')

        # run Query_4 read transaction
        cypher_query_read(query_4, driver, query_name='Query4')


# B.1 - Find the top 3 most cited papers of each conference
query_1 = '''
    MATCH (p2:Paper)<-[:CitedBy]-(p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c:Conference)
    WITH c.Conference as conference, p1.Title as paper, count(*) as citations
    ORDER BY conference, citations DESC
    WITH conference, collect([paper, citations]) as Papers
    RETURN conference as conference_name,
    Papers[0][0] as Paper1, Papers[0][1] as Total_Citations_Paper1,
    Papers[1][0] as Paper2, Papers[1][1] as Total_Citations_Paper2,
    Papers[2][0] as Paper3, Papers[2][1] as Total_Citations_Paper3;
'''

# B.2 - For each conference find its community: i.e., those authors that have published papers on that conference in, at least, 4 different editions.
query_2 = ''' 
    MATCH (author:Person)<-[:WritenBy]-(p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c:Conference)
    WITH c.Conference as conference, author.Name as author, count(distinct e1.Edition) as publications
    ORDER BY conference, publications DESC
    WHERE publications > 0
    WITH conference, collect([author]) as community_authors
    RETURN conference as conference_name, community_authors;
'''
    
# B.3 - Find the impact factors of the journals in your graph
query_3 = '''
    MATCH (j:Journal)
    CALL{
        with j
        MATCH (p2:Paper)-[:CitedBy]->(p1:Paper)-[:PublishedOn]->(v:Volume{Year: '2022'})-[:PartOf]->(j)
        WHERE EXISTS {
        MATCH(j)<-[:PartOf]-(v1:Volume)<-[:PublishedOn]-(p2)
        WHERE v1.Year IN ["2021","2020"]}
        REturn j.Journal as journal_name, p2.ID as paper2_id
    }
    CALL{
        with j
        MATCH(j)<-[:PartOf]-(v:Volume)<-[:PublishedOn]-(p1:Paper)
        WHERE v.Year IN ["2021","2020"]
        WITH j.Journal as journal_name, p1.Title as paper, count(*) as num_publications
        WITH sum(num_publications) AS total_num_publications
        where total_num_publications > 0
        return total_num_publications
    }
    with journal_name, count(paper2_id) as citations_2020_2021, total_num_publications as total_publications_2022
    return journal_name, citations_2020_2021, total_publications_2022, round( (1.0*citations_2020_2021) / (total_publications_2022), 2) as impact_factor;
'''

# B.4 - Find the h-indexes of the authors in your graph
query_4 = '''
    MATCH (pe:Person)<-[:WritenBy]-(p1:Paper)-[:CitedBy]->(p2:Paper)
    WITH pe.Name as author_name, p1.Title as Title, count(*) as NumCites 
    ORDER BY NumCites desc
    WITH author_name, collect(NumCites) as list_NumCites
    WITH author_name, [ x IN range(1,size(list_NumCites)) where x <= list_NumCites[x-1] | [list_NumCites[x-1],x] ] as list_hindex
    RETURN author_name, list_hindex[-1][1] as h_index
    ORDER BY h_index desc;
'''


if __name__=="__main__":
    main()