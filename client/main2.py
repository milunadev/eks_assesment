import grpc
import threading

import messaging_pb2_grpc as rpc
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_socketio import join_room, leave_room


app = Flask(__name__)
app.secret_key = 'mysecretkey'
socketio = SocketIO(app)
server_url = os.getenv('SERVER_URL', 'localhost:50051')


class AuthClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(server_url)
        self.stub = rpc.AuthServiceStub(self.channel)

    def authenticate(self, username, password):
        import messaging_pb2 as chat
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
        channel = grpc.insecure_channel(f'{server_url}')
        self.stub = rpc.ChatServerStub(channel)
        # Create a thread for receiving messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        import messaging_pb2 as chat
        metadata = [('authorization', f'Bearer {self.token}')]
        try:
            for note in self.stub.ChatStream(chat.EmptyMessage(),metadata=metadata):
                message = f'{note.name}: {note.message}'
                print("📨 RECIBIDO:",  message)
                # Emitir el mensaje a todos los usuarios conectados a través de SocketIO
                socketio.emit('new_message', {'message': message}, room=self.username, namespace='/chat')
        except Exception as e:
            print(f"Error al recibir mensaje:: {str(e)} ")
    
    def send_message(self, message):
        import messaging_pb2 as chat
        if message:
            note = chat.Note(name=self.username, message=message)
            metadata = [('authorization', f'Bearer {self.token}')]
            self.stub.SendNote(note,metadata=metadata)
            print(" 🚀ENVIADO: ", message)
    
    def save_chat(self, messages, token):
        import messaging_pb2 as chat
        def generate_messages():
            for msg in messages:
                if ": " in msg:
                    username, message = msg.split(": ", 1)
                    print(f"Enviando mensaje: {username}, {message}")
                    yield chat.ChatMessage(username=username, message=message, date='2021-01-01')

        metadata = [('authorization', f'Bearer {token}')]
        try:
            responses = self.stub.SaveChat(generate_messages(), metadata=metadata)
            for response in responses:
                print(f'Mensaje guardado: {response}')
        except grpc.RpcError as e:
            print(f"Error al guardar chat: {str(e)}")
            return False

        return True

clients = {} 
chat_histories = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        # Llamada al servicio de autenticación
        auth_client = AuthClient()
        token = auth_client.authenticate(username, password)
        #print(f'{username}:{token}')

        if token:
            session['username'] = username
            session['token'] = token
            return redirect(url_for('options'))
        else:
            return render_template('index.html', error="Error de autenticación")
    return render_template('index.html')

@app.route('/options', methods=['GET', 'POST'])
def options():
    print(session)
    username = session.get('username')
    if username:
        token = session.get('token')
        return render_template('options.html', username=username)
    else: 
        return redirect(url_for('index'))

@app.route('/livechat', methods=['GET', 'POST'])
def chat():
    username = session.get('username')
    token = session.get('token')
    if not username or not token:
        return redirect(url_for('index'))

    # Verificar si el usuario ya tiene una instancia de ChatClient
    if username not in clients:
        clients[username] = ChatClient(username, token)

    if request.method == 'POST':
        message = request.form['message']
        clients[username].send_message(message)

    return render_template('chat.html', username=username)

@app.route('/search', methods=['GET'])
def search():
    print(session)
    # Aquí puedes agregar la lógica para buscar chats
    if 'username' in session:
        # Plantilla simple como marcador de posición
        return render_template('search_chats.html')
    else:
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    username = session.pop('username', None)
    token = session.get('token')
    if username and token in clients:
        del clients[username]
    return redirect(url_for('index'))


@socketio.on('save_chat', namespace='/chat')
def handle_save_chat(data, extra):
    username = session.get('username')
    if not username:
        print("Usuario no autenticado.")
        return False  
    print("Recibido:", data)
    messages = data['messages']
    if not messages:
        print("No hay mensajes para guardar.")
        return False

    chat_client = clients.get(username)
    if chat_client:
        token = session.get('token')
        if chat_client.save_chat(messages, token):  # Pasar el token al método save_chat
            return True
        else:
            print("Fallo al guardar los mensajes.")
            return False
    else:
        print("El usuario no tiene una instancia de ChatClient.")
        return False


@socketio.on('connect', namespace='/chat')
def on_connect():
    username = session.get('username')
    if username:
        join_room(username)
        emit('status', {'msg': f'{username} has entered the chat.'}, room=username)

@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    username = session.get('username')
    if username:
        leave_room(username)
        emit('status', {'msg': f'{username} has left the chat.'}, room=username)
        if username in clients:
            del clients[username]


@socketio.on('send_message', namespace='/chat')
def handle_message(data, extra):
    username = session.get('username')
    if not username:
        print("Usuario no autenticado.")
        return False  # Asegúrate de que el usuario está autenticado
    message = data['message']
    note={'username': username, 'message': message}

    if username in clients:
        clients[username].send_message(message)

    if username in chat_histories:
        chat_histories[username].append(note)
    else:
        chat_histories[username] = [note]

    emit('new_message', {'name': username, 'message': message}, room=username)
    print("Mensaje enviado por", username, ":", message)
    

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True,host='0.0.0.0', port=5000)
