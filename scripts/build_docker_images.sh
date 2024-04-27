#!/bin/bash -e

CLIENT_IMAGE=$1
SERVER_IMAGE=$2

echo "Construyendo y etiquetando la imagen del cliente..."
docker build -t $CLIENT_IMAGE ./client
echo "Construyendo y etiquetando la imagen del servidor..."
docker build -t $SERVER_IMAGE ./server

