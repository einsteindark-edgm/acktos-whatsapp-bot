import os
import sys
import subprocess

def check_module_available(module_name):
    """Comprueba si un módulo está disponible para importar"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def run_test(test_script, description, required_modules=None):
    print(f"\n{'='*80}")
    print(f"Ejecutando {description}...")
    print(f"{'='*80}")
    
    # Verificar que los módulos requeridos estén disponibles
    if required_modules:
        missing_modules = []
        for module in required_modules:
            if not check_module_available(module):
                missing_modules.append(module)
        
        if missing_modules:
            print(f"\n[SKIP] No se puede ejecutar {description} debido a módulos faltantes: {', '.join(missing_modules)}")
            print(f"Instale los módulos faltantes con: pip install {' '.join(missing_modules)}")
            return None  # Indicar que la prueba se omitió
    
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
    
    # Obtener la ruta base del proyecto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))  # Sube 2 niveles desde scripts/ a la raíz
    
    # Lista de pruebas a ejecutar con rutas absolutas y sus dependencias
    tests = [
        # Pruebas manuales
        (os.path.join(base_dir, "tests", "manual", "check_deps.py"), "Verificación de dependencias", []),
        (os.path.join(base_dir, "tests", "manual", "mock_test.py"), "Prueba de mocks y dependencias", []),
        (os.path.join(base_dir, "tests", "manual", "test_extraction_agent.py"), "Prueba del agente de extracción de datos", []),
        (os.path.join(base_dir, "tests", "manual", "test_manual_vision_agent.py"), "Prueba del agente de visión", []),
        (os.path.join(base_dir, "tests", "manual", "test_storage_agent.py"), "Prueba del agente de almacenamiento", []),
        
        # Pruebas de integración
        (os.path.join(base_dir, "tests", "integration", "test_vision_extraction_e2e.py"), "Prueba end-to-end de visión y extracción", []),
        (os.path.join(base_dir, "tests", "app", "routers", "test_webhook.py"), "Prueba del webhook de FastAPI", ["fastapi"]),
        
        # Pruebas específicas de agentes (usadas también por CI)
        (os.path.join(base_dir, "tests", "agents", "test_agent_vision.py"), "Prueba específica del agente de visión", ["pydantic_ai"]),
        
        # Pruebas unitarias
        (os.path.join(base_dir, "tests", "unit", "agents", "test_vision_agent.py"), "Prueba unitaria del agente de visión", ["pydantic_ai"])
    ]
    
    # Ejecutar todas las pruebas
    results = []
    for test_script, description, required_modules in tests:
        result = run_test(test_script, description, required_modules)
        results.append((test_script, result))
    
    # Mostrar resumen
    print(f"\n{'='*80}")
    print("Resumen de pruebas:")
    print(f"{'='*80}")
    
    all_passed = True
    any_failed = False
    
    for test_script, result in results:
        if result is None:
            status = "[SKIP]"
        elif result is True:
            status = "[PASS]"
        else:  # False
            status = "[FAIL]"
            any_failed = True
            all_passed = False
        
        print(f"{status}: {test_script}")
    
    if all_passed:
        print("\n[PASS] Todas las pruebas pasaron correctamente!")
        return 0
    elif any_failed:
        print("\n[FAIL] Algunas pruebas fallaron!")
        return 1
    else:
        print("\n[WARNING] Algunas pruebas fueron omitidas debido a dependencias faltantes")
        return 0  # No consideramos que sea un error si las pruebas se omitieron intencionalmente

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar las pruebas: {e}")
        sys.exit(1)
