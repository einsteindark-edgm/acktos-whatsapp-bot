import os
from typing import Dict, Optional
from azure.cosmos import CosmosClient
from pymongo import MongoClient
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
        if self.is_production:
            cosmos_connection = os.getenv('COSMOSDB_CONNECTION_STRING')
            self.cosmos_client = CosmosClient.from_connection_string(cosmos_connection)
            self.db = self.cosmos_client.get_database_client(os.getenv('COSMOSDB_DATABASE'))
            self.drivers_container = self.db.get_container_client('drivers')
            self.service_requests_container = self.db.get_container_client('service_requests')
            self.unregistered_attempts_container = self.db.get_container_client('unregistered_attempts')
        else:
            mongo_connection = os.getenv('MONGODB_CONNECTION_STRING')
            self.mongo_client = MongoClient(mongo_connection)
            self.db = self.mongo_client[os.getenv('MONGODB_DATABASE')]
            self.drivers_collection = self.db['drivers']
            self.service_requests_collection = self.db['service_requests']
            self.unregistered_attempts_collection = self.db['unregistered_attempts']

    async def check_driver_registration(self, phone_number: str) -> Optional[Dict]:
        """Check if a driver is registered based on their phone number."""
        if self.is_production:
            query = f"SELECT * FROM c WHERE c.phone_number = '{phone_number}'"
            items = list(self.drivers_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return items[0] if items else None
        else:
            return self.drivers_collection.find_one({"phone_number": phone_number})

    async def save_service_request(self, request_data: Dict) -> Dict:
        """Save a service request from a registered driver."""
        request_data['timestamp'] = datetime.utcnow().isoformat()
        if self.is_production:
            return self.service_requests_container.create_item(body=request_data)
        else:
            result = self.service_requests_collection.insert_one(request_data)
            request_data['_id'] = str(result.inserted_id)
            return request_data

    async def log_unregistered_attempt(self, attempt_data: Dict) -> Dict:
        """Log an attempt from an unregistered phone number."""
        attempt_data['timestamp'] = datetime.utcnow().isoformat()
        if self.is_production:
            return self.unregistered_attempts_container.create_item(body=attempt_data)
        else:
            result = self.unregistered_attempts_collection.insert_one(attempt_data)
            attempt_data['_id'] = str(result.inserted_id)
            return attempt_data
