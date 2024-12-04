from message_handler import WhatsAppMessageHandler
import json

def test_message_parsing():
    # Crear una instancia del handler
    handler = WhatsAppMessageHandler()
    
    # Mensaje de prueba
    test_message = """*RECOGIDA 3:30AM*
3124432509    80795588 - DAVID ANDRES BLANCO GUTIERREZ
DG 72F SUR # 33-64   ARBORIZADORA ALTA"""

    # Probar el parsing
    result = handler.extract_service_details(test_message)
    
    # Imprimir resultados
    print("Resultados del parsing:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_message_parsing()
