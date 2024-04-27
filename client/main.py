import grpc
import messaging_pb2 as chat
import messaging_pb2_grpc as rpc
import threading

##Change to server nameservice when using Docker
address = 'localhost'
port = 50051

class AuthClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(f'{address}:{port}')
        self.stub = rpc.AuthServiceStub(self.channel)

    def authenticate(self, username, password):
        request = chat.LoginRequest(username=username, password=password)
        response = self.stub.AuthenticateUser(request)
        if response.error:
            print("Error de autenticacion: ",response.error)
            return None
        return response.token

class ChatClient:
    def __init__(self, username, token):
        self.username = username
        self.token = token
        # Create a channel gRPC + stub
        channel = grpc.insecure_channel(f'{address}:{port}')
        self.connection = rpc.ChatServerStub(channel)

        # Create a thread for receiving messages
        threading.Thread(target=self.receive_messages, daemon=True).start()
    
    def receive_messages(self):
        metadata = [('authorization', f'Bearer {self.token}')]
        for note in self.connection.ChatStream(chat.EmptyMessage(),metadata=metadata):
            print(f'{note.name}: {note.message}')
    
    def send_message(self, message):
        if message:
            metadata = [('authorization', f'Bearer {self.token}')]
            note = chat.Note(name=self.username, message=message)
            self.connection.SendNote(note,metadata=metadata)

def run_chat_client(username):
    auth = AuthClient()
    token = auth.authenticate(username, 'pass')
    print("Token:", token)
    client = ChatClient(username,token)
    print("😀 Conectado al servidor de chat. Escriba sus mensajes a continuación: ")

    try:
        while True:
            message = input()
            client.send_message(message)
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta pronto!")  

def main():
    username = input("Ingrese su nombre de usuario: ")
    authClient = AuthClient()
    token = authClient.authenticate(username, 'pass')
    if token:
        run_chat_client(username)

if __name__ == '__main__':
    main()