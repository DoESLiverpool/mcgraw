#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"

SCRIPT=$(basename "$0")
DIMENSIONS="297mm 420mm"
SPLIT_LAYERS=false
INPUTS=()

usage()
{
    cat <<EOF
Usage: $SCRIPT [--help] [--dimensions DIMENSIONS] FILES ..."

Converts the given SVG files into G-Code files, suitable for
plotting on McGraw the DoES Liverpool pen plotter.

The input files must be in SVG format.

positional arguments:
  FILES             paths to one or more SVG files to be converted

optional arguments:
  --dimensions      intended physical width and height of
                    ayour artwork (default: $DIMENSIONS)
                    (see below for how to specify dimensions)
  --split-layers    output a separate G-Code file for each layer
                    in the SVG (default: do not split)
  -h, --help        show this message and exit

how to specify dimensions:
  WIDTH HEIGHT      eg: "21cm 29.7cm" or "210mm 297mm" (A4 paper size)
  PAPERSIZE         one of: "a3" (portrait), "a3-portrait", "a3-landscape",
                    "a4" (portrait), "a4-portrait", "a4-landscape",
                    "a5" (portrait), "a5-portrait", "a5-landscape"

examples:
  $SCRIPT input.svg
  $SCRIPT --dimensions "a4-landscape" input.svg
  $SCRIPT --dimensions "10cm 10cm" --split-layers input.svg
  $SCRIPT *.svg
EOF
}

store_input_path()
{
    if [ -e "$1" ]; then
        INPUTS+=("$1") # Append to bash array
    else
        echo "File not found: $1"
        usage
        exit 1
    fi
}

while [ "$1" != "" ]; do
    case $1 in
        --dimensions )          shift
                                DIMENSIONS=$1
                                ;;
        --split-layers )        SPLIT_LAYERS=true
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     store_input_path "$1"
    esac
    shift
done

# lowercase dimensions
DIMENSIONS=$(echo "$DIMENSIONS" | tr '[:upper:]' '[:lower:]')

case "$DIMENSIONS" in
    a3 | a3-portrait )          DIMENSIONS="297mm 420mm";;
    a3-landscape )              DIMENSIONS="420mm 297mm";;
    a4 | a4-portrait )          DIMENSIONS="210mm 297mm";;
    a4-landscape )              DIMENSIONS="297mm 210mm";;
    a5 | a5-portrait )          DIMENSIONS="148mm 210mm";;
    a5-landscape )              DIMENSIONS="210mm 148mm";;
esac

# Note: $DIMENSIONS and $WRITE are intentionally unquoted,
# so the words inside them get passed as separate parameters.
for INPUT in "${INPUTS[@]}"; do
    if [ $SPLIT_LAYERS = true ]; then
        WRITE="forlayer gwrite --profile mcgraw ${INPUT%.svg}-%_name%-%_lid%.gcode end"
    else
        WRITE="gwrite --profile mcgraw ${INPUT%.svg}.gcode"
    fi

    WRITE="write ${INPUT%.svg}-rewritten.svg"

    vpype --config "mcgraw-config.toml" \
        read "$INPUT" \
        linemerge \
        linesort \
        scaleto $DIMENSIONS \
        $WRITE
done

# vpype read input.svg forlayer write "output_%_name or _lid%.svg" end
