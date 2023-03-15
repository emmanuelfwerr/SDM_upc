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


# ------------------------------------------------------------------------------------- 1
query_string = '''
    create (c:community {name:'db'});
    '''
conn.query(query_string, db='neo4j')

query_string = '''
    match (c:community {name:'db'})
    match (kw:Keyword)
    where kw.Keyword in ['Data management', 'Indexing', 'Data modeling', 'Big data', 'Data processing', 'Data storage' , 'Data querying']
    merge (kw)-[:Related_to]->(c);
    '''
conn.query(query_string, db='neo4j')


# ------------------------------------------------------------------------------------- 2
# Conference
query_string = '''
    MATCH (c:Conference)
    CALL{
    with c
    match (p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c)
    with c, c.Conference as conference, count(*) as num_papers
    Return num_papers}
    
    MATCH (c)<-[:PartOf]-(e1:Edition)<-[:PublishedOn]-(p1:Paper)-[:HasKeyword]->(kw:Keyword)-[:Related_to]->(commu)
    with c, commu, c.Conference as conference, num_papers, count(distinct p1.ID) as num_papers_db
    with c, commu,conference, num_papers, num_papers_db, (1.0*num_papers_db/num_papers) as percentage
    where percentage >=0.9
    merge (c)-[:related_to]->(commu)
    return conference, num_papers,num_papers_db, round(percentage,2) as percentage_db_com;
    '''
dtf_data = pd.DataFrame([dict(_) for _ in conn.query(query_string, db='neo4j')])
print(dtf_data)


# Journal
query_string = '''
    MATCH (j:Journal)
    CALL{
    with j
    match (p1:Paper)-[:PublishedOn]->(v:Volume)-[:PartOf]->(j)
    with j, j.Journal as journal, count(*) as num_papers
    Return num_papers}
    
    MATCH (j)<-[:PartOf]-(v:Volume)<-[:PublishedOn]-(p1:Paper)-[:HasKeyword]->(kw:Keyword)-[:Related_to]->(commu)
    with j, commu, j.Journal as journal, num_papers, count(distinct p1.ID) as num_papers_db
    with j, commu,journal, num_papers, num_papers_db, (1.0*num_papers_db/num_papers) as percentage
    where percentage >=0.9
    merge (j)-[:related_to]->(commu)
    return journal, num_papers,num_papers_db, round(percentage,2) as percentage_db_com;
    '''
dtf_data = pd.DataFrame([dict(_) for _ in conn.query(query_string, db='neo4j')])
print(dtf_data)


# ------------------------------------------------------------------------------------- 3
query_string = '''
    CALL gds.pageRank.stream(
    {nodeQuery: 'match (p:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c1)-[:related_to]->(commu:community) where commu.name="db" return id(p) as id',
    relationshipQuery: 'match (commu1:community)<-[:related_to]-(c1)<-[:PartOf]-(e1:Edition)<-[:PublishedOn]-(p1:Paper)-[:CitedBy]->(p2:Paper)-[:PublishedOn]->(e2:Edition)-[:PartOf]->(c2)-[:related_to]->(commu2:community) where commu1.name="db" and commu2.name="db" return id(p1) as source, id(p2) as target'})
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS a, score
    ORDER BY score DESC
    match (commu:community {name:'db'})
    merge (a)-[:related_to]->(commu)
    return a.Title, score
    ORDER BY score DESC
    limit 10;
    '''
dtf_data = pd.DataFrame([dict(_) for _ in conn.query(query_string, db='neo4j')])
print(dtf_data)


# ------------------------------------------------------------------------------------- 4
query_string = '''
    CALL gds.pageRank.stream(
    {nodeQuery: 'match (p:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c1)-[:related_to]->(commu:community) where commu.name="db" return id(p) as id',
    relationshipQuery: 'match (commu1:community)<-[:related_to]-(c1)<-[:PartOf]-(e1:Edition)<-[:PublishedOn]-(p1:Paper)-[:CitedBy]->(p2:Paper)-[:PublishedOn]->(e2:Edition)-[:PartOf]->(c2)-[:related_to]->(commu2:community) where commu1.name="db" and commu2.name="db" return id(p1) as source, id(p2) as target'})
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS a, score
    ORDER BY score DESC
    match (commu:community {name:'db'})
    merge (a)-[:related_to]->(commu)
    with a.Title as title ,score ORDER BY score DESC
    limit 10
    with collect(title) as top_papers
    match (au:Person)<-[:WritenBy]-(p:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c)-[:related_to]->(commu:community)
    where p.Title in top_papers
    with au.Name as author, count(*) as counts
    with author, counts as num_influential_papers, case when counts >=2 then 'guru' else 'reviewer' end as reviewer_type
    merge (au)-[:related_to {type:reviewer_type}]->(commu)
    return distinct(author), num_influential_papers, reviewer_type
    order by num_influential_papers desc;
    '''
dtf_data = pd.DataFrame([dict(_) for _ in conn.query(query_string, db='neo4j')])
print(dtf_data)
