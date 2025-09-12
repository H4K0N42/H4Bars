"""
    Progress Bar. Takes a pico W and a light strip to make a physical progress bar.
    Proof of Concept. Fork the repository and make it better
    
    Original Copyright (C) 2023 Veeb Projects https://veeb.ch
    Modifications made by H4K0N42 in 2025

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
from random import choice
import machine
import _thread
import utime
import time
import network
import config
import urequests
import neopixel
import math
import os
import json
import re
import gc

# Time with daylight savings time and time zone factored in, edit this to fit where you are
worldtimeurl = "https://timeapi.io/api/TimeZone/zone?timezone=" + config.TIMEZONE
n = config.PIXELS           # Number of pixels on strip
p = config.GPIOPIN          # GPIO pin that data line of lights is connected to
hexcolors = config.COLORS
schedule = config.SCHEDULE  # Working hours in config file (only used if google calendar not used)
flip = config.FLIP
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
led.on()
time.sleep(1)
checkevery = config.REFRESH   # Number of seconds for interval refreshinag neopixel
AP_NAME = "veebprojects"
AP_DOMAIN = "pipico.net"
AP_TEMPLATE_PATH = "ap_templates"
WIFI_FILE = "wifi.json"
delwifi = config.DELWIFI
dest = config.PING
dim = config.DIM

def machine_reset():
    print("Resetting...")
    time.sleep(1)
    machine.reset()


def whatday(weekday):
    dayindex = int(weekday)
    nameofday = [
                    'monday',
                    'tuesday',
                    'wednesday',
                    'thursday',
                    'friday',
                    'saturday',
                    'sunday']
    day = nameofday[dayindex]
    return day


def set_time(worldtimeurl):
    print('Grab time: ', worldtimeurl)
    try:
        response = urequests.get(worldtimeurl, timeout=60)
    except:
        print('Problem with ', worldtimeurl)
    # parse JSON
    parsed = response.json()
    datetime_str = str(parsed["currentLocalTime"])
    year = int(datetime_str[0:4])
    month = int(datetime_str[5:7])
    day = int(datetime_str[8:10])
    hour = int(datetime_str[11:13])
    minute = int(datetime_str[14:16])
    second = int(datetime_str[17:19])
    # update internal RTC
    machine.RTC().datetime((year,
                  month,
                  day,
                  0,
                  hour,
                  minute,
                  second,
                  0))
    print(f"Set: {year}/{month}/{day} {hour}:{minute}:{second}")


def is_online(dest, last, offcount=0):
    try:
        response = urequests.get(dest, timeout=3)
        response.close()  # important in urequests to avoid memory leaks
        return True
    except Exception:
        if last == False: return False
        print(f"PING: Failed: {offcount}")
        time.sleep(1)
        if offcount >= 5: return False
        return is_online(dest, last, offcount+1)

    
def bar(np, upto, clockin, clockout, r, c, n, dim):
    barupto = hourtoindex(upto, clockin, clockout)
    for i in range(barupto):
        np[i] = getcolor(c, n, i+r, dim)


def flipit(np, n):
    temp=[0]*n
    for i in range(n):
        temp[i]=np[i]
    for i in range(n):
        np[i]=temp[n-1-i]
    return np


def off(np):
    print('Turn off all LEDs')
    for i in range(n):
        np[i] = (0, 0, 0)
        np.write()


def hourtoindex(hoursin, clockin, clockout):
    index = int(math.floor(n*(hoursin - clockin)/(clockout-clockin)))
    if index < 0 or index > n:
        index = -1
    return index


def convertcolors(hexcolors):
    colors = []
    for color in hexcolors:
        colors.append(tuple(int(color[i:i+2], 16) for i in (1, 3, 5)))
    return colors


def getcolor(colors, n, pos, dim):
    pos = pos % n
    colorcount = len(colors)
    steps = n // colorcount

    if pos >= steps * colorcount:
        color = tuple(int(round(c * dim)) for c in colors[0])
        return color
    
    step = pos % steps
    start = colors[int((pos/steps)%colorcount)]
    end = colors[int(((pos/steps+1)%colorcount))]
    color = (
    int(round(start[0] + (end[0] - start[0]) * step / (steps - 1)) * dim),
    int(round(start[1] + (end[1] - start[1]) * step / (steps - 1)) * dim),
    int(round(start[2] + (end[2] - start[2]) * step / (steps - 1)) * dim)
    )
    return color


def atwork(clockin, clockout, time):
    work = False
    if (time >= clockin) & (time < clockout):
        work = True
    return work


def red(np, dim, c):
    print("Red!")
    for i in range(n):
        np[i] = getcolor(c, n, i, dim)
    r, g, b = [0]*n, [0]*n, [0]*n
    for i in range(n): r[i], g[i], b[i] = np[i]
    for j in range(int(255*dim)):
        for i in range(n):
            if r[i] < int(255*dim): r[i] += 1
            if g[i] > 0: g[i] -= 1
            if b[i] > 0: b[i] -= 1
            np[i] = (r[i], g[i], b[i])
        np.write()
        time.sleep(0.15)
        
        
def bedtime(np):
    print("Bedtime!")
    sleep = 0.01
    for i in range(n):
        np[i] = (0, 0, 0)
        np[n-i-1] = (0, 0, 0)
        np.write()
        sleep *= 1.05
        time.sleep(sleep)
    machine_reset()


def progress_bar(np):
    print("Entering Progress Bar Display Mode")
    # When you plug in, update rather than wait until the stroke of the next minute
    print("Connected to WiFi")
    np[0] = (0, int(255*dim), int(255*dim))
    np[n-1] = (0, int(255*dim), int(255*dim))
    np.write()
    # Set time and initialise variables
    set_time(worldtimeurl)
    np[0] = (0, int(255*dim), 0)
    np[n-1] = (0, int(255*dim), 0)
    np.write()
    colors = convertcolors(hexcolors)
    clockout = 0
    laststate = False
    now = time.gmtime()
    dayname = whatday(int(now[6]))
    clockout = float(schedule[dayname][0]['clockout'])
    clockin = clockout
    rotation = 0
    nowrite = False
    time.sleep(1)
    while True:
        try:
            # wipe led clean before adding the pixels that represent the bar
            if nowrite == False: 
                for i in range(n): np[i] = (0, 0, 0)
            now = time.gmtime()
            if now[3] == 4 and now[4] == 0: machine_reset()
            hoursin = float(now[3])+float(now[4])/60 + float(now[5])/3600  # hours into the day
            state = is_online(dest, laststate)
            if laststate and state == False: bedtime(np)
            if laststate == False and state: clockin = hoursin
            if state: working = atwork(clockin, clockout, hoursin)
            else: working = False
            print(f"Working={working}, clock-in={clockin}, clock-out={clockout}, hours-in={hoursin}, is_online={state}")
            if working: # These only need to be added to the bar if you're working
                for i in range(checkevery*10):
                    bar(np, hoursin, clockin, clockout, rotation, colors, n, dim)                
                    if flip: np = flipit(np, n)
                    np.write()
                    if flip: rotation += 1
                    else: rotation -= 1
                    time.sleep(.1)
            elif state and nowrite == False:
                red(np, dim, colors)
                nowrite = True
            if nowrite == False: np.write()
            gc.collect()  # clean up garbage in memory
            laststate = state
            if working == False: time.sleep(checkevery) 
        except Exception as e:
            print('Exception: ', e)
            off(np)
            time.sleep(1)
            machine.reset()
        except KeyboardInterrupt:
            off(np)


def wifi_setup_mode():
    print("Entering setup mode...")

    def ap_index(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain=AP_DOMAIN)

        return render_template(f"{AP_TEMPLATE_PATH}/index.html")

    def ap_configure(request):
        print("Saving wifi credentials...")

        with open(WIFI_FILE, "w") as f:
            json.dump(request.form, f)
            f.close()

        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{AP_TEMPLATE_PATH}/configured.html", ssid=request.form["ssid"])

    def ap_catch_all(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain=AP_DOMAIN)

        return "Not found.", 404

    server.add_route("/", handler=ap_index, methods=["GET"])
    server.add_route("/configure", handler=ap_configure, methods=["POST"])
    server.set_callback(ap_catch_all)

    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)
    server.run()
    
# Figure out which mode to start up in...
def main():
    np = neopixel.NeoPixel(machine.Pin(p), n)
    np[0] = (0, 0, int(255*dim))
    np[n-1] = (0, 0, int(255*dim))
    np.write()
    try:
        os.stat(WIFI_FILE)
        # File was found, attempt to connect to wifi...
        with open(WIFI_FILE) as f:
            wifi_credentials = json.load(f)
            ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])
            if not is_connected_to_wifi():
                # Bad configuration, delete the credentials file, reboot
                # into setup mode to get new credentials from the user.
                print("Bad wifi connection!")
                print(wifi_credentials)
                if delwifi: os.remove(WIFI_FILE)
                np[0] = (int(255*dim), 0, 0)
                np[n-1] = (int(255*dim), 0, 0)
                np.write()
                machine_reset()
            print(f"Connected to wifi, IP address {ip_address}")
            progress_bar(np)  # Contains all the progress bar code
            
    except Exception:
        # Either no wifi configuration file found, or something went wrong,
        # so go into setup mode
        if delwifi == False:
            np[0] = (int(255*dim), 0, 0)
            np[n-1] = (int(255*dim), 0, 0)
            np.write()  
            time.sleep(3)
            machine_reset()
        
        np[0] = (int(255*dim), int(255*dim), 0)
        np[n-1] = (int(255*dim), int(255*dim), 0)
        np.write()    
        wifi_setup_mode()
        
if __name__ == "__main__":
    main()

