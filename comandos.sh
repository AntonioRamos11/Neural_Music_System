#!/bin/bash
# 🎵 Script de comandos útiles para el Cycling Music Mixer

echo "🎵 CYCLING MUSIC MIXER - Comandos Útiles"
echo "=========================================="
echo ""

# Función para mostrar menú
mostrar_menu() {
    echo "Selecciona una opción:"
    echo ""
    echo "  1) 🔧 Instalar dependencias"
    echo "  2) 🎵 Generar audio de prueba"
    echo "  3) 🚀 Ejecutar análisis y generar playlist"
    echo "  4) 📊 Ver visualización de playlist"
    echo "  5) 🎨 Generar múltiples playlists"
    echo "  6) 📈 Ver estadísticas de biblioteca"
    echo "  7) 🗑️  Limpiar archivos de prueba"
    echo "  8) 🧹 Limpiar todos los archivos generados"
    echo "  9) ❓ Ver ayuda"
    echo "  0) 🚪 Salir"
    echo ""
    read -p "Opción: " opcion
    echo ""
}

# Opciones
case "${1}" in
    install)
        echo "🔧 Instalando dependencias..."
        pip install -r requirements.txt
        echo "✅ Instalación completa"
        ;;
    
    demo)
        echo "🎵 Generando audio de prueba..."
        python generar_audio_prueba.py
        echo ""
        echo "🚀 Ejecutando análisis..."
        python main.py
        ;;
    
    run)
        echo "🚀 Ejecutando análisis y generación de playlist..."
        python main.py
        ;;
    
    viz)
        echo "📊 Generando visualización..."
        python visualize.py
        ;;
    
    all)
        echo "🎨 Generando múltiples playlists..."
        python ejemplos.py
        ;;
    
    stats)
        echo "📈 Mostrando estadísticas..."
        python ejemplos.py stats
        ;;
    
    clean)
        echo "🗑️  Limpiando archivos de prueba..."
        python generar_audio_prueba.py clean
        ;;
    
    reset)
        echo "🧹 Limpiando archivos generados..."
        rm -f song_analysis.csv
        rm -f workout_playlist.csv
        rm -f workout_playlist.m3u
        rm -f playlist_*.csv
        rm -f playlist_visualization.png
        echo "✅ Archivos eliminados"
        ;;
    
    help|--help|-h)
        echo "🎵 Cycling Music Mixer - Ayuda"
        echo ""
        echo "Comandos disponibles:"
        echo ""
        echo "  ./comandos.sh install    - Instalar dependencias"
        echo "  ./comandos.sh demo       - Demo completo (genera audio + playlist)"
        echo "  ./comandos.sh run        - Analizar música y generar playlist"
        echo "  ./comandos.sh viz        - Ver visualización"
        echo "  ./comandos.sh all        - Generar múltiples playlists"
        echo "  ./comandos.sh stats      - Ver estadísticas de biblioteca"
        echo "  ./comandos.sh clean      - Limpiar archivos de prueba"
        echo "  ./comandos.sh reset      - Limpiar archivos generados"
        echo "  ./comandos.sh help       - Esta ayuda"
        echo ""
        echo "Uso rápido:"
        echo "  1. ./comandos.sh install"
        echo "  2. Copia tus MP3s a mis_canciones/"
        echo "  3. ./comandos.sh run"
        echo "  4. ./comandos.sh viz"
        echo ""
        ;;
    
    *)
        # Modo interactivo
        while true; do
            mostrar_menu
            
            case $opcion in
                1)
                    pip install -r requirements.txt
                    echo "✅ Instalación completa"
                    ;;
                2)
                    python generar_audio_prueba.py
                    ;;
                3)
                    python main.py
                    ;;
                4)
                    python visualize.py
                    ;;
                5)
                    python ejemplos.py
                    ;;
                6)
                    python ejemplos.py stats
                    ;;
                7)
                    python generar_audio_prueba.py clean
                    ;;
                8)
                    rm -f song_analysis.csv workout_playlist.csv workout_playlist.m3u
                    rm -f playlist_*.csv playlist_visualization.png
                    echo "✅ Archivos eliminados"
                    ;;
                9)
                    cat QUICKSTART.md
                    ;;
                0)
                    echo "👋 ¡Hasta luego!"
                    exit 0
                    ;;
                *)
                    echo "❌ Opción inválida"
                    ;;
            esac
            
            echo ""
            read -p "Presiona Enter para continuar..."
            clear
        done
        ;;
esac
