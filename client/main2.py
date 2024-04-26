import grpc
import threading

import messaging_pb2_grpc as rpc
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'mysecretkey'
socketio = SocketIO(app)

server_url = os.getenv('SERVER_URL', 'localhost:50051')

class ChatClient:
    def __init__(self, username):
        self.username = username
        # Create a channel gRPC + stub
        channel = grpc.insecure_channel(f'{server_url}')
        self.connection = rpc.ChatServerStub(channel)
        # Create a thread for receiving messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        import messaging_pb2 as chat
        try:
            for note in self.connection.ChatStream(chat.EmptyMessage()):
                message = f'{note.name}: {note.message}'
                print("📨 RECIBIDO:",  message)
                # Emitir el mensaje a todos los usuarios conectados a través de SocketIO
                socketio.emit('new_message', {'message': message}, namespace='/chat')
        except Exception as e:
            print(f"Error al recibir mensaje:: {str(e)} ")
    
    def send_message(self, message):
        import messaging_pb2 as chat
        if message:
            note = chat.Note(name=self.username, message=message)
            self.connection.SendNote(note)
            print(" 🚀ENVIADO: ", message)

clients = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form["username"]
        if username not in clients:
            clients[username] = ChatClient(username)
        session['username'] = username
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    username = session.get('username')
    if not username:
        return redirect(url_for('index'))

    if request.method == 'POST':
        message = request.form['message']
        clients[username].send_message(message)

    return render_template('chat.html', username=username)

@socketio.on('send_message', namespace='/chat')
def handle_message(data,extra):
    username = session.get('username')
    if not username:
        print("Usuario no autenticado.")
        return False  # Asegúrate de que el usuario está autenticado
    message = data['message']
    if username in clients:
        clients[username].send_message(message)
        print("Mensaje enviado por", username, ":", message)
    else:
        print("Usuario no encontrado.")

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True,host='0.0.0.0', port=5000)
