# WhatsApp Driver Service

This project implements a WhatsApp message processing system for driver services using Azure Functions. The system verifies driver registration and processes service requests accordingly.

## Features

- WhatsApp message integration
- Driver registration verification
- Service request processing
- Unregistered attempt logging
- Dual database support (Cosmos DB for production, MongoDB for development)

## Prerequisites

- Python 3.8 or higher
- Azure Functions Core Tools
- MongoDB (for local development)
- Azure Cosmos DB account (for production)
- Azure subscription
- VSCode with Azure Functions extension

## Local Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start MongoDB locally:
```bash
mongod
```

3. Configure local.settings.json with appropriate connection strings.

4. Start the function app locally:
```bash
func start
```

## Project Structure

- `function_app.py`: Main Azure Function app with webhook endpoint
- `database.py`: Database management for both Cosmos DB and MongoDB
- `message_handler.py`: WhatsApp message parsing and processing
- `requirements.txt`: Project dependencies
- `local.settings.json`: Local development settings

## Database Schema

### Drivers Collection
```json
{
    "id": "string",
    "phone_number": "string",
    "name": "string",
    "registration_date": "datetime",
    "status": "string"
}
```

### Service Requests Collection
```json
{
    "id": "string",
    "driver_id": "string",
    "message_id": "string",
    "phone_number": "string",
    "timestamp": "datetime",
    "message_text": "string",
    "parsed_data": "object"
}
```

### Unregistered Attempts Collection
```json
{
    "id": "string",
    "phone_number": "string",
    "timestamp": "datetime",
    "message_text": "string",
    "status": "string"
}
```

## Deployment

1. Create an Azure Function App resource
2. Configure application settings with production values
3. Deploy using Azure Functions extension in VSCode or Azure CLI

## Testing

1. Use the local MongoDB instance for development testing
2. Send test WhatsApp messages to verify functionality
3. Monitor logs for proper message processing
