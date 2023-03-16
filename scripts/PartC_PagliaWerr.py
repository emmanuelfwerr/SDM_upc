import pandas as pd
from neo4j import GraphDatabase


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
            print(output)
        # print message if transaction successful and return query esponse
        print('{} Transaction Completed Succesfully!'.format(query_name))
        return response
    except Exception as e: # error handling
        print("{} failed: ".format(query_name), e)


def main():
    '''
    '''
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        #
        # cypher_query_read(query_string_create_community, driver, query_name='test')
        # #
        # cypher_query_read(query_string_match_community, driver, query_name='test')
        # #
        # cypher_query_read(query_string_conference, driver, query_name='test')
        # #
        # cypher_query_read(query_string_journal, driver, query_name='test')
        #
        cypher_query_read(query_string_top_papers, driver, query_name='test')


# ------------------------------------------------------------------------------------- 1
query_string_create_community = '''
   create (c:Community {name:'CommunityDB'});
   '''

query_string_match_community = '''
   match (c:Community {name:'CommunityDB'})
   match (kw:Keyword)
   where kw.Keyword in ['data management', 'indexing', 'data modeling', 'big data', 'data processing', 'data storage' , 'data querying']
   merge (kw)-[:RelatedTo]->(c);
   '''

# ------------------------------------------------------------------------------------- 2

# Conference
query_string_conference = '''
MATCH (c:Conference)
CALL{
    with c
    match (p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c)
    with c, c.Conference as conference, count(*) as num_papers
    Return num_papers}
 
MATCH (c)<-[:PartOf]-(e1:Edition)<-[:PublishedOn]-(p1:Paper)-[:HasKeyword]->(kw:Keyword)-[:RelatedTo]->(co:Community)
with c, co, c.Conference as conference, num_papers, count(distinct p1.ID) as num_papers_CommunityDB
with c, co, conference, num_papers, num_papers_CommunityDB, (1.0*num_papers_CommunityDB/num_papers) as percentage
where percentage >=0.01
merge (c)-[:RelatedTo]->(co)
return conference, num_papers, num_papers_CommunityDB, round(percentage,2) as percentage_CommunityDB;'''


#############################################

# Journal
query_string_journal = '''
MATCH (j:Journal)
CALL{
    with j
    match (p1:Paper)-[:PublishedOn]->(v1:Volume)-[:PartOf]->(j)
    with j, j.Journal as journal, count(*) as num_papers
    Return num_papers}
 
MATCH (j)<-[:PartOf]-(v1:Volume)<-[:PublishedOn]-(p1:Paper)-[:HasKeyword]->(kw:Keyword)-[:RelatedTo]->(co:Community)
with j, co, j.Journal as journal, num_papers, count(distinct p1.ID) as num_papers_CommunityDB
with j, co, journal, num_papers, num_papers_CommunityDB, (1.0*num_papers_CommunityDB/num_papers) as percentage
where percentage >=0.01
merge (j)-[:RelatedTo]->(co)
return journal, num_papers, num_papers_CommunityDB, round(percentage,2) as percentage_CommunityDB;'''

# ------------------------------------------------------------------------------------- 3
query_string_top_papers = '''
CALL gds.pageRank.stream(
{nodeQuery: 'match (p:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c1)-[:relatedTo]->(commu:community) where commu.name="CommunityDB" return id(p) as id',
relationshipQuery: 'match (commu1:community)<-[:relatedTo]-(c1)<-[:PartOf]-(e1:Edition)<-[:PublishedOn]-(p1:Paper)-[:CitedBy]->(p2:Paper)-[:PublishedOn]->(e2:Edition)-[:PartOf]->(c2)-[:relatedTo]->(commu2:community) where commu1.name="CommunityDB" and commu2.name="CommunityDB" return id(p1) as source, id(p2) as target'})
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS a, score
ORDER BY score DESC
match (commu:community {name:'CommunityDB'})
merge (a)-[:relatedTo]->(commu)
return a.Title, score
ORDER BY score DESC
limit 10;'''

if __name__=="__main__":
    main()



