#!/bin/bash

# 🧪 Script para ejecutar todas las pruebas del sistema
# Ejecuta tests en diferentes modos y genera reportes

set -e  # Salir si hay errores

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║         🧪 EJECUTANDO TESTS - MUSIC CYCLING SYSTEM 🚴          ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Verificar que estamos en el directorio correcto
if [ ! -f "audio_analyzer.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra audio_analyzer.py${NC}"
    echo "   Ejecuta este script desde el directorio del proyecto"
    exit 1
fi

# Función para mostrar sección
show_section() {
    echo -e "\n${BOLD}${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════${NC}\n"
}

# Función para verificar instalación de dependencias
check_dependencies() {
    show_section "Verificando Dependencias"
    
    MISSING=()
    
    echo -e "${CYAN}📦 Verificando paquetes Python...${NC}\n"
    
    python3 -c "import librosa" 2>/dev/null || MISSING+=("librosa")
    python3 -c "import numpy" 2>/dev/null || MISSING+=("numpy")
    python3 -c "import pandas" 2>/dev/null || MISSING+=("pandas")
    python3 -c "import matplotlib" 2>/dev/null || MISSING+=("matplotlib")
    python3 -c "import scipy" 2>/dev/null || MISSING+=("scipy (opcional)")
    
    if [ ${#MISSING[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ Todas las dependencias están instaladas${NC}"
    else
        echo -e "${YELLOW}⚠️  Faltan dependencias: ${MISSING[*]}${NC}"
        echo -e "${YELLOW}   Instala con: pip install ${MISSING[*]}${NC}"
        
        read -p "¿Continuar de todos modos? (s/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            exit 1
        fi
    fi
}

# Función para generar audio de prueba
generate_test_audio() {
    show_section "Generando Audio de Prueba"
    
    if [ ! -d "mis_canciones" ] || [ -z "$(ls -A mis_canciones 2>/dev/null)" ]; then
        echo -e "${CYAN}🎵 Generando archivos de audio sintético...${NC}\n"
        python3 generar_audio_prueba.py
        
        if [ $? -eq 0 ]; then
            echo -e "\n${GREEN}✅ Audio de prueba generado${NC}"
        else
            echo -e "\n${YELLOW}⚠️  No se pudo generar audio (scipy no disponible?)${NC}"
            echo -e "${YELLOW}   Los tests continuarán con archivos existentes${NC}"
        fi
    else
        echo -e "${GREEN}✅ Ya existen archivos de audio en mis_canciones/${NC}"
        ls -lh mis_canciones/ | grep -E "\.(mp3|wav|flac)" | wc -l | xargs -I {} echo "   Archivos encontrados: {}"
    fi
}

# Función para ejecutar tests de sistema
run_system_tests() {
    show_section "Tests de Sistema (Integración Completa)"
    
    echo -e "${CYAN}🧪 Ejecutando test_system.py...${NC}\n"
    
    if [ "$1" == "quick" ]; then
        python3 test_system.py --quick
    else
        python3 test_system.py
    fi
    
    SYSTEM_RESULT=$?
    
    if [ $SYSTEM_RESULT -eq 0 ]; then
        echo -e "\n${GREEN}✅ Tests de sistema completados exitosamente${NC}"
    else
        echo -e "\n${RED}❌ Algunos tests de sistema fallaron${NC}"
    fi
    
    return $SYSTEM_RESULT
}

# Función para ejecutar tests unitarios
run_unit_tests() {
    show_section "Tests Unitarios (unittest)"
    
    echo -e "${CYAN}🧪 Ejecutando test_units.py...${NC}\n"
    
    if [ "$1" == "coverage" ]; then
        python3 test_units.py --coverage
    else
        python3 -m unittest test_units -v
    fi
    
    UNIT_RESULT=$?
    
    if [ $UNIT_RESULT -eq 0 ]; then
        echo -e "\n${GREEN}✅ Tests unitarios completados exitosamente${NC}"
    else
        echo -e "\n${RED}❌ Algunos tests unitarios fallaron${NC}"
    fi
    
    return $UNIT_RESULT
}

# Función para ejecutar ejemplos
run_examples() {
    show_section "Ejecutando Ejemplos"
    
    echo -e "${CYAN}📚 Ejecutando ejemplos.py...${NC}\n"
    
    if [ -f "ejemplos.py" ]; then
        python3 ejemplos.py
        
        if [ $? -eq 0 ]; then
            echo -e "\n${GREEN}✅ Ejemplos ejecutados correctamente${NC}"
            return 0
        else
            echo -e "\n${YELLOW}⚠️  Los ejemplos tuvieron algunos problemas${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  No se encuentra ejemplos.py${NC}"
        return 0
    fi
}

# Función para mostrar archivos generados
show_generated_files() {
    show_section "Archivos Generados"
    
    echo -e "${CYAN}📁 Archivos de salida:${NC}\n"
    
    FILES=(
        "song_analysis.csv:Análisis de canciones"
        "workout_playlist.csv:Playlist generada"
        "workout_playlist.m3u:Archivo M3U"
        "playlist_visualization.png:Visualización"
    )
    
    for entry in "${FILES[@]}"; do
        IFS=':' read -r file desc <<< "$entry"
        if [ -f "$file" ]; then
            size=$(ls -lh "$file" | awk '{print $5}')
            echo -e "  ${GREEN}✓${NC} $desc"
            echo -e "    └─ $file ($size)"
        else
            echo -e "  ${YELLOW}○${NC} $desc"
            echo -e "    └─ $file (no generado)"
        fi
    done
}

# Función para limpiar archivos temporales
cleanup() {
    show_section "Limpieza"
    
    echo -e "${CYAN}🧹 Limpiando archivos temporales...${NC}\n"
    
    rm -f test_*.csv test_*.m3u test_*.png
    rm -f playlist_visualization.png
    
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

# Función para mostrar resumen final
show_summary() {
    local system_result=$1
    local unit_result=$2
    
    show_section "RESUMEN FINAL"
    
    echo -e "${BOLD}Resultados:${NC}\n"
    
    if [ $system_result -eq 0 ]; then
        echo -e "  ${GREEN}✅ Tests de Sistema: PASS${NC}"
    else
        echo -e "  ${RED}❌ Tests de Sistema: FAIL${NC}"
    fi
    
    if [ $unit_result -eq 0 ]; then
        echo -e "  ${GREEN}✅ Tests Unitarios: PASS${NC}"
    else
        echo -e "  ${RED}❌ Tests Unitarios: FAIL${NC}"
    fi
    
    echo ""
    
    if [ $system_result -eq 0 ] && [ $unit_result -eq 0 ]; then
        echo -e "${GREEN}${BOLD}🎉 TODOS LOS TESTS PASARON 🎉${NC}\n"
        return 0
    else
        echo -e "${RED}${BOLD}❌ ALGUNOS TESTS FALLARON${NC}\n"
        echo -e "${YELLOW}Revisa los logs arriba para más detalles${NC}\n"
        return 1
    fi
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    local MODE="${1:-full}"
    
    case $MODE in
        quick)
            echo -e "${YELLOW}ℹ️  Modo QUICK - tests rápidos solamente${NC}\n"
            check_dependencies
            generate_test_audio
            run_system_tests quick
            SYSTEM_RESULT=$?
            run_unit_tests
            UNIT_RESULT=$?
            ;;
            
        coverage)
            echo -e "${CYAN}ℹ️  Modo COVERAGE - con análisis de cobertura${NC}\n"
            check_dependencies
            generate_test_audio
            run_system_tests
            SYSTEM_RESULT=$?
            run_unit_tests coverage
            UNIT_RESULT=$?
            ;;
            
        examples)
            echo -e "${BLUE}ℹ️  Modo EXAMPLES - solo ejemplos${NC}\n"
            check_dependencies
            generate_test_audio
            run_examples
            exit $?
            ;;
            
        clean)
            cleanup
            exit 0
            ;;
            
        full|*)
            echo -e "${CYAN}ℹ️  Modo FULL - todos los tests${NC}\n"
            check_dependencies
            generate_test_audio
            run_system_tests
            SYSTEM_RESULT=$?
            run_unit_tests
            UNIT_RESULT=$?
            run_examples
            ;;
    esac
    
    show_generated_files
    show_summary $SYSTEM_RESULT $UNIT_RESULT
    
    return $?
}

# Mostrar ayuda si se solicita
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo -e "${BOLD}Uso:${NC} $0 [modo]"
    echo ""
    echo -e "${BOLD}Modos disponibles:${NC}"
    echo "  full       - Ejecuta todos los tests (por defecto)"
    echo "  quick      - Ejecuta solo tests rápidos"
    echo "  coverage   - Ejecuta tests con análisis de cobertura"
    echo "  examples   - Ejecuta solo los ejemplos"
    echo "  clean      - Limpia archivos temporales"
    echo ""
    echo -e "${BOLD}Ejemplos:${NC}"
    echo "  $0              # Tests completos"
    echo "  $0 quick        # Tests rápidos"
    echo "  $0 coverage     # Con cobertura de código"
    echo "  $0 clean        # Limpiar archivos"
    echo ""
    exit 0
fi

# Ejecutar
main "$@"
exit $?
