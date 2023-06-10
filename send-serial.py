#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import colors
import glob
import serial
import sys
import time


def main(device, speed, file=None):
    print("# Connecting to {}, speed {}".format(device, speed))
    ser = serial.Serial(
        port=device,
        baudrate=speed
    )
    print("# Connected to {}, speed {}".format(ser.name, ser.baudrate))

    write_bytes("\r\n\r\n", ser)
    time.sleep(2) # Wait for grbl to initialize 
    ser.reset_input_buffer()

    if file:
        print("# Reading from {}".format(file))
        f = open(file, "r")
    else:
        print("# Reading from stdin")
        f = sys.stdin

    cancel = False

    try:
        for line in f:
            if cancel:
                break
            send_line(line, ser)
    except KeyboardInterrupt:
        cancel = True
    finally:
        print("\n# Disconnecting from {}".format(ser.name))
        f.close()
        ser.close()


def send_line(line, ser):
    command = line.strip()
    if command != '':
        print("> {}".format(colors.bold(command)))
        write_bytes(command + "\n", ser)
        response = str(ser.readline().strip(), 'utf-8')
        if response == 'ok':
            print('< {}'.format(colors.green(response)))
        else:
            print('< {}'.format(colors.red(response)))


def write_bytes(unicode_string, ser):
    ser.write(unicode_string.encode("utf-8"))


def guess_device():
    try:
        # macOS
        return glob.glob('/dev/tty.usb*')[0]
    except IndexError:
        try:
            # Linux
            return glob.glob("/dev/ttyUSB*")[0]
        except IndexError:
            # Give up
            return glob.glob("/dev/*")[0]


description = """
Sends G-Code commands (well, any commands, really) from either 
standard input (stdin) or the given file, to a connected Serial device.
"""

examples = """examples:
  echo 'M03 S05' | %(prog)s
  cat /some/file.gcode | %(prog)s
  %(prog)s /some/file.gcode
  cat /some/file.gcode | %(prog)s -d /dev/tty.whatever -s 9200
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=description,
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "file",
        metavar="FILE",
        nargs="?",
        default=None,
        help="send lines from the file at the given path, rather than from stdin"
    )
    parser.add_argument(
        "-d",
        "--device",
        default=guess_device(),
        help="path of a serial device to write to (default: %(default)s)"
    )
    parser.add_argument(
        "-s",
        "--speed",
        default=115200,
        help="baud rate to write with (default: %(default)s)"
    )

    args = parser.parse_args()

    main(device=args.device, speed=args.speed, file=args.file)
