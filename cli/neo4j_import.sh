#!/bin/bash
neo4j-admin import --mode=csv --database=dblp.db --delimiter ";" --array-delimiter "|" --id-type INTEGER --nodes:book "./data/csv/dblp_book_header.csv,./data/csv/dblp_book.csv" --nodes:inproceedings "./data/csv/dblp_inproceedings_header.csv,./data/csv/dblp_inproceedings.csv" --nodes:mastersthesis "./data/csv/dblp_mastersthesis_header.csv,./data/csv/dblp_mastersthesis.csv" --nodes:article "./data/csv/dblp_article_header.csv,./data/csv/dblp_article.csv" --nodes:incollection "./data/csv/dblp_incollection_header.csv,./data/csv/dblp_incollection.csv" --nodes:phdthesis "./data/csv/dblp_phdthesis_header.csv,./data/csv/dblp_phdthesis.csv" --nodes:www "./data/csv/dblp_www_header.csv,./data/csv/dblp_www.csv" --nodes:data "./data/csv/dblp_data_header.csv,./data/csv/dblp_data.csv" --nodes:proceedings "./data/csv/dblp_proceedings_header.csv,./data/csv/dblp_proceedings.csv" --nodes:journal "./data/csv/dblp_journal.csv" --relationships:published_in "./data/csv/dblp_journal_published_in.csv" --nodes:author "./data/csv/dblp_author.csv" --relationships:authored_by "./data/csv/dblp_author_authored_by.csv"