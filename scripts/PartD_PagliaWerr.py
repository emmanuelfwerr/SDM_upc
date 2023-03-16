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
        return response
    except Exception as e: # error handling
        print(f'{query_name} failed: ', e)


def main():
    '''
        Orchestrates main functionality of script. Initializes Neo4j driver and runs Cypher queries 
        as read/write transactions using custom function.
    '''
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # --*-- D.1 - Page Rank --*--
        run_cypher(drop_PageRank_Graph, driver, query_name='drop_PageRank_Graph', suppress_output=True) # drop GDS subgraph if already exists
        run_cypher(init_PageRank_Graph, driver, query_name='init_PageRank_Graph', suppress_output=True) # init GDS subgraph for PageRank
        run_cypher(GDS_PageRank, driver, query_name='GDS_PageRank') # call GDS PageRank Algorithm in stream mode

        #  --*-- D.2 - Louvain --*--
        run_cypher(drop_Louvain_Graph, driver, query_name='drop_Louvain_Graph', suppress_output=True) # drop GDS subgraph if already exists
        run_cypher(init_Louvain_Graph, driver, query_name='init_Louvain_Graph', suppress_output=True) # init GDS subgraph for Louvain
        run_cypher(GDS_Louvain, driver, query_name='GDS_Louvain') # call GDS Louvain Community Detection Algorithm in stream mode
        run_cypher(Louvain_communityCount, driver, query_name='Louvain_communityCount') # call GDS Louvain stats mode for communityCount


# --*-- D.1 - Page Rank --*--
# ---------------------------

# drop sub-graph for PageRank if already exists
drop_PageRank_Graph = '''
    CALL gds.graph.drop('PartD_PageRank', False)
'''

# initialize sub-graph for PageRank
init_PageRank_Graph = '''
    CALL gds.graph.project('PartD_PageRank', 'Paper', 'CitedBy');
'''

# stream mode PageRank
GDS_PageRank = '''
    CALL gds.pageRank.stream('PartD_PageRank', {maxIterations: 50, dampingFactor: 0.85}) 
    YIELD nodeId, score
    RETURN nodeId as paper_id, gds.util.asNode(nodeId).Title AS paper_name, round(score, 2) as page_rank
    ORDER BY score DESC LIMIT 10;
'''

# --*-- D.2 - Louvain Community Detection --*--
# ---------------------------------------------

# drop sub-graph for Louvain if already exists
drop_Louvain_Graph = '''
    CALL gds.graph.drop('PartD_Louvain', False)
'''
# initialize sub-graph for Louvain Community Detection
init_Louvain_Graph = '''
    CALL gds.graph.project('PartD_Louvain', 'Paper', 'CitedBy');
'''

# stream mode Louvain Community Detection
GDS_Louvain = '''
    CALL gds.louvain.stream('PartD_Louvain')
    YIELD nodeId, communityId, intermediateCommunityIds
    RETURN nodeId as paper_id, gds.util.asNode(nodeId).Title AS paper_name, communityId
    ORDER BY paper_id ASC
'''

# stats mode Louvain communityCount
Louvain_communityCount = '''
    CALL gds.louvain.stats('PartD_Louvain')
    YIELD communityCount
'''

# ----------------------------------------------
# ----------------------------------------------


if __name__=="__main__":
    main()
