#!/bin/bash

docker push $CLIENT_ECR_URI:$COMMIT_HASH
docker push $SERVER_ECR_URI:$COMMIT_HASH

echo "Subida completada :)"