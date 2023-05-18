from rdflib import Graph

# Initialize the graphs
tbox_graph = Graph()
abox_graph = Graph()

# Parse in an RDF file into the graph
tbox_graph.parse("Prueba tur.ttl", format="turtle")
abox_graph.parse("onto.owl", format="xml")

# Combine the two graphs
merged_graph = tbox_graph + abox_graph
           
merged_graph.serialize(destination='merged.owl', format='pretty-xml')