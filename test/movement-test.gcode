(XY plane)
G17

(millimeter units)
G21

(absolute distances)
G90

(rapid move home)
G28

(default feed rate)
G01 F800

(up)
M03 S05

(down, up)
G04 P1
M03 S120
G04 P1
M03 S05

(down, up)
G04 P1
M03 S120
G04 P1
M03 S05

(rapid move, down)
G04 P1
G00 X60 Y60
M03 S120

(move in a square)
G01 F1200 X20 Y60
G01 F1200 X20 Y20
G01 F1200 X60 Y20
G01 F1200 X60 Y60

(up, rapid move home)
G04 P1
M03 S05
G00 X0 Y0
