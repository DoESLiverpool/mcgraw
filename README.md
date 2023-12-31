# McGraw the Pen Plotter

[McGraw is a pen plotter at DoES Liverpool](https://github.com/DoESLiverpool/somebody-should/wiki/Pen-Plotter-McGraw), that was converted from a laser engraver.

Because of this former life as a CNC machine, McGraw expects to be fed [G-Code files](https://en.wikipedia.org/wiki/G-code). So if you want it to draw anything, you’ll need to convert your artwork to G-Code format. This is where the scripts in this repo come in!

## Requirements

- [Python 3](https://www.python.org/downloads/)

## How to use this

First, run the script to create a virtualenv and install the required Python packages into it. Open a Terminal, `cd` to this directory, and run:

    script/setup

A little while later, it will have set everything up.

Now activate the virtualenv:

    . ./venv/bin/activate

Eventually, we want the code in this repo to work for _any_ SVG or G-Code file. But for now, you are expected to either pass a perfectly-formed G-Code file to `./send-serial.py`, or to [export some G-Code from Inkscape](https://github.com/DoESLiverpool/somebody-should/wiki/Pen-Plotter-McGraw) then fix it up with `./fix-gcode.py` and send it with `./send-serial.py`.

For example, assuming you have a G-Code file that has been exported from Inkscape (in this case, `test/a3-landscape-test.gcode`):

    cat test/a3-landscape-test.gcode | ./fix-gcode.py | ./send-serial.py

Note: `send-serial.py` will attempt to guess McGraw’s device path on your system—defaulting to common paths like `/dev/tty.usb*` and `/dev/ttyUSB*`—but you may need to provide a path explicitly:

    … | ./send-serial.py test/a3-landscape-test.gcode --device /dev/cu.usbserial1

McGraw will now start drawing your file.

## Tips

You can send one-off G-Code commands to McGraw by piping them into `./send-serial.py`, eg:

    echo 'M3 S05' | ./send-serial.py   # pen up
    echo 'M3 S120' | ./send-serial.py  # pen down

When fixing up your G-Code, you can provide a custom speed parameter (the default is 800):

    … | ./fix-gcode.py --speed 1200 | …

If any of the scripts give you a `ModuleNotFoundError` when you run them, then you’re probably running them outside the virtualenv. Activate the virtualenv, and re-attempt:

    . ./venv/bin/activate
    cat test/a3-landscape-test.gcode | ./fix-gcode.py | ./send-serial.py

You can stop `send-serial.py` partway through a file by pressing `Ctrl-C`. Note: This will prevent further commands being sent to McGraw, but McGraw _will_ continue whatever commands have already been sent – the only way to prevent that is to cut power to McGraw using the red button on its circuit board.

## How it works

`svg-to-gcode.sh` is meant to be a friendly wrapper to a complex `vpype` command. [Vpype](https://vpype.readthedocs.io/en/latest/index.html) is a Python utility creating and modifying vector graphics like SVGs. In case, we’re using the [vpype-gwrite plugin](https://github.com/plottertools/vpype-gcode/) to output G-Code. The settings in `mcgraw-config.toml` tell vpype-gcode to use the specific commands (eg: for pen up, pen down) that McGraw the Pen Plotter expects. **But it doesn’t work right now.**

`svg-to-gcode.py` is meant to use the `vpype` and `vpype-gcode` Python libraries to read the specified SVG files, optimise them for plotting (combining lines, sorting lines by proximity), and then export them as G-Code files. The settings in `mcgraw-config.toml` tell vpype-gcode to use the specific commands (eg: for pen up, pen down) that McGraw the Pen Plotter expects. **But it doesn’t work right now.**

`fix-gcode.py` automatically performs the replacements that we used to do by hand (see _Converting from Inkscape GCodeTools output_, below), making G-Code files exported from Inkscape’s built-in GCodeTools “Path to Gcode” extension suitable for drawing on McGraw.

`send-serial.py` reads G-Code commands from the given file, or from whatever’s piped into it on standard input, establishes a Serial connection with mcGraw, and sends each line of the file to McGraw, printing McGraw’s responses. Since it’s using a “call and response” method (meaning that McGraw has to wait for the next command after finishing the current one, rather than already having the next command in its internal queue) `send-serial.py` potentially slows down McGraw, especially when drawing lots of small line segments. Perhaps one day we could re-write `send-serial.py` to [use a batched approach](https://github.com/gnea/grbl/blob/921e5a9799691118ffe5d4ecf5ccce68efe8a3f8/doc/script/stream.py).

### Jackie’s “flavour file”

Jackie provided a [Juicy G-Code flavour file](https://hackage.haskell.org/package/juicy-gcode-1.0.0.0#readme), with the following command snippets:

#### `begin`

| expression | what it does |
| :--- | :--- |
| `G17` | select the XY plane (this probably isn’t required, as `G17` is [the default in grbl](https://github.com/gnea/grbl/wiki/Grbl-v1.1-Commands#g---view-gcode-parser-state)) |
| `G21` | use millimeter units (this probably isn’t required, as `G21` is [the default in grbl](https://github.com/gnea/grbl/wiki/Grbl-v1.1-Commands#g---view-gcode-parser-state)) |
| `G90` | use absolute distances (this probably isn’t required, as `G21` is [the default in grbl](https://github.com/gnea/grbl/wiki/Grbl-v1.1-Commands#g---view-gcode-parser-state)) |
| `G28` | rapid move back to home |
| `G1 F400` | linear move, at feed rate `400` |
| `M3 S05` | set spindle speed to `5` – McGraw interpets this as “pen up” |
| `G4 P0.3` | dwell for 0.3 seconds – we use this to avoid “ticks” caused by the pen remaining in contact while the head moves |

#### `end`

| expression | what it does |
| :--- | :--- |
| `M3 S05` | set spindle speed to `5` – McGraw interpets this as “pen up” |
| `G4 P0.3` | dwell for 0.3 seconds – we use this to avoid “ticks” caused by the pen remaining in contact while the head moves |
| `G1 X.000 Y.000` | linear move to XY position `0,0` |

#### `toolon`

| expression | what it does |
| :--- | :--- |
| `M3 S120` | set spindle speed to `120` – McGraw interpets this as “pen down” |
| `G4 P0.3` | dwell for 0.3 seconds – we use this to avoid “ticks” caused by the pen remaining in contact while the head moves |

#### `tooloff`

| expression | what it does |
| :--- | :--- |
| `M3 S05` | set spindle speed to `5` – McGraw interpets this as “pen up” |
| `G4 P0.3` | dwell for 0.3 seconds – we use this to avoid “ticks” caused by the pen remaining in contact while the head moves |

### Converting from Inkscape GCodeTools output

[The DoES wiki explains](https://github.com/DoESLiverpool/somebody-should/wiki/Pen-Plotter-McGraw) how to replace some expressions generated by [GCodeTools](https://github.com/cnc-club/gcodetools), with equivalents that McGraw understands. These are archived here for convenience:

| before | what it does | after | what it does |
| :--- | :--- | :--- | :--- |
| `G00 Z5.000000` | rapid travel to XYZ `0,0,5` | `M03 S05; G04 P0.3` | set spindle speed to `5` (pen up) then dwell for 0.3 seconds |
| `Z-0.125000` | a coordinate 0.125mm below the surface |  | nothing (so `0`) |
| `G01 F100.0(Penetrate)` | linear move at feed rate `100` | `G04 P0.3; M03 S120` | dwell for 0.3 seconds then set spindle speed to `120` (pen down)
| `F400` | speed `400` | `F800` | speed `800` |
