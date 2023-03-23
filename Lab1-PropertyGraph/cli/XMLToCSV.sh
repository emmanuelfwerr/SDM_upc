# run python script to tranfsorm graph data format from XML to CSV 
python ./src/XMLToCSV.py --annotate --neo4j ./data/xml/dblp.xml ./data/xml/dblp.dtd ./data/csv/dblp.csv --relations author:authored_by journal:published_in 

# publisher:published_by school:submitted_at editor:edited_by cite:has_citation series:is_part_of ?