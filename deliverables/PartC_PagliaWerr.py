import pandas as pd
from neo4j import GraphDatabase


# instantiate neo4j credentials
URI = 'neo4j://localhost:7687'
AUTH = ('neo4j', 'password')
DB_NAME = 'neo4j'

def run_cypher(query: str, driver: object, query_name: str='ad-hoc', suppress_output: bool=False):
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
    # prettify terminal output
    if suppress_output == False:
        print('\n' + 15*'-' + f' Running {query_name} Cypher ' + 15*'-' + '\n')

    # neo4j transaction commit error handling
    try:
        # initialize neo4j session
        with driver.session(database=DB_NAME) as session:
            response = list(session.run(query))
            # parse query response and format into DataFrame for output
            output = pd.DataFrame([dict(obj) for obj in response])
            # print response to terminal 
            if suppress_output == False:
                print(output)
        # print message if transaction successful and return query response
        print(f'\n{query_name} Transaction Completed Succesfully!')
    except Exception as e: # error handling
        print(f'{query_name} failed: ', e)


def main():
    '''
        Orchestrates main functionality of script. Initializes Neo4j driver and runs Cypher queries 
        as read transactions using custom function.
    '''
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # Delete CommunityDB node if exists
        run_cypher(Delete_CommunityDB, driver, query_name='Delete_CommunityDB', suppress_output=True)
        # Create CommunityDB node
        run_cypher(Create_CommunityDB, driver, query_name='Create_CommunityDB', suppress_output=True)
        # Set Keywords RelatedTo CommunityDB
        run_cypher(Match_Keyword_CommunityDB, driver, query_name='Match_Keyword_CommunityDB', suppress_output=True)
        # Get Papers RelatedTo CommunityDB via Conferences according to threshold
        run_cypher(Match_Conference_CommunityDB, driver, query_name='Match_Conference_CommunityDB')
        # Get Papers RelatedTo CommunityDB via Journals according to threshold
        run_cypher(Match_Journal_CommunityDB, driver, query_name='Match_Journal_CommunityDB')

        # --*-- Top 100 Papers within CommunityDB Conferences --*--
        run_cypher(drop_ConfPapers_CommunityDB, driver, query_name='drop_ConfPapers_CommunityDB', suppress_output=True)
        run_cypher(init_ConfPapers_CommunityDB, driver, query_name='init_ConfPapers_CommunityDB', suppress_output=True)
        run_cypher(Top_ConfPapers_CommunityDB, driver, query_name='Top_ConfPapers_CommunityDB')

        # --*-- Top 100 Papers within CommunityDB Journals --*--
        run_cypher(drop_JournPapers_CommunityDB, driver, query_name='drop_JournPapers_CommunityDB', suppress_output=True)
        run_cypher(init_JournPapers_CommunityDB, driver, query_name='init_JournPapers_CommunityDB', suppress_output=True)
        run_cypher(Top_JournPapers_CommunityDB, driver, query_name='Top_JournPapers_CommunityDB')

# ------------------------------------------------------------------------------------- 1
Delete_CommunityDB = '''
    MATCH (cdb:Community {name: 'CommunityDB'})
    DETACH DELETE cdb
'''

Create_CommunityDB = '''
   CREATE (cdb:Community {name:'CommunityDB'});
'''

Match_Keyword_CommunityDB = '''
   MATCH (cdb:Community {name:'CommunityDB'})
   MATCH (k:Keyword)
   WHERE k.Keyword in ['data management', 'indexing', 'data modeling', 'big data', 'data processing', 'data storage' , 'data querying']
   MERGE (k)-[:RelatedTo]->(cdb);
'''

# ------------------------------------------------------------------------------------- 2

# Conference
Match_Conference_CommunityDB = '''
    MATCH (c:Conference)
    CALL{
        WITH c
        MATCH (p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c)
        WITH c, c.Conference as conference_name, count(*) as total_papers
        RETURN total_papers}
    
    MATCH (c)<-[:PartOf]-(e1:Edition)<-[:PublishedOn]-(p1:Paper)-[:HasKeyword]->(k:Keyword)-[:RelatedTo]->(cdb:Community)
    WITH c, cdb, c.Conference as conference_name, total_papers, count(distinct p1.ID) as total_papers_CommunityDB
    WITH c, cdb, conference_name, total_papers, total_papers_CommunityDB, ( (1.0*total_papers_CommunityDB) / (total_papers) ) as threshold
    WHERE threshold >= 0.15
    merge (c)-[:RelatedTo]->(cdb)
    return conference_name, total_papers, total_papers_CommunityDB, round(threshold, 2) as percentage_CommunityDB;
'''


