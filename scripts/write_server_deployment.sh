#!/bin/bash -e
SERVER_IMAGE=$1

cat << EOF > eks_files/deployment_server.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: server-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: server
  template:
    metadata:
      labels:
        app: server
    spec:
      containers:
      - name: server
        image: ${SERVER_IMAGE}
        ports:
        - containerPort: 50051
EOF