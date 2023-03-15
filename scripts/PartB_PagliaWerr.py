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


# 1. Find the top 3 most cited papers of each conference
query_string = '''MATCH (p2:Paper)<-[:CitedBy]-(p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c:Conference)
WITH c.Conference as conference, p1.Title as paper, count(*) as cites
ORDER BY conference,cites DESC
WITH conference, collect([paper,cites]) as Papers
RETURN conference as conference_name,
Papers[0][0] as Cited_Paper1, Papers[0][1] as Num_cites1,
Papers[1][0] as Cited_Paper2, Papers[1][1] as Num_cites2,
Papers[2][0] as Cited_Paper3, Papers[2][1] as Num_cites3;
'''

query1 = pd.DataFrame([dict(_) for _ in conn.query(query_string, db='neo4j')])
print(query1)

