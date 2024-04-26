import grpc
import messaging_pb2 as chat
import messaging_pb2_grpc as rpc
import threading

##Change to server nameservice when using Docker
address = 'localhost'
port = 50051

class ChatClient:
    def __init__(self,username):
        self.username = username
        # Create a channel gRPC + stub
        channel = grpc.insecure_channel(f'{address}:{port}')
        self.connection = rpc.ChatServerStub(channel)

        # Create a thread for receiving messages
        threading.Thread(target=self.receive_messages, daemon=True).start()
    
    def receive_messages(self):
        for note in self.connection.ChatStream(chat.EmptyMessage()):
            print(f'{note.name}: {note.message}')
    
    def send_message(self, message):
        if message:
            note = chat.Note(name=self.username, message=message)
            self.connection.SendNote(note)

def run_chat_client(username):
    client = ChatClient(username)
    print("😀 Conectado al servidor de chat. Escriba sus mensajes a continuación: ")

    try:
        while True:
            message = input()
            client.send_message(message)
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta pronto!")  

def main():
    username = input("Ingrese su nombre de usuario: ")
    run_chat_client(username)

if __name__ == '__main__':
    main()