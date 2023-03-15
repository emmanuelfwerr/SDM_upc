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
query_1_string = '''
    MATCH (p2:Paper)<-[:CitedBy]-(p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c:Conference)
    WITH c.Conference as conference, p1.Title as paper, count(*) as cites
    ORDER BY conference,cites DESC
    WITH conference, collect([paper,cites]) as Papers
    RETURN conference as conference_name,
    Papers[0][0] as Cited_Paper1, Papers[0][1] as Num_cites1,
    Papers[1][0] as Cited_Paper2, Papers[1][1] as Num_cites2,
    Papers[2][0] as Cited_Paper3, Papers[2][1] as Num_cites3;
'''

query1 = pd.DataFrame([dict(_) for _ in conn.query(query_1_string, db='neo4j')])
print(query1)
query1.to_csv('PartB_query1.csv', index=False, sep=';')


# 2. For each conference find its community: i.e., those authors that have published papers on that conference in, at least, 4 different editions.
query_2_string = ''' 
    MATCH (author:Person)<-[:WritenBy]-(p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c:Conference)
    WITH c.Conference as conference, author.Name as author, count(distinct e1.Edition) as publications
    ORDER BY conference,publications DESC
    WHERE publications>0
    WITH conference, collect([author]) as Comunity
    RETURN conference as Conference_name, Comunity;
'''

query2 = pd.DataFrame([dict(_) for _ in conn.query(query_2_string, db='neo4j')])
print(query2)
query2.to_csv('PartB_query2.csv', index=False, sep=';')

# 3. Find the impact factors of the journals in your graph
query_3_string = '''
MATCH (j:Journal)
CALL{
    with j
    MATCH (p2:Paper)-[:CitedBy]->(p1:Paper)-[:PublishedOn]->(v:Volume{Year: '2002'})-[:PartOf]->(j)
    WHERE EXISTS {
    MATCH(j)<-[:PartOf]-(v1:Volume)<-[:PublishedOn]-(p2)
    WHERE v1.Year IN ["2001","2000"]}
    REturn j.Journal as Journal_title, p2.ID as paper2_id
}
CALL{
    with j
    MATCH(j)<-[:PartOf]-(v:Volume)<-[:PublishedOn]-(p1:Paper)
    WHERE v.Year IN ["2001","2000"]
    WITH j.Journal as journal_title, p1.Title as paper, count(*) as num_publications
    WITH sum(num_publications) AS total_num_publications
    where total_num_publications >0
    return total_num_publications
}
with Journal_title,count(paper2_id)as cites_2000_2001, total_num_publications as num_publications_2002
return Journal_title,cites_2000_2001,num_publications_2002,round(1.0*cites_2000_2001/num_publications_2002,2) as Impact_Factor;
'''

query3 = pd.DataFrame([dict(_) for _ in conn.query(query_3_string, db='neo4j')])
print(query3)
query3.to_csv('PartB_query3.csv', index=False, sep=';')


# 4. Find the h-indexes of the authors in your graph
query_4_string = '''MATCH (pe:Person)<-[:WritenBy]-(p1:Paper)-[:CitedBy]->(p2:Paper)
WITH pe.Name as Author, p1.Title as Title, count(*) as NumCites 
ORDER BY NumCites desc
WITH Author, collect(NumCites) as list_NumCites
WITH Author, [x IN range(1,size(list_NumCites)) where x<=list_NumCites[x-1]| [list_NumCites[x-1],x] ] as list_hindex
RETURN Author,list_hindex[-1][1] as h_index
ORDER BY h_index desc;
'''

query4 = pd.DataFrame([dict(_) for _ in conn.query(query_4_string, db='neo4j')])
print(query4)
query4.to_csv('PartB_query4.csv', index=False, sep=';')
