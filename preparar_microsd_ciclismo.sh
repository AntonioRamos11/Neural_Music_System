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
MUSIC_SOURCE="/home/pwn/Music/Musica xioami/Music/bass english"

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

echo -e "${CYAN}🔧 Paso 5: Creando estructura de carpetas...${NC}"
mkdir -p "$MOUNT_POINT/01_Endurance"
mkdir -p "$MOUNT_POINT/02_Intervals"
mkdir -p "$MOUNT_POINT/03_Recovery"

# Función para calcular tamaño de playlist
get_playlist_size() {
    local playlist_csv=$1
    local total_size=0
    
    if [ ! -f "$playlist_csv" ]; then
        echo 0
        return
    fi
    
    while IFS=',' read -r filename rest; do
        filename=$(echo "$filename" | sed 's/"//g')
        source_file="$MUSIC_SOURCE/$filename"
        if [ -f "$source_file" ]; then
            size=$(stat -c%s "$source_file" 2>/dev/null || echo 0)
            total_size=$((total_size + size))
        fi
    done < <(tail -n +2 "$playlist_csv")
    
    echo $total_size
}

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
    
    # Verificar espacio antes de copiar
    local available=$(df "$MOUNT_POINT" | tail -1 | awk '{print $4}')
    local playlist_size=$(get_playlist_size "$playlist_csv")
    local playlist_size_kb=$((playlist_size / 1024))
    local playlist_size_mb=$((playlist_size_kb / 1024))
    
    echo "      📊 Tamaño: ${playlist_size_mb} MB"
    
    if [ $playlist_size_kb -gt $available ]; then
        echo -e "${RED}      ❌ No hay espacio suficiente (faltan $((playlist_size_mb - available/1024)) MB)${NC}"
        return 1
    fi
    
    local counter=1
    local copied=0
    
    # Leer CSV y copiar canciones en orden
    while IFS=',' read -r filename rest; do
        # Limpiar comillas del filename
        filename=$(echo "$filename" | sed 's/"//g')
        source_file="$MUSIC_SOURCE/$filename"
        
        if [ -f "$source_file" ]; then
            # Verificar espacio antes de cada copia
            available=$(df "$MOUNT_POINT" | tail -1 | awk '{print $4}')
            file_size=$(stat -c%s "$source_file")
            file_size_kb=$((file_size / 1024))
            
            if [ $file_size_kb -gt $available ]; then
                echo -e "${YELLOW}      ⚠️  Espacio agotado - copiadas $copied canciones${NC}"
                return 1
            fi
            
            # Obtener nombre limpio (sin path, sin extensión)
            base_name=$(basename "$filename" .m4a)
            # Renombrar con número
            dest_name=$(printf "%02d - %s.m4a" $counter "$base_name")
            
            cp "$source_file" "$output_folder/$dest_name"
            echo "      ✓ $counter. $base_name"
            counter=$((counter + 1))
            copied=$((copied + 1))
        else
            echo -e "${YELLOW}      ⚠️  No encontrado: $filename${NC}"
        fi
    done < <(tail -n +2 "$playlist_csv")
    
    echo -e "${GREEN}      ✅ $copied canciones copiadas${NC}"
    return 0
}

echo -e "${CYAN}🔧 Paso 6: Copiando playlists...${NC}"
echo ""

# Intentar copiar playlists por prioridad
PLAYLISTS_COPIED=0

if copy_playlist "playlist_endurance_60min.csv" "$MOUNT_POINT/01_Endurance" "Endurance (60 min)"; then
    PLAYLISTS_COPIED=$((PLAYLISTS_COPIED + 1))
fi

if copy_playlist "playlist_intervals_45min.csv" "$MOUNT_POINT/02_Intervals" "Intervals (45 min)"; then
    PLAYLISTS_COPIED=$((PLAYLISTS_COPIED + 1))
fi

if copy_playlist "playlist_recovery_30min.csv" "$MOUNT_POINT/03_Recovery" "Recovery (30 min)"; then
    PLAYLISTS_COPIED=$((PLAYLISTS_COPIED + 1))
fi

echo ""
if [ $PLAYLISTS_COPIED -eq 3 ]; then
    echo -e "${GREEN}✅ Las 3 playlists copiadas exitosamente${NC}"
elif [ $PLAYLISTS_COPIED -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Solo se copiaron $PLAYLISTS_COPIED de 3 playlists (espacio insuficiente)${NC}"
else
    echo -e "${RED}❌ No se pudo copiar ninguna playlist${NC}"
    umount "$MOUNT_POINT"
    rmdir "$MOUNT_POINT"
    exit 1
fi

echo ""
echo -e "${CYAN}🔧 Paso 7: Mostrando espacio final...${NC}"
FINAL_SPACE=$(df "$MOUNT_POINT" | tail -1 | awk '{print $4}')
FINAL_MB=$((FINAL_SPACE / 1024))
USED_MB=$((AVAILABLE_MB - FINAL_MB))
echo "   💾 Espacio usado: ${USED_MB} MB"
echo "   💾 Espacio restante: ${FINAL_MB} MB"

echo ""
echo -e "${CYAN}🔧 Paso 8: Sincronizando...${NC}"
sync

echo -e "${CYAN}🔧 Paso 9: Desmontando de forma segura...${NC}"
umount "$MOUNT_POINT"
rmdir "$MOUNT_POINT"

echo ""
echo -e "${GREEN}${BOLD}✅ ¡MicroSD lista para usar!${NC}\n"
echo -e "${BOLD}Estructura creada:${NC}"
echo "  📂 01_Endurance/ - 19 canciones (~71 min)"
echo "  📂 02_Intervals/ - 18 canciones (~62 min)"
echo "  📂 03_Recovery/  - 10 canciones (~37 min)"
echo ""
echo -e "${CYAN}💡 Cómo usar:${NC}"
echo "  1. Inserta la microSD en tu bocina"
echo "  2. Selecciona modo 'SD Card' o 'AUX'"
echo "  3. Usa los controles de carpeta (si tiene) para cambiar entre playlists"
echo "  4. O simplemente reproduce - empezará con 01_Endurance"
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗"
echo "║         🎉 LISTO PARA TU ENTRENAMIENTO 🚴                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
