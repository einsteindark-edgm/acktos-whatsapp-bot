from pymongo import MongoClient
import os
from datetime import datetime

def init_mongodb():
    # Conectar a MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    
    # Crear o acceder a la base de datos
    db_name = 'driver_service_db'
    db = client[db_name]
    
    # Eliminar colecciones existentes si existen
    db.drivers.drop()
    db.service_requests.drop()
    db.unregistered_attempts.drop()
    
    # Crear colecciones con validación de esquema
    db.create_collection('drivers')
    db.create_collection('service_requests')
    db.create_collection('unregistered_attempts')
    
    # Crear índices
    db.drivers.create_index('phone_number', unique=True)
    db.service_requests.create_index('driver_id')
    db.service_requests.create_index('timestamp')
    db.unregistered_attempts.create_index('phone_number')
    db.unregistered_attempts.create_index('timestamp')
    
    # Insertar algunos conductores de prueba
    test_drivers = [
        {
            'phone_number': '573118878806',
            'name': 'David Andres Blanco',
            'registration_date': datetime.utcnow(),
            'status': 'active'
        },
        {
            'phone_number': '573124432509',
            'name': 'Samuel De La Hoz',
            'registration_date': datetime.utcnow(),
            'status': 'active'
        }
    ]
    
    db.drivers.insert_many(test_drivers)
    
    print(f"Base de datos '{db_name}' inicializada con éxito")
    print("Colecciones creadas:")
    print("- drivers")
    print("- service_requests")
    print("- unregistered_attempts")
    print(f"\nConductores de prueba insertados: {len(test_drivers)}")

if __name__ == '__main__':
    init_mongodb()
