# Neo4j Graph Init Queries
neo_init_nodes = [
    ''' LOAD CSV with headers FROM 'file:///authors.csv' AS row FIELDTERMINATOR ',' 
        CREATE (:Person {ID: row.ID, Name: row.author});''',

    ''' LOAD CSV with headers FROM 'file:///conference.csv' AS row FIELDTERMINATOR ',' 
        CREATE (:Conference {ID: row.ID, Conference: row.Conference});''',

    ''' LOAD CSV with headers FROM 'file:///edition.csv' AS row FIELDTERMINATOR ',' 
        CREATE (:Edition {ID: row.ID, Edition: row.Edition, City: row.City, Year: row.Year});''',

    ''' LOAD CSV with headers FROM 'file:///topic.csv' AS row FIELDTERMINATOR ','
        CREATE (:Topic {ID: row.ID, Topic: row.Topic});''',

    ''' LOAD CSV with headers FROM 'file:///keyword.csv' AS row FIELDTERMINATOR ',' 
        CREATE (:Keyword {ID: row.ID, Keyword: row.Keyword});''',

    ''' LOAD CSV with headers FROM 'file:///papers.csv' AS row FIELDTERMINATOR ',' 
        CREATE (:Paper {ID: row.ID, Title: row.title, Abstract: row.Abstract});''',

    ''' LOAD CSV with headers FROM 'file:///volume.csv' AS row FIELDTERMINATOR ',' 
        CREATE (:Volume {ID: row.ID, Volume: row.volume, Year: row.year});''',
        
    ''' LOAD CSV with headers FROM 'file:///journal.csv' AS row FIELDTERMINATOR ',' 
        CREATE (:Journal {ID: row.ID, Journal: row.journal});'''
]

neo_init_relations = [
    ''' LOAD CSV WITH HEADERS FROM "file:///relation_WritenBy.csv" AS row
        MERGE (paper:Paper {ID: row.start})
        MERGE (person:Person {ID: row.end})
        MERGE (paper)-[:WritenBy]->(person);''',

    '''LOAD CSV WITH HEADERS FROM "file:///relation_CoauthoredBy.csv" AS row
        MERGE (paper:Paper {ID: row.start})
        MERGE (person:Person {ID: row.end})
        MERGE (paper)-[:CoauthoredBy]->(person);''',

    '''LOAD CSV WITH HEADERS FROM "file:///relation_CitedBy.csv" AS row
        MERGE (paper1:Paper {ID: row.start})
        MERGE (paper2:Paper {ID: row.end})
        MERGE (paper1)-[:CitedBy]->(paper2);''',

    '''LOAD CSV WITH HEADERS FROM "file:///relation_PublishedOn_edition.csv" AS row
        MERGE (paper:Paper {ID: row.start})
        MERGE (edition:Edition {ID: row.end})
        MERGE (paper)-[:PublishedOn]->(edition);''',

    '''LOAD CSV WITH HEADERS FROM "file:///relation_edition_conference.csv" AS row
        MERGE (edition:Edition {ID: row.start})
        MERGE (conference:Conference {ID: row.end})
        MERGE (edition)-[:PartOf]->(conference);''',

    '''LOAD CSV WITH HEADERS FROM "file:///relation_HasKeyword.csv" AS row
        MERGE (paper:Paper {ID: row.start})
        MERGE (keyword:Keyword {ID: row.end})
        MERGE (paper)-[:HasKeyword]->(keyword);''',

    '''LOAD CSV WITH HEADERS FROM "file:///relation_CorrespondTo.csv" AS row
        MERGE (keyword:Keyword {ID: row.start})
        MERGE (topic:Topic {ID: row.end})
        MERGE (keyword)-[:CorrespondTo]->(topic);''',

    '''LOAD CSV WITH HEADERS FROM "file:///relation_PublishedOn_volume.csv" AS row
        MERGE (paper:Paper {ID: row.start})
        MERGE (volume:Volume {ID: row.end})
        MERGE (paper)-[:PublishedOn]->(volume);''',

    '''LOAD CSV WITH HEADERS FROM "file:///relation_volume_journals.csv" AS row
        MERGE (volume:Volume {ID: row.start})
        MERGE (journal:Journal {ID: row.end})
        MERGE (volume)-[:PartOf]->(journal);'''
]

# other queries...
