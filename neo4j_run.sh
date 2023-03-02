
# run neo4j:5.5.0 docker image
docker run \
    --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:5.5.0