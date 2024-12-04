from typing import Dict, Optional
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey

class WhatsAppMessageHandler:
    def __init__(self, connection_string: str, database_name: str = "driver_service_db", container_name: str = "messages"):
        """Initialize the WhatsApp message handler with Cosmos DB connection."""
        self.client = CosmosClient.from_connection_string(connection_string)
        self.database = self.client.get_database_client(database_name)
        self.container = self.database.get_container_client(container_name)

    def parse_whatsapp_message(self, body: Dict) -> Optional[Dict]:
        """Parse the incoming WhatsApp message and extract relevant information."""
        try:
            # Check if the message is in the correct format
            if not body.get('entry') or not body['entry'][0].get('changes'):
                return None

            # Get the message data from the webhook payload
            message_data = body['entry'][0]['changes'][0]['value']
            if not message_data.get('messages') or not message_data['messages'][0].get('text'):
                return None

            message = message_data['messages'][0]
            contact = message_data['contacts'][0] if message_data.get('contacts') else None

            return {
                'id': message['id'],  # Using message_id as the partition key
                'phone_number': message['from'],
                'timestamp': message['timestamp'],
                'message_text': message['text']['body'],
                'contact_name': contact['profile']['name'] if contact and 'profile' in contact else None,
                'raw_message': body  # Store the complete message for reference
            }
        except Exception as e:
            print(f"Error parsing WhatsApp message: {str(e)}")
            return None

    def save_message(self, message: Dict) -> bool:
        """Save the message to Cosmos DB."""
        try:
            # Add received_at timestamp
            message['received_at'] = datetime.utcnow().isoformat()
            
            # Save to Cosmos DB
            self.container.create_item(body=message)
            return True
        except Exception as e:
            print(f"Error saving message to Cosmos DB: {str(e)}")
            return False
