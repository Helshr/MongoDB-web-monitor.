#! /bin/bash

# run docker-compose to start mongoDB cluster
docker-compose -f docker-compose.yml up -d

# init mongoDB replicate set.
docker-compose exec configsvr01 sh -c "mongo < /scripts/init-configserver.js"
docker-compose exec shard01-a sh -c "mongo < /scripts/init-shard01.js"
docker-compose exec router01 sh -c "mongo < /scripts/init-router.js"

# create mongoexporter image
cd MongoExporter && docker build -t mongoexporter -f Dockerfile . && cd ..

# create mongoexporter conf and prometheus conf
cd mongoDBConf && python configCreator.py mongo.cf && cd ..

# start prometheus and mongoExporter container.
cd mongoDBConf && docker-compose -f deployment/compose_rs.yml up -d && cd ..
