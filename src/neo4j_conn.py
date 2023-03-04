from neo4j import GraphDatabase


class Neo4jConnection:
    '''
    
    '''
    def __init__(self, uri: str, user: str, password: str):
        try:
            self.__driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as e:
            print("Failed to create Neo4j driver: ", e)

    def verify_conn(self):
        # Verify the connection details
        self.__driver.verify_connectivity()

    def close(self):
        self.__driver.close()

    @staticmethod
    def query(self, query: str, db: str = None):
        '''
        
        '''
        assert self.__driver is not None, "Neo4j driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
            session.close() # close conn
        except Exception as e:
            print("Query failed: ", e)

        return response