# #############################################

# Journal
Match_Journal_CommunityDB = '''
    MATCH (j:Journal)
    CALL{
        WITH j
        MATCH (p1:Paper)-[:PublishedOn]->(v1:Volume)-[:PartOf]->(j)
        WITH j, j.Journal as journal_name, count(*) as total_papers
        RETURN total_papers}
    
    MATCH (j)<-[:PartOf]-(v1:Volume)<-[:PublishedOn]-(p1:Paper)-[:HasKeyword]->(kw:Keyword)-[:RelatedTo]->(cdb:Community)
    WITH j, cdb, j.Journal as journal_name, total_papers, count(distinct p1.ID) as total_papers_CommunityDB
    WITH j, cdb, journal_name, total_papers, total_papers_CommunityDB, ( (1.0*total_papers_CommunityDB) / (total_papers) ) as threshold
    WHERE threshold >= 0.15
    MERGE (j)-[:RelatedTo]->(cdb)
    RETURN journal_name, total_papers, total_papers_CommunityDB, round(threshold, 2) as percentage_CommunityDB;
'''


# --*-- Papers within CommunityDB Conferences --*--
# -------------------------------------------------

# drop subgraph of conference papers in CommunityDB if already exists
drop_ConfPapers_CommunityDB = '''
    CALL gds.graph.drop('ConfPapers_CommunityDB', False)
'''

# create subgraph of conference papers in CommunityDB
init_ConfPapers_CommunityDB = '''
    CALL gds.graph.project.cypher(
        'ConfPapers_CommunityDB', 
        'MATCH (p:Paper) RETURN DISTINCT id(p) As id',
        'MATCH (cdb1:Community)<-[:RelatedTo]-(c1:Conference)<-[:PartOf]-(e1:Edition)<-[:PublishedOn]-(p1:Paper)-[:CitedBy]->(p2:Paper)-[:PublishedOn]->(e2:Edition)-[:PartOf]->(c2:Conference)-[:RelatedTo]->(cdb2:Community) WHERE cdb1.name="CommunityDB" and cdb2.name="CommunityDB" RETURN id(p1) as source, id(p2) as target'
    );
'''

Top_ConfPapers_CommunityDB = '''
    CALL gds.pageRank.stream('ConfPapers_CommunityDB', {maxIterations: 50, dampingFactor: 0.85})
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) as node, nodeId as paper_id, gds.util.asNode(nodeId).Title AS paper_name, score as page_rank
        MATCH (cdb:Community {name:'CommunityDB'})
        MERGE (node)-[:RelatedTo]->(cdb)
        RETURN paper_id, paper_name, page_rank
        ORDER BY page_rank DESC
        LIMIT 100;
'''

# --*-- Papers within CommunityDB Journals --*--
# ----------------------------------------------

# drop subgraph of conference papers in CommunityDB if already exists
drop_JournPapers_CommunityDB = '''
    CALL gds.graph.drop('JournPapers_CommunityDB', False)
'''

# create subgraph of conference papers in CommunityDB
init_JournPapers_CommunityDB = '''
    CALL gds.graph.project.cypher(
        'JournPapers_CommunityDB', 
        'MATCH (p:Paper) RETURN DISTINCT id(p) As id',
        'MATCH (cdb1:Community)<-[:RelatedTo]-(j1:Journal)<-[:PartOf]-(v1:Volume)<-[:PublishedOn]-(p1:Paper)-[:CitedBy]->(p2:Paper)-[:PublishedOn]->(v2:Volume)-[:PartOf]->(j2:Journal)-[:RelatedTo]->(cdb2:Community) WHERE cdb1.name="CommunityDB" and cdb2.name="CommunityDB" RETURN id(p1) as source, id(p2) as target'
    );
'''

Top_JournPapers_CommunityDB = '''
    CALL gds.pageRank.stream('JournPapers_CommunityDB', {maxIterations: 50, dampingFactor: 0.85})
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) as node, nodeId as paper_id, gds.util.asNode(nodeId).Title AS paper_name, score as page_rank
        MATCH (cdb:Community {name:'CommunityDB'})
        MERGE (node)-[:RelatedTo]->(cdb)
        RETURN paper_id, paper_name, page_rank
        ORDER BY page_rank DESC
        LIMIT 100;
'''


# --*-- Gurus within CommunityDB Conferences --*--
# ------------------------------------------------



# ----------------------------------------------
# ----------------------------------------------


if __name__=="__main__":
    main()