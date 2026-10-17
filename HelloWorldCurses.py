import curses
from curses import wrapper # get proper exceptions when using curses
import time
import sys



def main(stdscr):

    minx=35
    miny=14
    x=curses.COLS
    y=curses.LINES

    stdscr.clear()
    curses.noecho()
    curses.cbreak()

    stdscr.box()
    stdscr.addstr(1, 1, "Hello, world!")
    stdscr.addstr(2,1,'Screen x={} y={}'.format(x,y))
    stdscr.refresh() 
    time.sleep(2)

    if (x<minx or y<miny):
        stdscr.addstr(3,1,'ERROR: Screen too small!')
        stdscr.addstr(4,1,'Need size x>{} y>{}'.format(minx,miny))
        stdscr.refresh() 
        time.sleep(5)
        return

    x1=2
    y1=5
    for i in range(0, 11):
        stdscr.addstr(y1,x1,'number: {} ...press something'.format(i))
        stdscr.refresh()
        stdscr.getkey()
        y1=y1+1
    time.sleep(2)
  

wrapper(main)
