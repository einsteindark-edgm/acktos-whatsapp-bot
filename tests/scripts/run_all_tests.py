import os
import sys
import subprocess

def run_test(test_script, description):
    print(f"\n{'='*80}")
    print(f"Ejecutando {description}...")
    print(f"{'='*80}")
    
    result = subprocess.run(
        [sys.executable, test_script],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode == 0:
        print(f"\n[PASS] {description} completado con éxito!")
        return True
    else:
        print(f"\n[FAIL] {description} falló!")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return False

def main():
    print("Ejecutando todas las pruebas...")
    
    # Activar entorno virtual
    os.environ['OPENAI_API_KEY'] = 'dummy_key'
    
    # Lista de pruebas a ejecutar
    tests = [
        ("../manual/check_deps.py", "Verificación de dependencias"),
        ("../manual/mock_test.py", "Prueba de mocks y dependencias"),
        ("../manual/test_extraction_agent.py", "Prueba del agente de extracción de datos"),
        ("../manual/test_vision_agent.py", "Prueba del agente de visión"),
        ("../manual/test_storage_agent.py", "Prueba del agente de almacenamiento"),
        ("../integration/test_vision_extraction_e2e.py", "Prueba end-to-end de visión y extracción"),
        ("../app/routers/test_webhook.py", "Prueba del webhook de FastAPI")
    ]
    
    # Ejecutar todas las pruebas
    results = []
    for test_script, description in tests:
        success = run_test(test_script, description)
        results.append((test_script, success))
    
    # Mostrar resumen
    print(f"\n{'='*80}")
    print("Resumen de pruebas:")
    print(f"{'='*80}")
    
    all_passed = True
    for test_script, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status}: {test_script}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n[PASS] Todas las pruebas pasaron correctamente!")
        return 0
    else:
        print("\n[FAIL] Algunas pruebas fallaron!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar las pruebas: {e}")
        sys.exit(1)
