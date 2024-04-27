from pymongo import MongoClient

# Configuración de conexión
MONGO_URI = 'mongodb://mongodb:27017/'
COLLECTION_NAME = 'users'

# Datos iniciales
initial_data = [
    {'username': 'mimi', 'password': 'pass'},
    {'username': 'juan', 'password': 'pass'},
    # Añade más datos según sea necesario
]

# Conectar a MongoDB
client = MongoClient(MONGO_URI)
db = client['mydatabase']

# Verificar si la colección ya existe y tiene datos
collection = db[COLLECTION_NAME]
if collection.count_documents({}) == 0:
    # Insertar datos iniciales si la colección está vacía
    collection.insert_many(initial_data)
    print("Datos iniciales agregados a MongoDB.")
else:
    print("La colección ya existe y contiene datos.")

# Cerrar la conexión
client.close()
