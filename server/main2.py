import messaging_pb2 as chat
import messaging_pb2_grpc as rpc
from concurrent import futures
import grpc
import jwt
from pymongo import MongoClient
import hashlib

secret_key = 'mydemokey'
database = "demo"
auth_collection = "users"

class AuthService(rpc.AuthServiceServicer):
    users = {
        'admin': 'pass',
        'mimi': 'pass',
        'pepe': 'pass',
        'juan': 'pass'
    }

    def __init__(self,mongo_url,jwt_secret):
        self.mongo_client = MongoClient(mongo_url)
        self.db = self.mongo_client[database]
        self.users_collection = self.db[auth_collection]
        self.jwt_secret = jwt_secret

    def AuthenticateUser(self, request, context):
        username = request.username
        password = request.password 

        #Buscar user en mongo
        user = self.users_collection.find_one({'username': username, 'password': password})

        if username in self.users and self.users[username] == password:
            token = jwt.encode({'username': username}, secret_key, algorithm='HS256')
            return chat.LoginResponse(token=token)
        else:
            return chat.LoginResponse(error='Invalid username or password')


class ChatServer(rpc.ChatServerServicer):

    def __init__(self):
        #History of chat messages
        self.chats = []
    
    #Streaming method from server to clients
    def ChatStream(self, request_iterator, context):
        last_index = 0
        while True:
            #Verify new messages
            while len(self.chats) > last_index:
                msg = self.chats[last_index]
                last_index += 1
                yield msg #Send mesage to clients
    
    #Method to receive messages from clients
    def SendNote(self, request, context):
        print(f'{request.name}: {request.message}')
        self.chats.append(request)   #Append to message history
        return chat.EmptyMessage()   #Return empty message
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    rpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('🚀 Servidor iniciado, escuchando...')

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print('⌨️ Interrupción por teclado detectada, cerrando el servidor...')
        server.stop(0)  # Detiene el servidor de inmediato
        print('✅ Servidor cerrado correctamente.')

if __name__ == '__main__':
    serve()
