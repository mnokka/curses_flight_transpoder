import curses
from curses import wrapper # get proper exceptions when using curses
import time
import random
import datetime
import locale



locale.setlocale(locale.LC_TIME, "fi_FI.UTF-8")

#####################################################################################

def RandomData():
    return random.randint(0, 25)


#####################################################################################
def PrintScreen(stdscr):
    x1=2
    y1=2
    stdscr.clear()
    stdscr.box()

    
    

    y2=3
    t=datetime.datetime.now()
    paivays = t.strftime('%d.%m.%Y')
    paivan_nimi = t.strftime("%A")
    kello = t.strftime('%H:%M:%S')
    stdscr.addstr(y1, 10, '{} {}  {}'.format(paivan_nimi, paivays,kello))

    y1=y2+3
    v1=RandomData()
    stdscr.addstr(y1,x1,'Tilannerivi 1: {}'.format(v1))
    y1=y1+1
    v1=RandomData()
    stdscr.addstr(y1,x1,'Tilannerivi 2: {}'.format(v1))
    y1=y1+1
    v1=RandomData()
    stdscr.addstr(y1,x1,'Tilannerivi 3: {}'.format(v1))

    y1=y1+5
    stdscr.addstr(y1,x1,'Q - lopeta')
    stdscr.refresh()

########################################################################################
def CheckQuit(stdscr):
    stdscr.nodelay(False)
    x1=2
    y1=5
    stdscr.clear()
    stdscr.box()
    stdscr.addstr(y1,x1,' P - Verify Quit     Any other key - Cancel')
    stdscr.refresh()
    key=stdscr.getkey() # wait
    stdscr.nodelay(True)
    if key in ('P', 'p'):
        return 'Y'
    else:
        return 'N'


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

    stdscr.nodelay(True)
    while True:
        PrintScreen(stdscr)
        for j in range(10):  # delay is x 0,1s
            key = stdscr.getch()

            if key in (ord('Q'), ord('q')):
                ckey = CheckQuit(stdscr) # do not wait
                if ckey == "Y":
                    return
                else:
                    break
            time.sleep(0.1)
     

wrapper(main)
