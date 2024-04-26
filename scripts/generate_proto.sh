#!/bin/bash -e
echo "Generating proto grpc files..."
python -m grpc_tools.protoc -I=protobufs/ --python_out=protobufs/ --grpc_python_out=protobufs/ protobufs/messaging.proto
echo "SUCESS: Proto grpc files generated y protobufs"

echo "####################################################"
echo "Copying proto grpc files to server and client folders"
cp protobufs/messaging_pb2.py client/
cp protobufs/messaging_pb2_grpc.py client/
cp protobufs/messaging_pb2_grpc.py server/
cp protobufs/messaging_pb2.py server/
echo "SUCESS: Proto grpc files copied to server and client folders"

