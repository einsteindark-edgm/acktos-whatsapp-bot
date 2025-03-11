#!/bin/bash

# Script para eliminar los archivos de prueba originales de la raíz del proyecto
# después de haberlos migrado a la estructura de carpetas adecuada

ROOT_DIR="/Users/edgm/CascadeProjects/whatsapp-driver-service"

echo "Eliminando archivos de prueba de la raíz del proyecto..."

# Archivos Python de prueba
TEST_FILES=(
    "check_deps.py"
    "mock_test.py"
    "run_all_tests.py"
    "run_tests.py"
    "simple_test.py"
    "test_agents.py"
    "test_extraction_agent.py"
    "test_storage_agent.py"
    "test_vision_agent.py"
    "test_vision_extraction_e2e.py"
    "test_with_testmodel.py"
)

# Scripts Shell de prueba
SHELL_SCRIPTS=(
    "test.sh"
    "test_fastapi.sh"
    "test_webhook.sh"
)

# Verificar que cada archivo existe en su nueva ubicación antes de eliminarlo
echo "Verificando que todos los archivos se hayan copiado correctamente..."

ALL_COPIED=true

# Verificar archivos Python
for file in "${TEST_FILES[@]}"; do
    if [[ "$file" == "check_deps.py" || "$file" == "mock_test.py" || "$file" == "simple_test.py" || 
          "$file" == "test_extraction_agent.py" || "$file" == "test_storage_agent.py" || 
          "$file" == "test_vision_agent.py" || "$file" == "test_with_testmodel.py" ]]; then
        if [ ! -f "$ROOT_DIR/tests/manual/$file" ]; then
            echo "❌ Error: $file no se encuentra en tests/manual/"
            ALL_COPIED=false
        fi
    elif [[ "$file" == "test_agents.py" || "$file" == "test_vision_extraction_e2e.py" ]]; then
        if [ ! -f "$ROOT_DIR/tests/integration/$file" ]; then
            echo "❌ Error: $file no se encuentra en tests/integration/"
            ALL_COPIED=false
        fi
    elif [[ "$file" == "run_all_tests.py" || "$file" == "run_tests.py" ]]; then
        if [ ! -f "$ROOT_DIR/tests/scripts/$file" ]; then
            echo "❌ Error: $file no se encuentra en tests/scripts/"
            ALL_COPIED=false
        fi
    fi
done

# Verificar scripts Shell
for script in "${SHELL_SCRIPTS[@]}"; do
    if [ ! -f "$ROOT_DIR/tests/scripts/$script" ]; then
        echo "❌ Error: $script no se encuentra en tests/scripts/"
        ALL_COPIED=false
    fi
done

# Proceder con la eliminación solo si todos los archivos se copiaron correctamente
if [ "$ALL_COPIED" = true ]; then
    echo "✅ Todos los archivos se copiaron correctamente. Procediendo con la eliminación..."
    
    # Eliminar archivos Python
    for file in "${TEST_FILES[@]}"; do
        if [ -f "$ROOT_DIR/$file" ]; then
            rm "$ROOT_DIR/$file"
            echo "✓ Eliminado: $file"
        else
            echo "⚠️ Advertencia: $file no existe en la raíz"
        fi
    done
    
    # Eliminar scripts Shell
    for script in "${SHELL_SCRIPTS[@]}"; do
        if [ -f "$ROOT_DIR/$script" ]; then
            rm "$ROOT_DIR/$script"
            echo "✓ Eliminado: $script"
        else
            echo "⚠️ Advertencia: $script no existe en la raíz"
        fi
    done
    
    echo "\n✅ Limpieza completada con éxito! La raíz del proyecto ahora está ordenada."
else
    echo "\n❌ No se eliminaron archivos porque algunos no se copiaron correctamente."
    echo "Por favor, verifica manualmente los archivos faltantes."
fi
