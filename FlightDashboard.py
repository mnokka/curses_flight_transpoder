# Based onhttps://github.com/mnokka/flight_transponder
# UI implemented with Curses
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

# --------------------------------------------------
# ASETUKSET
# --------------------------------------------------

try:
    locale.setlocale(locale.LC_TIME, "fi_FI.UTF-8")
except locale.Error:
    print(f"VAROITUS: Suomi localea ei saatu käyttöön: {e}")
    print(f"Käytössä oleva locale: {locale.setlocale(locale.LC_TIME, None)}")


map_file = "map.html"
dashboard_file = ""
dump_file = "dump109.log"

StartTime = time.monotonic()

JSON_DIR = "./json_data"
JSON_FILE = os.path.join(JSON_DIR, "aircraft_backup.json")
EXCEL_FILE = "./aircraftDatabase.csv"


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

    stdscr.addstr(y1, x1, headers[:max_width])
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

        if y1 >= curses.LINES - 1:
            break

        stdscr.addstr(
            y1, x1,
            row[:max_width]
        )
        y1 += 1

    return y1


# --------------------------------------------------
# PÄÄNÄYTTÖ
# --------------------------------------------------

def PrintScreen(stdscr, planes,systemmessage):

    ###### systemmessage
    if not hasattr(PrintScreen, "message"):
        PrintScreen.message = ""
        PrintScreen.message_time = 0

    if systemmessage:
        if systemmessage != PrintScreen.message:
            PrintScreen.message = systemmessage
            PrintScreen.message_time = time.monotonic()

    if time.monotonic() - PrintScreen.message_time >= 10:
        PrintScreen.message = ""

    systemmessage = PrintScreen.message 
    x1 = 2
    y1 = 0
    ######
    

    stdscr.erase()
    stdscr.box()

    stdscr.addstr(y1, x1,systemmessage,curses.A_BOLD) 
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
        f"Ajoaika: {hh:02d}:{mm:02d}:{ss:02d}"
    )

    stdscr.addstr(
        y1, 2,
        otsikko[:max(0, curses.COLS - 4)],
        curses.A_BOLD
    )
    y1 += 2

    tiedostot = (
        f"Map file:{map_file}   "
        f"Dump file:{dump_file}   "
        f"Dashboard file:{dashboard_file}"
    )

    stdscr.addstr(
        y1, x1,
        tiedostot[:max(0, curses.COLS - x1 - 1)]
    )
    y1 += 1

    ohje = "s - Save data    m - Save map"
    stdscr.addstr(
        y1, x1,
        ohje[:max(0, curses.COLS - x1 - 1)]
    )
    y1 += 1
    

    viiva = "-" * max(0, curses.COLS - x1 - 2)
    stdscr.addstr(y1, x1, viiva)
    y1 += 1

    y1 = PrintAircraftList(
        stdscr, planes, x1, y1
    )

    y1 += 2

    if y1 < curses.LINES - 1:
        stdscr.addstr(y1, x1, "Q - lopeta")

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
# PÄÄOHJELMA
# --------------------------------------------------

def main(stdscr):
    minx = 35
    miny = 14

    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)

    x = curses.COLS
    y = curses.LINES

    if x < minx or y < miny:
        stdscr.erase()
        stdscr.addstr(1, 1, "ERROR: Screen too small!")
        stdscr.addstr(
            2, 1,
            f"Need screen at least {minx} x {miny}"
        )
        stdscr.refresh()
        time.sleep(3)
        return

    while True:
        planes = ReadAircraftData()
     
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

        
        PrintScreen(stdscr, planes,systemmessage)

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
