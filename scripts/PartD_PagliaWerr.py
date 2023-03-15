import pandas as pd
from neo4j import GraphDatabase


class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


conn = Neo4jConnection(uri="neo4j://localhost:7687", user="neo4j", pwd="password")




# ------------------------------------------------------------------------------------- Page Rank
query_string = '''
    CALL gds.graph.project('pagerank_example', 'Paper', 'CitedBy');
    '''
conn.query(query_string, db='neo4j')

query_string = '''
    CALL gds.pageRank.stream('pagerank_example',
    {maxIterations: 15, dampingFactor: 0.70}) YIELD nodeId, score
    RETURN gds.util.asNode(nodeId).Title AS name, round(score,2) as score
    ORDER BY score DESC LIMIT 10;
    '''

dtf_data = pd.DataFrame([dict(_) for _ in conn.query(query_string, db='neo4j')])
print(dtf_data)


