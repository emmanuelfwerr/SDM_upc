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
            if suppress_output == False:
                output = pd.DataFrame([dict(obj) for obj in response])
                output.to_csv('./PartB_output/PartB_{}.csv'.format(query_name), index=False, sep=';')
                print(output)
        # print message if transaction successful and return query esponse
        print('\n{} Transaction Completed Succesfully!'.format(query_name))
    except Exception as e: # error handling
        print("\n{} failed: ".format(query_name), e)


def main():
    '''
        Orchestrates main functionality of script. Initializes Neo4j driver and runs Cypher queries 
        as read/write transactions using custom function.
    '''
    # initialize neo4j driver
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # run Query_1 read transaction
        run_cypher(query_1, driver, query_name='Query1')
        # run Query_2 read transaction
        run_cypher(query_2, driver, query_name='Query2')
        # run Query_3 read transaction
        run_cypher(query_3, driver, query_name='Query3')
        # run Query_4 read transaction
        run_cypher(query_4, driver, query_name='Query4')


# B.1 - Find the top 3 most cited papers of each conference
query_1 = '''
    MATCH (p2:Paper)<-[:CitedBy]-(p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c:Conference)
    WITH c.ID as conference_id, c.Conference as conference_name, p1.Title as paper, count(*) as citations
    ORDER BY conference_id, citations DESC
    WITH conference_id, conference_name, collect([paper, citations]) as result
    RETURN conference_id, conference_name,
    result[0][0] as Paper1, result[0][1] as Total_Citations_Paper1,
    result[1][0] as Paper2, result[1][1] as Total_Citations_Paper2,
    result[2][0] as Paper3, result[2][1] as Total_Citations_Paper3;
'''

# B.2 - For each conference find its community: i.e., those authors that have published papers on that 
# conference in, at least, 4 different editions.
query_2 = ''' 
    MATCH (p:Person)<-[:WritenBy]-(p1:Paper)-[:PublishedOn]->(e1:Edition)-[:PartOf]->(c:Conference)
    WITH c.ID as conference_id, c.Conference as conference_name, p.Name as author, count(DISTINCT e1.Edition) as publications
    ORDER BY conference_id, publications DESC
    WHERE publications > 3
    WITH conference_id, conference_name, collect(author) as community_authors
    RETURN conference_id, conference_name, community_authors;
'''
    
# B.3 - Find the impact factors of the journals in your graph
query_3 = '''
    MATCH (j:Journal)
    CALL{
        WITH j
        MATCH (p2:Paper)-[:CitedBy]->(p1:Paper)-[:PublishedOn]->(v:Volume{Year: '2022'})-[:PartOf]->(j)
        WHERE EXISTS {
        MATCH(j)<-[:PartOf]-(v1:Volume)<-[:PublishedOn]-(p2)
        WHERE v1.Year IN ["2021","2020"]}
        RETURN j.Journal as journal_name, p2.ID as paper2_id
    }
    CALL{
        WITH j
        MATCH(j)<-[:PartOf]-(v:Volume)<-[:PublishedOn]-(p1:Paper)
        WHERE v.Year IN ["2021","2020"]
        WITH j.Journal as journal_name, p1.Title as paper, count(*) as publications
        WITH sum(publications) AS total_publications
        WHERE total_publications > 0
        RETURN total_publications
    }
    WITH journal_name, count(paper2_id) as citations_2020_2021, total_publications as total_publications_2022
    RETURN journal_name, citations_2020_2021, total_publications_2022, round( (1.0*citations_2020_2021) / (total_publications_2022), 2) as impact_factor;
'''

# B.4 - Find the h-indexes of the authors in your graph
query_4 = '''
    MATCH (p:Person)<-[:WritenBy]-(p1:Paper)-[:CitedBy]->(p2:Paper)
    WITH p.Name as author_name, p1.Title as Title, count(*) as total_citations 
    ORDER BY total_citations desc
    WITH author_name, collect(total_citations) as list_total_citations
    WITH author_name, [ i IN range(1,size(list_total_citations)) where i <= list_total_citations[i-1] | [list_total_citations[i-1], i] ] as list_hindex
    RETURN author_name, list_hindex[-1][1] as h_index
    ORDER BY h_index desc;
'''

# ----------------------------------------------
# ----------------------------------------------


if __name__=="__main__":
    main()