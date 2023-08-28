import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# instantiate neo4j credentials
URI = os.getenv('AURADS_NEO4J_URI')
AUTH = (os.getenv('AURADS_NEO4J_USERNAME'), os.getenv('AURADS_NEO4J_PASSWORD'))
DB_NAME = os.getenv('AURADS_DB_NAME')

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
        # --*-- Descriptive Statistics --*--
        # run Query_1 read transaction
        run_cypher(query_1, driver, query_name='Node Statistics')
        # run Query_2 read transaction
        run_cypher(query_2, driver, query_name='Edge Statistics')
        # run Query_3 read transaction
        run_cypher(query_3, driver, query_name='Node/Edge Profiling')

        # --*-- GDS Projection --*--
        # drop moviesProjection if already exists
        run_cypher(drop_moviesProjection, driver, query_name='drop moviesProjection')
        # run gdsProjection read transaction
        run_cypher(gdsProjection, driver, query_name='gdsProjection')
        # check if moviesProjection exists
        run_cypher(check_exists, driver, query_name='check moviesProjection exists')

        # --*-- FastRP Embedding --*--
        # create FastRP embeddings
        #run_cypher(FastRP, driver, query_name='FastRP')

        # --*-- Node2Vec Embedding --*--
        # create Node2Vec embeddings
        run_cypher(Node2Vec, driver, query_name='Node2Vec')

        # --*-- kNN Similarity --*--
        # run kNN
        run_cypher(kNN_Similarity, driver, query_name='kNN_Similarity')
        


# --*-- Query1 - Get Node Statistics --*--
# ----------------------------------------
query_1 = '''
    CALL db.labels()
    YIELD label
    MATCH (n)
    WHERE label IN labels(n)
    RETURN label AS NodeType, count(*) AS Count
    ORDER BY Count DESC
'''

# --*-- Query2 - Get Edge Statistics --*--
# ----------------------------------------
query_2 = '''
    CALL db.relationshipTypes()
    YIELD relationshipType
    MATCH ()-[r]->()
    WHERE type(r) = relationshipType
    RETURN relationshipType AS RelationshipType, count(*) AS Count
    ORDER BY Count DESC
'''

# --*-- Query3 - Node/Edge Profiling --*--
# ---------------------------------------
query_3 = '''
    MATCH (n)
    RETURN
    DISTINCT labels(n),
    count(*) AS SampleSize,
    avg(size(keys(n))) as Avg_PropertyCount,
    min(size(keys(n))) as Min_PropertyCount,
    max(size(keys(n))) as Max_PropertyCount,
    avg(size( [ (n)-[]-() | n] ) ) as Avg_RelationshipCount,
    min(size( [ (n)-[]-() | n] ) ) as Min_RelationshipCount,
    max(size( [ (n)-[]-() | n] ) ) as Max_RelationshipCount
'''


# --*-- Graph Data Science Projection --*--
#
# drop moviesProjection if already exists
drop_moviesProjection = '''
    CALL gds.graph.drop('moviesProjection', False)
'''

# create moviesProjection 
gdsProjection = '''
    CALL gds.graph.project('moviesProjection',
        ['Movie', 'Actor', 'Director', 'Genre', 'User'],
        {
            ACTED_IN: {
            orientation: 'UNDIRECTED'
            },
            DIRECTED: {
            orientation: 'UNDIRECTED'
            },
            IN_GENRE: {
            orientation: 'UNDIRECTED'
            },
            RATED: {
            orientation: 'UNDIRECTED'
            }
        }
    )
'''

# check if moviesProjection exists
check_exists = '''
    CALL gds.graph.exists('moviesProjection')
'''

# --*-- Node2Vec Embedding --*--
# ----------------------------
Node2Vec = '''
    CALL gds.beta.node2vec.mutate('moviesProjection', {
        randomSeed: 42,
        returnFactor: 1.0, 
        inOutFactor: 1.0, 
        embeddingDimension: 256,
        mutateProperty: 'embedding'
        }
    )
    YIELD nodePropertiesWritten
'''


# --*-- FastRP Embedding --*--
# ----------------------------
FastRP = '''
    CALL gds.fastRP.mutate('moviesProjection', {
        embeddingDimension: 256,
        randomSeed: 42,
        mutateProperty: 'embedding'
        }
    )
    YIELD nodePropertiesWritten
'''

# --*--  --*--
# -------------------------
kNN_Similarity = '''
    CALL gds.knn.write('moviesProjection', {
        topK: 10,
        nodeProperties: ['embedding'],
        randomSeed: 42,
        concurrency: 1,
        sampleRate: 1.0,
        deltaThreshold: 0.0,
        writeRelationshipType: "SIMILAR_kNN",
        writeProperty: "sim_kNN_score"
    })
    YIELD nodesCompared, relationshipsWritten, similarityDistribution
    RETURN nodesCompared, relationshipsWritten, similarityDistribution.mean as meanSimilarity
'''

# ----------------------------------------------
# ----------------------------------------------


if __name__=="__main__":
    main()