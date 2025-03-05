#!/bin/bash

# Script para probar endpoints del webhook

# Variables de configuraciu00f3n - Editar segu00fan sea necesario
HOST="http://localhost:8000"
VERIFY_TOKEN="tu_token_de_verificacion" # Debe coincidir con WHATSAPP_VERIFY_TOKEN_WEBHOOK en .env

# Colores para la salida
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NC="\033[0m" # No Color

echo -e "${YELLOW}===== PRUEBA DE WEBHOOK DE WHATSAPP =====${NC}\n"

# Funciu00f3n para probar verificaciu00f3n GET
test_verification() {
    echo -e "${YELLOW}Probando verificaciu00f3n del webhook (GET)...${NC}"
    
    CHALLENGE="test_challenge_123"
    RESPONSE=$(curl -s "$HOST/webhook?hub.mode=subscribe&hub.verify_token=$VERIFY_TOKEN&hub.challenge=$CHALLENGE")
    
    if [ "$RESPONSE" == "$CHALLENGE" ]; then
        echo -e "${GREEN}\u2705 Verificaciu00f3n exitosa${NC}"
    else
        echo -e "${RED}\u274C Error en verificaciu00f3n${NC}"
        echo "Respuesta recibida: $RESPONSE"
    fi
    echo ""
}

# Funciu00f3n para probar mensaje de texto
test_text_message() {
    echo -e "${YELLOW}Probando mensaje de texto (POST)...${NC}"
    
    PAYLOAD='{
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "12345",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "+123456789",
                        "phone_number_id": "123456789"
                    },
                    "messages": [{
                        "from": "123456789",
                        "timestamp": "'$(date +%s)'",
                        "type": "text",
                        "text": {
                            "body": "Mensaje de prueba"
                        }
                    }]
                },
                "field": "messages"
            }]
        }]
    }'
    
    RESPONSE=$(curl -s -X POST "$HOST/webhook" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")
    
    if [[ "$RESPONSE" == *"success"* ]]; then
        echo -e "${GREEN}\u2705 Mensaje de texto procesado${NC}"
    else
        echo -e "${RED}\u274C Error al procesar mensaje de texto${NC}"
        echo "Respuesta recibida: $RESPONSE"
    fi
    echo ""
}

# Probar health check
test_health() {
    echo -e "${YELLOW}Probando health check...${NC}"
    
    RESPONSE=$(curl -s "$HOST/health")
    
    if [[ "$RESPONSE" == *"ok"* ]]; then
        echo -e "${GREEN}\u2705 Health check OK${NC}"
    else
        echo -e "${RED}\u274C Error en health check${NC}"
        echo "Respuesta recibida: $RESPONSE"
    fi
    echo ""
}

# Ejecutar todas las pruebas
test_health
test_verification
test_text_message

echo -e "${GREEN}Pruebas completadas.${NC}"
