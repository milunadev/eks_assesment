#!/bin/bash -e

### PROVISIONING GRPC ENVIRONMENT IN WINDOWS SYSTEM ###
python -m venv grpcvenv
source grpcvenv/Scripts/activate
echo `pwd`
pip install -r requirements.txt
