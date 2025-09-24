# TTH: A progress bar that shows `t`ime `t`ill your next `h`olidays

###### Forked from [veebch/hometime](https://github.com/veebch/hometime)

A physical LED progress bar that shows the days until the next holidays. The bar uses an addressable LED strip and a Raspberry Pi Pico W. It:

- automatically reads start and end dates from your Google Calendar => no code updates needed when your holidays change,
- shows 1 px / day until your next holidays,
- changes colors dynamically based on the percentage of days completed.

## Hardware

- Raspberry Pi Pico W
- 5V Addressable LED strip (I use a 1 m, 144 LED, WS2812B).

## Assembly

Attach the Light Strip to the Pico as described below:

| [Pico GPIO](https://www.elektronik-kompendium.de/sites/raspberry-pi/bilder/raspberry-pi-pico-gpio.png) | Light Strip |
| ------------------------------------------------------------------------------------------------------ | ----------- |
| VBUS                                                                                                   | VCC         |
| GND                                                                                                    | GND         |
| 15                                                                                                     | DATA        |

### Schematic:

![Schematic](https://github.com/H4K0N42/bedtime/blob/main/images/schematic_fritzing.png)

## Installing

Download a `uf2` image and install it on the Pico W according to the [instructions](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython) on the Raspberry Pi website.

Clone this repository to your computer using the commands (from a terminal):

```
cd ~
git clone -b tth https://github.com/H4K0N42/H4Bars.git
cd H4Bars
mv config_example.py config.py
mv wifi_example.json wifi.json
```

Check the port of the pico with the port listing command:

```
python -m serial.tools.list_ports
```

Now, using the port path (in my case `/dev/ttyACM0`) copy the contents to the repository by installing [ampy](https://pypi.org/project/adafruit-ampy/) and using and the commands:

```
ampy -p /dev/ttyACM0 put main.py
ampy -p /dev/ttyACM0 put config.py
ampy -p /dev/ttyACM0 put wifi.json
ampy -p /dev/ttyACM0 put phew
ampy -p /dev/ttyACM0 put ap_templates
```

(_NB. make sure you are using the right port name, as shown in the port listing command above_)

Done! All the required files should now be on the Pico. Whenever you connect to USB power the script will autorun.

## Configuration

1. Set up your Google Calendar API key and get the public calendar link:
   - API key: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Public calendar link: Share your calendar and copy the link ending in `@group.calendar.google.com`
   - If you need help, you can follow step 4 of [this](https://medium.com/p/workday-progressbar-with-google-calendar-integration-b266aabd32a8) guide.
2. Configure parameters in `config.py`.
3. Set your Wi-Fi credentials in `wifi.json`.

The script always selects the 2 latest events with the name `tth`. The days that the events are on are included.

That's it. Now whenever you plug it in to power, the code will autorun.
