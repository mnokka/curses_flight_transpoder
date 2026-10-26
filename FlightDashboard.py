# Based on https://github.com/mnokka/flight_transponder
# UI reimplemented with Curses October 2026
#
# mika.nokka1@gmail.com October 2026
#


import curses
from curses import wrapper
import time
import datetime
import locale
import json
import os
import random
import logging

# --------------------------------------------------
# ASETUKSET
# --------------------------------------------------

try:
    locale.setlocale(locale.LC_TIME, "fi_FI.UTF-8")
except locale.Error:
    print(f"VAROITUS: Suomi localea ei saatu käyttöön")
    print(f"Käytössä oleva locale: {locale.setlocale(locale.LC_TIME, None)}")
    time.sleep(5)




DEBUG_FILE = "debug.log"
map_file = "map.html"
dashboard_file = ""
dump_file = "dump109.log"
Y1Breaking=2

StartTime = time.monotonic()

JSON_DIR = "./json_data"
JSON_FILE = os.path.join(JSON_DIR, "aircraft_backup.json")
EXCEL_FILE = "./aircraftDatabase.csv"



logging.basicConfig(
    filename=DEBUG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s"
)

logging.debug("Program started")




# --------------------------------------------------
# JSON-DATAN LUKEMINEN
# --------------------------------------------------

def ReadAircraftData():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("aircraft", [])

    except (FileNotFoundError, json.JSONDecodeError):
        return []

    except OSError:
        return []


# --------------------------------------------------
# LENTOKONETAULUKKO
# --------------------------------------------------

def PrintAircraftList(stdscr, planes, x1, y1):
    headers = (
        f"{'ICAO':<7} {'Flight':<8} "
        f"{'Lat':>9} {'Lon':>9} {'Alt':>6} "
        f"{'Spd':>6} {'Trk':>5} {'RSSI':>6} "
        f"{'Msgs':>5} {'Vert':>6} {'Squawk':>6} "
        f"{'Alert':>5} {'OnG':>4}"
    )

    max_width = max(0, curses.COLS - x1 - 1)

    stdscr.addstr(y1, x1, headers)
    y1 += 1

    stdscr.addstr(

        y1, x1,
        "-" * min(len(headers), max_width)
    )
    y1 += 1

    for p in planes:
        row = (
            f"{str(p.get('hex', '?')):<7} "
            f"{str(p.get('flight') or '?')[:8]:<8} "
            f"{p.get('lat', 0):>9.5f} "
            f"{p.get('lon', 0):>9.5f} "
            f"{p.get('altitude', 0):>6} "
            f"{p.get('speed', 0):>6} "
            f"{p.get('track', 0):>5} "
            f"{p.get('rssi', 0):>6.1f} "
            f"{p.get('messages', 0):>5} "
            f"{p.get('vertical_rate', 0):>6} "
            f"{str(p.get('squawk', '?')):>6} "
            f"{str(p.get('alert', False)):>5} "
            f"{str(p.get('on_ground', False)):>4}"
        )

        logging.debug("curses.LINES - 1:  %s",curses.LINES - 1)
        logging.debug("y1:  %s",y1)
        if y1 >= curses.LINES -Y1Breaking:
            logging.debug("Breaking listing of aircrafs, y1 too big %s", y1)
            break

        stdscr.addstr(y1, x1,row)
        y1 += 1
    
    logging.debug("Printing list returns %s", y1)
    return y1


#############################################################################################################
# MAIN SCREEN LOGIC. like amiga copper list management
# ###########################################################################################################

