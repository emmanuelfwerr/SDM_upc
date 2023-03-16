from neo4j import GraphDatabase


# instantiate neo4j credentials
URI = 'neo4j://localhost:7687'
AUTH = ('neo4j', 'password')
DB_NAME = 'neo4j'

def run_cypher(query: str, driver: object):
    '''
        Opens a session using Neo4j driver and executes a write transaction.

            Parameters:
                query (str): Cypher query formatted as string
                driver (obj): Neo4j Driver object

            Returns:
                response (obj): query response as list
    '''
    # neo4j transaction commit error handling
    try:
        # initialize neo4j session
        with driver.session(database=DB_NAME) as session:
            response = list(session.run(query))
        # print message if transaction successful and return query esponse
        print('Transaction Completed Succesfully!')
        return response
    except Exception as e: # error handling
        print("Query failed: ", e)


def main():
    '''
        Orchestrates main functionality of script. Initializes Neo4j driver and runs Cypher queries 
        as read/write transactions using custom function.
    '''
    # initialize neo4j driver
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # run query transactions to create all nodes
        for query in cypher_init_nodes:
            run_cypher(query, driver)

        # run query transactions to create all relationships
        for query in cypher_init_relations:
            run_cypher(query, driver)


# --*-- A.2 - load graph nodes from CSV --*--
# -------------------------------------------
cypher_init_nodes = [
    ''' LOAD CSV WITH HEADERS FROM 'file:///papers.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Paper {ID: row.paper_id, Title: row.title, Abstract: row.abstract});''',

    ''' LOAD CSV WITH HEADERS FROM 'file:///authors.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Person {ID: row.author_id, Name: row.author_name});''',

    ''' LOAD CSV WITH HEADERS FROM 'file:///keywords.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Keyword {ID: row.keyword_id, Keyword: row.keyword_name});''',

    ''' LOAD CSV WITH HEADERS FROM 'file:///topics.csv' AS row FIELDTERMINATOR ';'
        CREATE (:Topic {ID: row.topic_id, Topic: row.topic_name});''',

    ''' LOAD CSV WITH HEADERS FROM 'file:///conferences.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Conference {ID: row.conference_id, Conference: row.conference_name});''',

    ''' LOAD CSV WITH HEADERS FROM 'file:///editions.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Edition {ID: row.edition_id, Edition: row.edition, City: row.venue, Year: row.year, Season: row.season});''',

    ''' LOAD CSV WITH HEADERS FROM 'file:///journals.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Journal {ID: row.journal_id, Journal: row.journal_name});''',

    ''' LOAD CSV WITH HEADERS FROM 'file:///volumes.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Volume {ID: row.volume_id, Volume: row.volume, Year: row.year});'''
]

# --*-- A.2 - load graph edges from CSV --*--
# -------------------------------------------
cypher_init_relations = [
    ''' LOAD CSV WITH HEADERS FROM "file:///paper_TO_author.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (person:Person {ID: row.author_id})
        MERGE (paper)-[:WritenBy]->(person);''',

    ''' LOAD CSV WITH HEADERS FROM "file:///paper_TO_author.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (person:Person {ID: row.co_author_id})
        MERGE (paper)-[:CoauthoredBy]->(person);''',

    ''' LOAD CSV WITH HEADERS FROM "file:///paper_TO_reviewer.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (person:Person {ID: row.reviewer_id})
        MERGE (paper)-[:ReviewedBy]->(person);''',

    '''LOAD CSV WITH HEADERS FROM "file:///paper_TO_paper.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper1:Paper {ID: row.cited_paper_id})
        MERGE (paper2:Paper {ID: row.citing_paper_id})
        MERGE (paper1)-[:CitedBy]->(paper2);''',

    '''LOAD CSV WITH HEADERS FROM "file:///paper_TO_edition.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (edition:Edition {ID: row.edition_id})
        MERGE (paper)-[:PublishedOn]->(edition);''',

    '''LOAD CSV WITH HEADERS FROM "file:///edition_TO_conference.csv" AS row FIELDTERMINATOR ';' 
        MERGE (edition:Edition {ID: row.edition_id})
        MERGE (conference:Conference {ID: row.conference_id})
        MERGE (edition)-[:PartOf]->(conference);''',

    '''LOAD CSV WITH HEADERS FROM "file:///paper_TO_volume.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (volume:Volume {ID: row.volume_id})
        MERGE (paper)-[:PublishedOn]->(volume);''',

    '''LOAD CSV WITH HEADERS FROM "file:///volume_TO_journal.csv" AS row FIELDTERMINATOR ';' 
        MERGE (volume:Volume {ID: row.volume_id})
        MERGE (journal:Journal {ID: row.journal_id})
        MERGE (volume)-[:PartOf]->(journal);''',

    '''LOAD CSV WITH HEADERS FROM "file:///paper_TO_keyword.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (keyword:Keyword {ID: row.keyword_id})
        MERGE (paper)-[:HasKeyword]->(keyword);''',

    '''LOAD CSV WITH HEADERS FROM "file:///keyword_TO_topic.csv" AS row FIELDTERMINATOR ';' 
        MERGE (keyword:Keyword {ID: row.keyword_id})
        MERGE (topic:Topic {ID: row.topic_id})
        MERGE (keyword)-[:CorrespondTo]->(topic);'''
]

# ----------------------------------------------
# ----------------------------------------------


if __name__=="__main__":
    main()