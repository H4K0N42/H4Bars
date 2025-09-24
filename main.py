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

from phew import connect_to_wifi, is_connected_to_wifi
import machine      # type: ignore
import time
import config
import urequests    # type: ignore
import neopixel     # type: ignore
import math
import json
import rp2          # type: ignore
import gc

# Time with daylight savings time and time zone factored in, edit this to fit where you are
worldtimeurl = "https://timeapi.io/api/TimeZone/zone?timezone=" + config.TIMEZONE
p = config.GPIOPIN          # GPIO pin that data line of lights is connected to
calendar_id = config.CALENDAR
google_key = config.APIKEY
hexcolors = config.COLORS
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
time.sleep(1)
led.on()
checkevery = config.REFRESH   # Number of seconds for interval refreshinag neopixel
dim = config.DIM
rweekends = config.REMOVE_WEEKENDS

def machine_reset():
    print("Resetting...")
    time.sleep(1)
    machine.reset()


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


def update():
    global daystotal, daysleft

    def count_workdays(start_ts, end_ts):
        count = 0
        ts = start_ts
        while ts <= end_ts:
            if time.gmtime(ts)[6] < 5:  # Day is weekday
                count += 1
            ts += 86400                 # 86400s = 1d
        return count

    led.on()
    now = time.gmtime()
    day = time.mktime((now[0], now[1], now[2], 0, 0, 0, 0, 0))
    
    start, end = google_cal(calendar_id, google_key)
    start -= 86400
    
    if rweekends:
        daystotal = count_workdays(start, end)
        daysleft = count_workdays(day, end)
    else:
        daystotal = (end - start) // 86400
        daysleft = (end - day) // 86400
    
    print(f"now={now}")
    print(f"daystotal={daystotal}")
    print(f"daysleft={daysleft}")
    led.off()
    return now
    
    
def google_cal(calendar_id, api_key):
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    url += f"?key={api_key}"

    response = urequests.get(url)
    data = response.json()

    tth_items = []
    
    for item in data.get("items", []):
        if "tth" in item["summary"]:
            y, m, d = item["start"]["date"].split("-")
            tm = (int(y), int(m), int(d), 0, 0, 0, 0, 0)
            tth_items.append(time.mktime(tm))
    tth_items.sort()
    return tth_items[-2], tth_items[-1]


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

    
def bar(np, c):
    for i in range(daystotal):
        np[i] = c[0]
        np.write()
        time.sleep(.025)
    
    while rp2.bootsel_button() == 1:
        time.sleep(.1)
    time.sleep(1)
    
    for i in reversed(range(daysleft, daystotal)):
        color = getcolor(c, daystotal, daystotal-i, dim)
        for j in range(daystotal): np[j] = color
        for j in range(i, daystotal): np[j] = (0, 0, 0)
        np.write()
        time.sleep(.05)
    
    for i in range(10*10):
        if rp2.bootsel_button() == 1:
            led.off()
            while rp2.bootsel_button() == 1: time.sleep(0.1)
            break
        time.sleep(.1)
        
    for i in reversed(range(daysleft)):
        np[i] = (0, 0, 0)
        np.write()
        time.sleep(.025)

def off(np):
    print('Turn off all LEDs')
    for i in range(daystotal):
        np[i] = (0, 0, 0)
        np.write()


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
        color = tuple(int(round(c * dim)) for c in colors[-1])
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
        
        
def progress_bar(np):
    print("Entering Progress Bar Display Mode")
    np[0] = (0, int(255*dim), int(255*dim))
    np.write()
    set_time(worldtimeurl)
    np[0] = (0, int(255*dim), 0)
    np.write()
    colors = convertcolors(hexcolors)
    now = update()
    bar(np, colors)
    while True:
        for i in range(checkevery*10):
            if rp2.bootsel_button() == 1:
                led.on()
                bar(np, colors)
                led.off()
                update()
            time.sleep(.1)
        gc.collect()
        now = update()
        if now[3] == 4 and now[4] <= 10: machine_reset()


   
def main():
    np = neopixel.NeoPixel(machine.Pin(p), 150)
    np[0] = (0, 0, int(255*dim))
    np.write()
    with open('wifi.json') as f:
        wifi_credentials = json.load(f)
        ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])
        if not is_connected_to_wifi():
            print("Bad wifi connection!")
            print(wifi_credentials)
            np[0] = (int(255*dim), 0, 0)
            np.write()
            machine_reset()
        print(f"Connected to wifi, IP address {ip_address}")
        progress_bar(np)
            
        
if __name__ == "__main__":
    main()

