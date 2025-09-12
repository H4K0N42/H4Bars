# Bedtime: A progress bar that shows your Bedtime

###### Forked from [veebch/hometime](https://github.com/veebch/hometime)

A physical LED progress bar for your day that shows the time remaining until your configured bedtime. The bar uses an addressable LED strip and a Raspberry Pi Pico W. It:

- keeps you posted on how much time has passed since you started your PC,
- shows the progression toward your bedtime,
- Turns red when your set bedtime is reached

## How it works

The progress bar displays your progress toward your configured bedtime. It connects to Wi-Fi, grabs the current time from a [time API](https://timeapi.io), then shows you how much time has passed since you started your PC and how far you are from your bedtime.

## Hardware

- Raspberry Pi Pico W
- 5V Addressable LED strip (we used a 1 m, 144 LED, WS2812B Eco).

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
git clone https://github.com/H4K0N42/bedtime.git
cd bedtime
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

**Note:** Make sure you have set up an HTTP server on your PC (it can serve a blank webpage)

## Configuration

Set your wifi + password in `wifi.json`.

The parameters are in `config.py`.

That's it. Now whenever you plug it in to power, the code will autorun.
