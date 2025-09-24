# Calendar

TIMEZONE = "Europe/Berlin"
SCHEDULE = {                                    # Input your bedtime (9.5 = 09:30 AM; 13 = 01:00 PM; 0 = OFF)
    "monday":     [{"clockout": "22.5"}],
    "tuesday":    [{"clockout": "22.5"}],
    "wednesday":  [{"clockout": "22.5"}],
    "thursday":   [{"clockout": "22.5"}],
    "friday":     [{"clockout": "0"}],
    "saturday":   [{"clockout": "0"}],
    "sunday":     [{"clockout": "22.5"}]
}

# Neopixel

PIXELS = 144                                    # The number of pixels on the neopixel strip
GPIOPIN = 15                                    # The pin that the signal wire of the LED strip is connected to
FLIP = False                                    # Set to True if you want to flip the bar

REFRESH = 30                                    # Seconds between time updates and ping
COLORS = [                                      # Pick any number of colors you like
    "#0000ff",
    "#00a0ff",
    "#a000ff",
    "#00a0ff",
    "#0040ff"
]
DIM = 0.5                                       # Brightness of the Pixels 0..1; 1 = 100%

# Other

DELWIFI = False                                 # Deletes wifi credentials if the connection fails
USE_HTTP = True                                 # If False, Bootsel button is used for clockin / clockout
PING = "http://192.168.178.42:80"               # Online when an HTTP server responds with status 200