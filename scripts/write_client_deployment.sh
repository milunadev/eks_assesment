#!/bin/bash -e
CLIENT_IMAGE=$1

cat << EOF > eks_files/deployment_client.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: client-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: client
  template:
    metadata:
      labels:
        app: client
    spec:
      containers:
      - name: client
        image: ${CLIENT_IMAGE}
        ports:
        - containerPort: 5000
        env:
        - name: SERVER_URL
          value: "server-service:50051"
EOF

cat eks_files/deployment_client.yaml
echo "Deployment created"