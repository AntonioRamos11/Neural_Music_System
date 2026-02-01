#!/bin/bash

# 🎵 Script para preparar MicroSD para bocinas con música de ciclismo
# Uso: sudo ./preparar_microsd_ciclismo.sh /dev/sdX1

set -e

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
echo "║         🎵 PREPARADOR DE MICROSD PARA CICLISMO 🚴               ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Este script debe ejecutarse como root${NC}"
    echo "   Usa: sudo $0 /dev/sdX1"
    exit 1
fi

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Error: Debes especificar el dispositivo${NC}"
    echo ""
    echo -e "${YELLOW}Dispositivos disponibles:${NC}"
    lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | grep -E "disk|part"
    echo ""
    echo -e "${CYAN}Uso:${NC}"
    echo "  # Ver dispositivos disponibles"
    echo "  lsblk"
    echo ""
    echo "  # Preparar la microSD (cambia sdX1 por tu dispositivo)"
    echo "  sudo ./preparar_microsd_ciclismo.sh /dev/sdb1"
    exit 1
fi

DEVICE=$1
MOUNT_POINT="/tmp/cycling_sd"
PLAYLIST_DIR="playlists"
CSV_DIR="csv"

# Verificar que el dispositivo existe
if [ ! -b "$DEVICE" ]; then
    echo -e "${RED}❌ Error: $DEVICE no existe o no es un dispositivo de bloques${NC}"
    exit 1
fi

# Advertencia
echo -e "${YELLOW}⚠️  ADVERTENCIA:${NC}"
echo "   Dispositivo: $DEVICE"
echo "   Se formateará y perderán TODOS los datos"
echo ""
read -p "¿Continuar? (escribe 'SI' en mayúsculas): " confirm

if [ "$confirm" != "SI" ]; then
    echo -e "${YELLOW}Operación cancelada${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}🔧 Paso 1: Desmontando dispositivo...${NC}"
umount "$DEVICE" 2>/dev/null || true

echo -e "${CYAN}🔧 Paso 2: Formateando a FAT32...${NC}"
mkfs.vfat -F 32 -n "CYCLING" "$DEVICE"

echo -e "${CYAN}🔧 Paso 3: Montando dispositivo...${NC}"
mkdir -p "$MOUNT_POINT"
mount "$DEVICE" "$MOUNT_POINT"

echo -e "${CYAN}🔧 Paso 4: Verificando espacio disponible...${NC}"
AVAILABLE_SPACE=$(df "$MOUNT_POINT" | tail -1 | awk '{print $4}')
AVAILABLE_MB=$((AVAILABLE_SPACE / 1024))
echo "   💾 Espacio disponible: ${AVAILABLE_MB} MB"

echo -e "${CYAN}🔧 Paso 5: Verificando playlists disponibles...${NC}"

# Listar playlists disponibles
echo ""
echo "Playlists disponibles:"
AVAILABLE_PLAYLISTS=()
counter=1
for csv in "$CSV_DIR"/playlist_*.csv; do
    if [ -f "$csv" ]; then
        basename=$(basename "$csv" .csv)
        name=$(echo "$basename" | sed 's/_/ /g' | sed 's/playlist //')
        echo "  $counter. $name"
        AVAILABLE_PLAYLISTS+=("$csv")
        counter=$((counter + 1))
    fi
done

