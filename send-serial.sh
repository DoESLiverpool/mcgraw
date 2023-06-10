#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"

SCRIPT=$(basename "$0")
FILE=""
DEVICE=$(ls /dev/cu.usb* | head -n1)
SPEED="115200"

usage()
{
    cat <<EOF
Usage: $SCRIPT [--help] [--device DEVICE] [--speed SPEED] [FILE]"

optional arguments:
  FILE              send lines from the file at the given path,
                    rather than from stdin
  -d, --device      path of a serial device to write to
                    (default: $DEVICE)
  -s, --speed       baud rate to write with (default: $SPEED)
  -h, --help        show this message and exit

Sends G-Code commands (well, any commands, really) from either standard
input (stdin) or the given file, to a connected Serial device.

examples:
  echo 'M03 S05' | $SCRIPT
  cat /some/file.gcode | $SCRIPT
  $SCRIPT /some/file.gcode
  cat /some/file.gcode | $SCRIPT -d /dev/tty.whatever -s 9200
EOF
}

store_file_path()
{
    if [ -e "$1" ]; then
        FILE="$1"
    else
        echo "Unrecognised argument: $1"
        usage
        exit 1
    fi
}

while [ "$1" != "" ]; do
    case $1 in
        -d | --device )     shift
                            PAGESIZE=$1
                            ;;
        -s | --speed )      shift
                            ORIENTATION=$1
                            ;;
        -h | --help )       usage
                            exit
                            ;;
        * )                 store_file_path "$1"
    esac
    shift
done

if [ "$FILE" == "" ]; then
    echo "# Reading from stdin"
else
    echo "# Reading from $FILE"
fi
echo "# Opening $DEVICE, speed $SPEED"

# TODO: this must be `stty -F` on linux
stty -f $DEVICE $SPEED -echo

if [ "$FILE" == "" ]; then
    while read -r line; do
        echo "$line" > $DEVICE
    done
else
    while read -r line; do
        echo "$line" > $DEVICE
    done < "$FILE"
fi

# exec 4<$DEVICE 5>$DEVICE
# stty -F $DEVICE $SPEED -echo
# while read -r LINE; do
#     echo "> $LINE"
#     # echo "$LINE" >&5
#     # read RESPONSE <&4
#     # echo "< $RESPONSE"
# done < <(cat "$FILE" /dev/stdin)

# while read line; do
#     echo "$line"
# done < "${1:-/dev/stdin}"

# while read -r line; do
#     echo "$line" > /dev/ttyS2
# done < /dev/ttyS2

# echo -e "USB Command" >> /dev/ttyACM0
# echo $?

# https://unix.stackexchange.com/questions/569110/how-to-send-and-receive-data-from-serial-port-using-command-line
# exec 3<>/dev/ttyUSB0      # hold serial device open on file descriptor 3
# stty -F /dev/ttyUSB0 9600
# echo "1" >&3              # send data
# sleep 0.2                 # wait for data to be sent
# cat <&3                   # read the data
# 3<&-                      # close file descriptor

# https://superuser.com/questions/845299/echo-pipe-command-output-to-serial-line
# ( stty raw speed 115200 >&2; echo -ne 'output-string' ) >/dev/ttyUSB0 <&1

# https://unix.stackexchange.com/questions/231975/connect-to-serial-issue-a-command-read-result-capture-it-and-exit
# tty=/dev/ttyUSB0
# exec 4<$tty 5>$tty
# stty -F $tty 9600 -echo
# echo abcdef >&5
# read reply <&4
# echo "reply is $reply"

echo "# Closed $DEVICE"