def PrintScreen(stdscr, planes,systemmessage,bottommessage):

    stdscr.erase()
    curses.update_lines_cols() 
    stdscr.box()

    x1=2
    y1=0

    ### check minimum screen size
    rows, cols = stdscr.getmaxyx()
    logging.debug("Screen size (rowxcol): %s %s", rows, cols)
    if rows < 10 or cols < 60:
        stdscr.erase()
        viesti = "Window too small - resize"
        y = rows // 2
        x = max(0, (cols - len(viesti)) // 2)

        if rows > 0 and cols > 0:
            stdscr.addnstr(y, x, viesti, max(0, cols - x - 1))

        stdscr.refresh()
        return
    ####################

    ###### handle systemmessage
    if not hasattr(PrintScreen, "message"):
        PrintScreen.message = ""
        PrintScreen.message_time = 0
        PrintScreen.system_message_alarmed = 0

    if systemmessage:
        if systemmessage != PrintScreen.message:
            PrintScreen.message = systemmessage
            PrintScreen.message_time = time.monotonic()

    if time.monotonic() - PrintScreen.message_time >= 10:
        PrintScreen.message = ""
        PrintScreen.system_message_alarmed = 0
     

    if PrintScreen.message: 
        if (not PrintScreen.system_message_alarmed):
            beep()
            flash_screen()
            PrintScreen.system_message_alarmed = 1
        stdscr.addstr(0, 5,PrintScreen.message,curses.A_REVERSE) 
    ######
    
    ##### clock and date
    y1=y1+1
    now = datetime.datetime.now()
    paivays = now.strftime("%d.%m.%Y")
    paivan_nimi = now.strftime("%A")
    kello = now.strftime("%H:%M:%S")

    runtime = int(time.monotonic() - StartTime)
    hh = runtime // 3600
    mm = (runtime % 3600) // 60
    ss = runtime % 60

    otsikko = (
        f"{paivan_nimi} {paivays}  {kello}       "
        f"Running time: {hh:02d}:{mm:02d}:{ss:02d}"
    )
    stdscr.addstr(y1, 2,otsikko,curses.A_BOLD)
    ##########
    
    ############ file infos
    y1 += 2
    tiedostot = (
        f"Map file:{map_file}   "
        f"Dump file:{dump_file}   "
        f"Dashboard file:{dashboard_file}"
    )
    stdscr.addstr(y1, x1,tiedostot,curses.A_DIM)
    y1 += 1

    ohje = "s - Save data    m - Save map"
    stdscr.addstr(y1, x1,ohje,curses.A_DIM)
    y1 += 1
    ################

    stdscr.addstr(y1, x1, '--------------------------------------------------------------------------------------------------')
    y1 += 1

    y1 = PrintAircraftList(stdscr, planes, x1, y1)

    y1 += 2
    if y1 <= curses.LINES -Y1Breaking:
        stdscr.addstr(y1, x1, "Q - lopeta")

    ######handle bottom screen system message 

    if not hasattr(PrintScreen, "bottom_message"):
            PrintScreen.bottom_message = ""
            PrintScreen.bottom_message_time = 0
            PrintScreen.bottom_message_alarmed = 0

    if bottommessage:
        if bottommessage != PrintScreen.bottom_message:
            PrintScreen.bottom_message = bottommessage
            PrintScreen.bottom_message_time = time.monotonic()

    if time.monotonic() - PrintScreen.bottom_message_time >= 15:
        PrintScreen.bottom_message = ""
        PrintScreen.bottom_message_alarmed = 0

    if PrintScreen.bottom_message:
        rows, cols = stdscr.getmaxyx()
        bottom_message = PrintScreen.bottom_message
        y = rows - 1
        x = 5
        if (not PrintScreen.bottom_message_alarmed):
            beep()
            flash_screen()
            PrintScreen.bottom_message_alarmed = 1
        stdscr.addstr(y, x, PrintScreen.bottom_message,curses.A_REVERSE)

    ######################




    stdscr.refresh()


# --------------------------------------------------
# LOPETUKSEN VAHVISTUS
# --------------------------------------------------

def CheckQuit(stdscr):
    stdscr.nodelay(False)

    stdscr.erase()
    stdscr.box()

    x1 = 2
    y1 = 5

    stdscr.addstr(
        y1, x1,
        "P - Vahvista lopetus    Muu nappain - Peruuta"
    )
    stdscr.refresh()

    key = stdscr.getkey()

    stdscr.nodelay(True)

    if key in ("P", "p"):
        return "Y"

    return "N"

# --------------------------------------------------
# UTILITIES
# --------------------------------------------------

def beep():
    os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga &")


def flash_screen():
    curses.flash()


# --------------------------------------------------
# PÄÄOHJELMA
# --------------------------------------------------

def main(stdscr):

    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)


    while True:
        planes = ReadAircraftData()
     

##################################### 
        systemmessage = ""
        if not planes:
            systemmessage = "ERROR: AIRCRAFT DATA NOT FOUND"
        elif random.randint(1, 20) == 1:
            systemmessage = random.choice([
                "TEST: New aircraft detected",
                "TEST: JSON data updated",
                "TEST: Signal weak",
                "TEST: Aircraft data received"
            ])
######################################
        bottommessage=""
        if (random.randint(1, 20) == 1):
            bottommessage = random.choice([
                "TEST: Random alarm",
                "TEST: New plane ever detected detected",
                "TEST: Signal blaa blaa",
                "TEST: Bottom message is this"
            ])
#######################################


        PrintScreen(stdscr, planes,systemmessage,bottommessage)

        # Päivitä näyttö noin sekunnin välein.
        for _ in range(10):
            key = stdscr.getch()

            if key in (ord("Q"), ord("q")):
                result = CheckQuit(stdscr)

                if result == "Y":
                    return

                # Peruuta: palataan päänäyttöön.
                break

            time.sleep(0.1)


# --------------------------------------------------
# KÄYNNISTYS
# --------------------------------------------------

wrapper(main)
