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

        if user:
            print("User found: ", user, " generating token")
            token = jwt.encode({'username': username}, self.jwt_secret , algorithm='HS256')
            return chat.LoginResponse(token=token)
        else:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Invalid username or password')
            #return chat.LoginResponse(error='Invalid username or password')


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
    
    def SaveChat(self, request_iterator, context):
        print('Iniciando guardado de chat...', self)
        try:
            for note in request_iterator:
                print(note)
                if context.is_active():
                    print(note)
                    print(f'{note.username}: {note.message}')
                    # Aquí agregar lógica para guardar efectivamente los mensajes
                else:
                    print('El contexto no está activo.')
                    break
            print('Todos los mensajes fueron guardados exitosamente.')
            return chat.SaveChatResponse(success=True)
        except Exception as e:
            print(f'Error durante el guardado de chat: {e}')
            return chat.SaveChatResponse(success=False)
    
def serve():
    jwt_secret = secret_key
    mongo_url = 'mongodb://localhost:27017'

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    rpc.add_AuthServiceServicer_to_server(AuthService(mongo_url,jwt_secret), server)
   
    
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
