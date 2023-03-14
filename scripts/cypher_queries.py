# ---*--- Neo4j Cypher Queries ---*---
# ------------------------------------

# data path
path = ''

# A.2 - load graph nodes from CSV
cypher_init_nodes = [
    ''' LOAD CSV with headers FROM 'file:///data/synthetic/papers.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Paper {ID: row.id, Title: row.title, Abstract: row.abstract});''',

    ''' LOAD CSV with headers FROM 'file:///data/synthetic/authors.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Person {ID: row.id, Name: row.author});''',

    ''' LOAD CSV with headers FROM 'file:///data/synthetic/keywords.csv' AS row FIELDTERMINATOR ';' 
    CREATE (:Keyword {ID: row.keyword_id, Keyword: row.keyword_name});''',

    ''' LOAD CSV with headers FROM 'file:///data/synthetic/topics.csv' AS row FIELDTERMINATOR ';'
        CREATE (:Topic {ID: row.topic_id, Topic: row.topic_name});''',

    ''' LOAD CSV with headers FROM 'file:///data/synthetic/conferences.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Conference {ID: row.publisher_id, Conference: row.conference_name});''',

    ''' LOAD CSV with headers FROM 'file:///data/synthetic/conferences.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Edition {ID: row.publisherType_id, Edition: row.edition, City: row.venue, Year: row.year, Season: row.season});''',

    ''' LOAD CSV with headers FROM 'file:///data/synthetic/journals.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Journal {ID: row.publisher_id, Journal: row.journal_name});''',

    ''' LOAD CSV with headers FROM 'file:///data/synthetic/journals.csv' AS row FIELDTERMINATOR ';' 
        CREATE (:Volume {ID: row.publisherType_id, Volume: row.volume, Year: row.year});'''
]

# A.2 - load graph edges from CSV
cypher_init_relations = [
    ''' LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/paper_TO_person.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (person:Person {ID: row.author_id})
        MERGE (paper)-[:WritenBy]->(person);''',

    ''' LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/paper_TO_person.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (person:Person {ID: row.co_author_id})
        MERGE (paper)-[:CoauthoredBy]->(person);''',

    ''' LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/paper_TO_person.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (person:Person {ID: row.reviewer1_id})
        MERGE (paper)-[:ReviewedBy]->(person);''',

    ''' LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/paper_TO_person.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (person:Person {ID: row.reviewer2_id})
        MERGE (paper)-[:ReviewedBy]->(person);''',

    ''' LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/paper_TO_person.csv" AS row FIELDTERMINATOR ';' 
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (person:Person {ID: row.reviewer3_id})
        MERGE (paper)-[:ReviewedBy]->(person);''',

    '''LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/paper_TO_paper.csv" AS row
        MERGE (paper1:Paper {ID: row.cited_paper_id})
        MERGE (paper2:Paper {ID: row.citing_paper_id})
        MERGE (paper1)-[:CitedBy]->(paper2);''',

    '''LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/paper_TO_edition.csv" AS row
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (edition:Edition {ID: row.edition_id})
        MERGE (paper)-[:PublishedOn]->(edition);''',

    '''LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/edition_TO_conference.csv" AS row
        MERGE (edition:Edition {ID: row.edition_id})
        MERGE (conference:Conference {ID: row.conference_id})
        MERGE (edition)-[:PartOf]->(conference);''',

    '''LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/paper_TO_volume.csv" AS row
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (volume:Volume {ID: row.volume_id})
        MERGE (paper)-[:PublishedOn]->(volume);''',

    '''LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/volume_TO_journal.csv" AS row
        MERGE (volume:Volume {ID: row.volume_id})
        MERGE (journal:Journal {ID: row.journal_id})
        MERGE (volume)-[:PartOf]->(journal);''',

    '''LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/paper_TO_keyword.csv" AS row
        MERGE (paper:Paper {ID: row.paper_id})
        MERGE (keyword:Keyword {ID: row.keyword_id})
        MERGE (paper)-[:HasKeyword]->(keyword);''',

    '''LOAD CSV WITH HEADERS FROM "file:///data/synthetic/relations/keyword_TO_topic.csv" AS row
        MERGE (keyword:Keyword {ID: row.keyword_id})
        MERGE (topic:Topic {ID: row.topic_id})
        MERGE (keyword)-[:CorrespondTo]->(topic);'''
]

# A.3 - extend graph nodes from CSV

# A.3 - extend graph edges from CSV
