#!/bin/bash
#
# Exifxtr - Exif Extractor
# Author: Filipe Soares
# GitHub: https://github.com/halpr
# License: MIT
# Version: 1.0.0
# Description: Simple exif extractor, version á simplifier et a porter en C

# Regarde si exiftool est installé -- Si Exiftool est manquant, sudo apt install lib image-exiftool-perl, ou brew install exiftool
if ! command -v exiftool &> /dev/null; then
    echo "Error: exiftool is not installed. Please install it first." >&2
    exit 1
fi

# Fonction montrant instructions d'usage
usage() {
    echo "Usage: $0 [-v] <path-to-image-file>"
    echo "  -v    Verbose mode (shows all raw metadata tags)"
    exit 1
}

VERBOSE=false

# Parser les flats optionnels
while getopts "v" opt; do
    case ${opt} in
        v ) VERBOSE=true ;;
        * ) usage ;;
    esac
done
shift $((OPTIND -1))

# Regarde si un flat argument a été donné
if [ $# -ne 1 ]; then
    usage
fi

IMAGE_FILE="$1"

# Regarde si le fichier existe et s'il est r ou w
if [ ! -f "$IMAGE_FILE" ]; then
    echo "Error: File '$IMAGE_FILE' not found." >&2
    exit 1
fi

echo "=================================================="
echo " EXIF du fichier: $IMAGE_FILE"
echo "=================================================="

if [ "$VERBOSE" = true ]; then
    # Montrer tous les tags par groupe
    exiftool -g "$IMAGE_FILE"
else
    # Montrer toutes les entrées extraites
    exiftool -g \
        -Make \
        -Model \
        -LensModel \
        -DateTimeOriginal \
        -ExposureTime \
        -FNumber \
        -ISO \
        -FocalLength \
        -FocalLengthIn35mmFormat \
        -ExposureProgram \
        -MeteringMode \
        -Flash \
        -ImageSize \
        -FileType \
        "$IMAGE_FILE"
fi

echo "=================================================="