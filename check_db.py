from pymongo import MongoClient
import json
from bson import json_util

def check_database():
    # Conectar a MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['driver_service_db']
    
    # Verificar conductores registrados
    print("\n=== Conductores Registrados ===")
    drivers = list(db.drivers.find())
    for driver in drivers:
        print(json.dumps(json.loads(json_util.dumps(driver)), indent=2))
    
    # Verificar solicitudes de servicio
    print("\n=== Solicitudes de Servicio ===")
    requests = list(db.service_requests.find())
    for request in requests:
        print(json.dumps(json.loads(json_util.dumps(request)), indent=2))
    
    # Verificar intentos no registrados
    print("\n=== Intentos No Registrados ===")
    attempts = list(db.unregistered_attempts.find())
    for attempt in attempts:
        print(json.dumps(json.loads(json_util.dumps(attempt)), indent=2))

if __name__ == '__main__':
    check_database()
