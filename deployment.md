# Guía de Despliegue en Azure

## Prerrequisitos

1. Azure CLI instalado
2. Suscripción de Azure activa
3. Recursos necesarios en Azure:
   - Resource Group
   - Azure Function App (Python)
   - Cosmos DB
   - Application Insights

## Pasos para el Despliegue

### 1. Crear Recursos en Azure

```bash
# Variables
RESOURCE_GROUP="whatsapp-driver-rg"
LOCATION="eastus"
STORAGE_NAME="whatsappdriverstore"
FUNCTION_APP_NAME="whatsapp-driver-func"
COSMOS_DB_ACCOUNT="whatsapp-driver-cosmos"

# Crear Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Crear Storage Account
az storage account create \
  --name $STORAGE_NAME \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --sku Standard_LRS

# Crear Cosmos DB
az cosmosdb create \
  --name $COSMOS_DB_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --kind MongoDB \
  --capabilities EnableMongo

# Crear Function App
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name $FUNCTION_APP_NAME \
  --os-type linux \
  --storage-account $STORAGE_NAME
```

### 2. Configurar Variables de Entorno

```bash
# Obtener cadena de conexión de Cosmos DB
COSMOS_CONNECTION_STRING=$(az cosmosdb keys list \
  --name $COSMOS_DB_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --type connection-strings \
  --query connectionStrings[0].connectionString \
  --output tsv)

# Configurar variables de entorno en Function App
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    COSMOSDB_CONNECTION_STRING=$COSMOS_CONNECTION_STRING \
    COSMOSDB_DATABASE="driver_service_db" \
    ENVIRONMENT="production"
```

### 3. Desplegar el Código

```bash
# Desde el directorio del proyecto
func azure functionapp publish $FUNCTION_APP_NAME
```

## Verificación Post-Despliegue

1. Verificar el estado del despliegue:
```bash
az functionapp show \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP
```

2. Obtener la URL de la función:
```bash
az functionapp function show \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --function-name WhatsAppWebhook \
  --query "invokeUrlTemplate" \
  --output tsv
```

## Monitoreo

1. Ver logs en tiempo real:
```bash
az webapp log tail \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP
```

2. Configurar Application Insights para monitoreo detallado desde el portal de Azure.

## Mantenimiento

1. Actualizar la función:
```bash
func azure functionapp publish $FUNCTION_APP_NAME
```

2. Escalar según sea necesario:
```bash
az functionapp plan update \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --max-burst 4
```