if [ ${#AVAILABLE_PLAYLISTS[@]} -eq 0 ]; then
    echo -e "${RED}❌ No se encontraron playlists${NC}"
    echo "   Ejecuta primero: python3 generar_multiples_playlists.py"
    umount "$MOUNT_POINT" 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${YELLOW}Selecciona playlists a copiar (separadas por espacio, ej: 1 2 5)${NC}"
echo -e "${YELLOW}O presiona ENTER para copiar las primeras 3${NC}"
read -p "Selección: " selection

if [ -z "$selection" ]; then
    selection="1 2 3"
fi

echo ""
echo -e "${CYAN}🔧 Paso 6: Creando estructura de carpetas...${NC}"

# Función para copiar y renombrar canciones según playlist
copy_playlist() {
    local playlist_csv=$1
    local output_folder=$2
    local playlist_name=$3
    
    echo -e "${BLUE}   📀 Preparando $playlist_name...${NC}"
    
    if [ ! -f "$playlist_csv" ]; then
        echo -e "${YELLOW}   ⚠️  No se encuentra: $playlist_csv${NC}"
        return 1
    fi
    
    local counter=1
    local copied=0
    local failed=0
    
    # Leer CSV y copiar canciones con rutas completas desde la columna filepath
    while IFS=',' read -r line; do
        # Extraer filepath (segunda columna después de filename)
        filepath=$(echo "$line" | cut -d',' -f2 | sed 's/"//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Saltar header y líneas vacías
        if [[ "$filepath" == "filepath" ]] || [[ -z "$filepath" ]]; then
            continue
        fi
        
        if [ -f "$filepath" ]; then
            # Verificar espacio antes de cada copia
            available=$(df "$MOUNT_POINT" | tail -1 | awk '{print $4}')
            file_size=$(stat -c%s "$filepath")
            file_size_kb=$((file_size / 1024))
            
            if [ $file_size_kb -gt $available ]; then
                echo -e "${YELLOW}      ⚠️  Espacio agotado - copiadas $copied canciones${NC}"
                return 1
            fi
            
            # Obtener nombre base del archivo
            base_name=$(basename "$filepath")
            name="${base_name%.*}"
            ext="${base_name##*.}"
            
            # Renombrar con número para ordenar
            dest_name=$(printf "%02d - %s.%s" $counter "$name" "$ext")
            
            cp "$filepath" "$output_folder/$dest_name" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "      ✓ $counter. $name"
                counter=$((counter + 1))
                copied=$((copied + 1))
            else
                failed=$((failed + 1))
            fi
        else
            echo -e "${YELLOW}      ⚠️  No encontrado: $filepath${NC}"
            failed=$((failed + 1))
        fi
    done < "$playlist_csv"
    
    echo -e "${GREEN}      ✅ $copied canciones copiadas${NC}"
    if [ $failed -gt 0 ]; then
        echo -e "${YELLOW}      ⚠️  $failed archivos no encontrados${NC}"
    fi
    
    return 0
}

echo -e "${CYAN}🔧 Paso 7: Copiando playlists seleccionadas...${NC}"
echo ""

# Convertir selección a array
IFS=' ' read -ra SELECTED <<< "$selection"

PLAYLISTS_COPIED=0
FOLDER_NUM=1

for idx in "${SELECTED[@]}"; do
    # Validar índice
    if [ "$idx" -lt 1 ] || [ "$idx" -gt "${#AVAILABLE_PLAYLISTS[@]}" ]; then
        echo -e "${YELLOW}⚠️  Índice inválido: $idx (ignorado)${NC}"
        continue
    fi
    
    # Obtener playlist CSV
    playlist_idx=$((idx - 1))
    playlist_csv="${AVAILABLE_PLAYLISTS[$playlist_idx]}"
    
    # Crear nombre de carpeta
    basename=$(basename "$playlist_csv" .csv)
    clean_name=$(echo "$basename" | sed 's/playlist_//' | sed 's/_/ /g')
    folder_name=$(printf "%02d_%s" $FOLDER_NUM "$(echo $basename | sed 's/playlist_//')")
    
    # Crear carpeta
    mkdir -p "$MOUNT_POINT/$folder_name"
    
    # Copiar playlist
    if copy_playlist "$playlist_csv" "$MOUNT_POINT/$folder_name" "$clean_name"; then
        PLAYLISTS_COPIED=$((PLAYLISTS_COPIED + 1))
        FOLDER_NUM=$((FOLDER_NUM + 1))
    fi
done

echo ""
if [ $PLAYLISTS_COPIED -gt 0 ]; then
    echo -e "${GREEN}✅ $PLAYLISTS_COPIED playlists copiadas exitosamente${NC}"
else
    echo -e "${RED}❌ No se pudo copiar ninguna playlist${NC}"
    umount "$MOUNT_POINT"
    rmdir "$MOUNT_POINT"
    exit 1
fi

echo ""
echo -e "${CYAN}🔧 Paso 8: Mostrando espacio final...${NC}"
FINAL_SPACE=$(df "$MOUNT_POINT" | tail -1 | awk '{print $4}')
FINAL_MB=$((FINAL_SPACE / 1024))
USED_MB=$((AVAILABLE_MB - FINAL_MB))
echo "   💾 Espacio usado: ${USED_MB} MB"
echo "   💾 Espacio restante: ${FINAL_MB} MB"

echo ""
echo -e "${CYAN}🔧 Paso 9: Sincronizando...${NC}"
sync

echo -e "${CYAN}🔧 Paso 10: Desmontando de forma segura...${NC}"
umount "$MOUNT_POINT"
rmdir "$MOUNT_POINT"

echo ""
echo -e "${GREEN}${BOLD}✅ ¡MicroSD lista para usar!${NC}\n"
echo -e "${BOLD}Estructura creada:${NC}"
for folder in "$MOUNT_POINT"/*; do
    if [ -d "$folder" ]; then
        folder_name=$(basename "$folder")
        song_count=$(ls "$folder" 2>/dev/null | wc -l)
        echo "  📂 $folder_name/ - $song_count canciones"
    fi
done 2>/dev/null || echo "  (microSD ya desmontada)"
echo ""
echo -e "${CYAN}💡 Cómo usar:${NC}"
echo "  1. Inserta la microSD en tu bocina/reproductor"
echo "  2. Selecciona modo 'SD Card' o 'Tarjeta'"
echo "  3. Usa los controles de carpeta para cambiar entre playlists"
echo "  4. Cada carpeta está numerada para fácil navegación"
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗"
echo "║         🎉 LISTO PARA TU ENTRENAMIENTO 🚴                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
