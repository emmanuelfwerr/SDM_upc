import rdflib
import csv
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Create a new RDF graph
g = Graph()
# Define the namespaces
ABox = Namespace("http://graph.org/abox/")
g.bind("ABox", ABox)

# Function to load instances from a CSV file, ABox
def load_classes_from_csv(file_path, instance_class):
    with open(file_path, "r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        if instance_class == 'Author':
            for row in csv_reader:
                individual_uri = ABox[f"{instance_class}_{row['id']}"]
                g.add((individual_uri, RDF.type, ABox[instance_class]))
                g.add((individual_uri, ABox.Name, Literal(row["name"], lang="en")))

                if row["reviewer"] == 'yes':
                    reviewer_uri = ABox[f"Reviewer_{row['id']}"]
                    g.add((reviewer_uri, RDF.type, ABox['Reviewer']))
                    g.add((reviewer_uri, ABox.Name, Literal(row["name"], lang="en")))
        
        elif instance_class == 'Handlers':
            for row in csv_reader:
                sub_class = row["type"]
                individual_uri = ABox[f"{sub_class}_{row['id']}"]
                g.add((individual_uri, RDF.type, ABox[sub_class]))

        elif instance_class == 'Paper':
            for row in csv_reader:
                sub_class = row["type"]
                individual_uri = ABox[f"{sub_class}_{row['id']}"]
                g.add((individual_uri, RDF.type, ABox[sub_class]))
                g.add((individual_uri, ABox.text_date, Literal(row["date"], datatype=XSD.integer)))
                g.add((individual_uri, ABox.text_name, Literal(row["name"], lang="en")))
                g.add((individual_uri, ABox.text_valid, Literal(row["valid"], lang="en")))

        elif instance_class == 'Review':
            for row in csv_reader:
                individual_uri = ABox[f"{instance_class}_{row['id']}"]
                g.add((individual_uri, RDF.type, ABox[instance_class]))
                g.add((individual_uri, ABox.text_date, Literal(row["date"], datatype=XSD.integer)))

        elif instance_class == 'Area':
            for row in csv_reader:
                individual_uri = ABox[f"{instance_class}_{row['id']}"]
                g.add((individual_uri, RDF.type, ABox[instance_class]))
                g.add((individual_uri, ABox.area, Literal(row["area"], lang="en")))
        
        elif instance_class == 'Publication':
            for row in csv_reader:
                individual_uri = ABox[f"{instance_class}_{row['id']}"]
                g.add((individual_uri, RDF.type, ABox[instance_class]))
                g.add((individual_uri, ABox.text_name, Literal(row["name"], lang="en")))
                

        elif instance_class == 'Conferences':
            for row in csv_reader:
                sub_class = row["type"]
                individual_uri = ABox[f"{sub_class}_{row['id']}"]
                proceeding_uri = ABox[f"Proceeding_{row['id']}"]
                g.add((individual_uri, RDF.type, ABox[sub_class]))
                g.add((proceeding_uri, RDF.type, ABox["Proceeding"]))
                g.add((individual_uri, ABox.conference_city, Literal(row["city"], lang="en")))
                g.add((individual_uri, ABox.conference_name, Literal(row["name"], lang="en")))
                g.add((individual_uri, ABox.conference_time, Literal(row["date"], datatype=XSD.integer)))

        elif instance_class == 'Journal':
            for row in csv_reader:
                journal_uri = ABox[f"{instance_class}_{row['id']}"]
                g.add((journal_uri, RDF.type, ABox[instance_class]))
                g.add((journal_uri, ABox.journal_name, Literal(row["name"], lang="en")))

                # Assuming values are comma separated
                volume_dates = row["date"].split(",")
                volumeID = row["volumes"].split(",")
                for volume in range(1, int(row["vol_num"]) + 1):
                    volume_uri = ABox[f"Volume_{row['id']}_v{volume}"]
                    g.add((volume_uri, RDF.type, ABox['Volume']))

                    volume_id = volumeID[volume - 1].strip()
                    volume_date = volume_dates[volume - 1].strip()
                    g.add((volume_uri, ABox.volumeID, Literal(volume_id, datatype=XSD.integer)))
                    g.add((volume_uri, ABox.Date, Literal(volume_date, datatype=XSD.date)))

def load_relationships_from_csv(file_path, instance_rel):
    with open(file_path, "r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        
        #Author writes papers
        if instance_rel == 'writes':
            for row in csv_reader:
                author_uri = ABox[f"Author_{row['author']}"]
                paper_uri = ABox[f"Paper_{row['research_article']}"]
                g.add((author_uri, ABox.writes, paper_uri))

        #Reviewers submits reviews
        elif instance_rel == 'submits':
            for row in csv_reader:
                reviewers_uri = ABox[f"Reviewers_{row['reviewer']}"]
                review_uri = ABox[f"Review_{row['article']}"]
                g.add((reviewers_uri, ABox.submits, review_uri))

        #Papers submitted to conferences
        elif instance_rel == 'submitted1':
            for row in csv_reader:
                conference_uri = ABox[f"Conferences_{row['conference']}"]
                paper_uri = ABox[f"Paper_{row['research_article']}"]
                g.add((paper_uri, ABox.submitted, conference_uri))

        #Papers submitted to journals
        elif instance_rel == 'submitted2':

            for row in csv_reader:
                journal_uri = ABox[f"Journal_{row['id']}"]

                # Assuming values are comma separated
                papers = row["research_article"].split(",")
                for paper in range(1, int(row["vol_num"]) + 1):
                    paper_uri = ABox[f"Paper_{papers[paper-1]}"]
                    g.add((paper_uri, ABox.submitted, journal_uri))


        #Papers pertains_to type
        elif instance_rel == 'pertains_to1':
            for row in csv_reader:
                paper_uri = ABox[f"Paper_{row['research_article']}"]
                area_uri = ABox[f"Area_{row['area']}"]
                g.add((paper_uri, ABox.pertains_to, area_uri))

        #Proceeding pertains_to type
        elif instance_rel == 'pertains_to2':
            for row in csv_reader:
                conference_uri = ABox[f"Proceeding_{row['conference']}"]
                area_uri = ABox[f"Area_{row['area']}"]
                g.add((conference_uri, ABox.pertains_to, area_uri))

        #Journal pertains_to type
        elif instance_rel == 'pertains_to3':
            for row in csv_reader:
                journal_uri = ABox[f"Journal_{row['id']}"]
                area_uri = ABox[f"Area_{row['area']}"]
                g.add((journal_uri, ABox.pertains_to, area_uri))

        #Reviewers accepts_or_rejects papers
        elif instance_rel == 'accepts_or_rejects':
            for row in csv_reader:
                reviewers_uri = ABox[f"Reviewers_{row['reviewer']}"]
                paper_uri = ABox[f"Paper_{row['research_article']}"]
                g.add((reviewers_uri, ABox.accepts_or_rejects, paper_uri))

        #Handlers assigns reviewers
        elif instance_rel == 'assigns1':
            for row in csv_reader:
                assigns1_uri = ABox[f"Chairs_{row['chair']}"]
                reviewers_uri = ABox[f"Reviewers_{row['reviewer']}"]
                g.add((assigns1_uri, ABox.assigns, reviewers_uri))

        elif instance_rel == 'assigns2':
            for row in csv_reader:
                assigns2_uri = ABox[f"Editors_{row['editor']}"]
                reviewers_uri = ABox[f"Reviewers_{row['reviewer']}"]
                g.add((assigns2_uri, ABox.assigns, reviewers_uri))

        #Papers are accepted as publications
        elif instance_rel == 'accepted_as':
            for row in csv_reader:
                paper_uri = ABox[f"Paper_{row['research_article']}"]
                publication_uri = ABox[f"Publication_{row['id']}"]
                g.add((paper_uri, ABox.accepted_as, publication_uri))

        #Publications has reviews
        elif instance_rel == 'has':
            for row in csv_reader:
                review_uri = ABox[f"Review_{row['review']}"]
                publication_uri = ABox[f"Publication_{row['id']}"]
                g.add((publication_uri, ABox.has, review_uri))

        #Publications are published in
        elif instance_rel == 'published_in1':
            for row in csv_reader:
                publication_uri = ABox[f"Publication_{row['id']}"]
                proceeding_uri = ABox[f"Proceeding_{row['conference']}"]
                g.add((publication_uri, ABox.published_in, proceeding_uri))

        elif instance_rel == 'published_in2':
            for row in csv_reader:
                publication_uri = ABox[f"Publication_{row['id']}"]
                volumes_uri = ABox[f"Volume_{row['volumes']}"]
                g.add((publication_uri, ABox.published_in, volumes_uri))

        #Conference handled_by chairs
        elif instance_rel == 'handled_by1':
            for row in csv_reader:
                conference_uri = ABox[f"Conferences_{row['conference']}"]
                handler1_uri = ABox[f"Chairs_{row['chair']}"]
                g.add((handler1_uri, ABox.handled_by1, conference_uri))

        #Journal handled_by editors
        elif instance_rel == 'handled_by2':
            for row in csv_reader:
                journal_uri = ABox[f"Journal_{row['id']}"]
                handler2_uri = ABox[f"Editors_{row['editor']}"]
                g.add((handler2_uri, ABox.handled_by2, journal_uri))

## Load instances from the CSV files

#Classes

load_classes_from_csv("authors.csv", "Author")
load_classes_from_csv("handlers.csv", "Handlers")
load_classes_from_csv("papers.csv", "Paper")
load_classes_from_csv("review.csv", "Review")
load_classes_from_csv("area.csv", "Area")
load_classes_from_csv("conference.csv", "Conferences")
load_classes_from_csv("journals.csv", "Journal")
load_classes_from_csv("volumes.csv", "Volumes")
load_classes_from_csv("publication.csv", "Publication")

#Relations

load_relationships_from_csv("writes.csv", "writes")
load_relationships_from_csv("submits.csv", "submits")
load_relationships_from_csv("submitted_conf.csv", "submitted1")
load_relationships_from_csv("journals.csv", "submitted2")
load_relationships_from_csv("pertains_paper.csv", "pertains_to1")
load_relationships_from_csv("submitted_conf.csv", "pertains_to2")
load_relationships_from_csv("journals.csv", "pertains_to3")
load_relationships_from_csv("reviewed_by.csv", "accepts_or_rejects")
load_relationships_from_csv("assigns_chair.csv", "assigns1")
load_relationships_from_csv("assigns_editor.csv", "assigns2")
load_relationships_from_csv("handled_chair.csv", "handled_by1")
load_relationships_from_csv("handled_editor.csv", "handled_by2")

load_relationships_from_csv("publication.csv", "accepted_as")
load_relationships_from_csv("publication.csv", "has")
load_relationships_from_csv("published_conf.csv", "published_in1")
load_relationships_from_csv("published_vol.csv", "published_in2")

# Save the ABox in the OWL file
g.serialize(destination='12I-B3-GonzalezWerr.owl', format='pretty-xml')

print("ABox OWL file created successfully.")