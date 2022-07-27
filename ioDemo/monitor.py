#!/usr/bin/python
import socket, argparse, time, json, sys
import LCD_1in44, LCD_Config
import Image, ImageDraw, ImageFont, ImageColor
import RPi.GPIO as GPIO
import subprocess
from uuid import getnode
import socket
from time import sleep

import requests
from datetime import datetime
from uuid import getnode
import socket
from time import sleep
from bluepy.btle import *
from requests.exceptions import ConnectionError, ReadTimeout

DEVICE_ADDR = '00:0B:57:4E:DC:8B'
INTERVAL_SECONDS = 5
INTERVAL_SECONDS_ACCEL = 2
SLEEP_ON_RESET = 5
DEBUG = False

BATT_SERVICE = '180F' 
UI_SERVICE = 'fcb89c40-c600-59f3-7dc3-5ece444a401b'
MOTION_SERVICE = 'a4e649f4-4be5-11e5-885d-feff819cdc9f'  # Also called 'inertial measurment'
ENVIRONMENTAL_SERVICE = '181A'
GENERAL_ACCESS_SERVICE = '1800'
AIR_QUALITY_SERVICE = 'efd658ae-c400-ef33-76e7-91b00019103b'
IO_SERVICE = '1815'

ACCEL_CHAR = 'c4c1f6e2-4be5-11e5-885d-feff819cdc9f'
ORIENT_CHAR = 'b7c4b694-bee3-45dd-ba9f-f3b5e994f49a'
BATTERY_CHAR = "2a19"
TEMP_CHAR = "2a6e"
HUMIDITY_CHAR = "2a6f"
PRESSURE_CHAR = "2A6D"
COMMAND_CHAR = "71e30b8c-4131-4703-b0a0-b0bbba75856b"
CO2_CHAR = 'efd658ae-c401-ef33-76e7-91b00019103b'
VOC_CHAR = 'efd658ae-c402-ef33-76e7-91b00019103b'


LED_CHAR = "2a56"

# Defaults
LASTINPUT=""
BGCOLOR="BLACK"
TEXT1_COLOR="RED"
TEXT2_COLOR="WHITE"
FONT = ImageFont.truetype("./arial.ttf", 11)
FONT2 = ImageFont.truetype("./arial.ttf", 10)
IPADDR=""

pinObject = [
    {"name": "Key1", "pin": 21, "mode":GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Key2", "pin": 20, "mode":GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Key3", "pin": 16, "mode":GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Up", "pin": 6, "mode":GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Down", "pin": 19, "mode":GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Left", "pin": 5, "mode":GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Right", "pin": 26, "mode":GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Click", "pin": 13, "mode":GPIO.IN, "method": GPIO.PUD_UP}
]

LCD = LCD_1in44.LCD() #LCD Module

def create_event(session, stream, data):
    """
    Sends an event to the sandbox
    :param session: Requests session to post to
    :param stream: Stream to send the data to
    :param data: JSON data
    :param add_ip: String of an IP address. If included, is sent along with the data
    :param debug: Optional file to write to if you are in debug mode
    :return: nothing
    """
    clock(LASTINPUT)
    print("{}: Sending event. data: {}".format(datetime.utcnow(), json.dumps(data)))
    x1=5
    x2=80
    y1=15
    y2=25
    y3=35
    key="temperature"
    if key in data.keys(): 
        print(key, data[key])
        drawText(img, "temp:" + str(data[key]), x1,y1,"Cyan")

    key="humidity"
    if key in data.keys(): 
        print(key, data[key])
        drawText(img, "hum:" + str(data[key]), x1,y2,"Cyan")

    key="co2"
    if key in data.keys(): 
        print(key, data[key])
        drawText(img, key+ ":" + str(data[key]), x2,y3,"Red")

    key="voc"
    if key in data.keys(): 
        print(key, data[key])
        drawText(img, "voc:" + str(data[key]), x2,y1,"Cyan")

    key="pressure"
    if key in data.keys(): 
        print(key, data[key])
        drawText(img, "pres:" + str(data[key]), x1,y3,"Green")

    key="light"
    if key in data.keys(): 
        print(key, data[key])
        drawText(img, "light:" + str(data[key]), x2,y3,"Cyan")

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val -= 1 << bits
    return val


class AccelerationDelegate(DefaultDelegate):
    """
    This class reads the acceleration data from the board as it comes in as notifications.
    We manually put in a limit of max 1 event containing acceleration data to the cloud to avoid using
    too many credits. We also calculate a min, max, and average as the data comes in.
    For more information see: https://ianharvey.github.io/bluepy-doc/delegate.html
    """
    def __init__(self, session, motionGATT, debug = None):
        DefaultDelegate.__init__(self)
        self.session = session
        self.motionGATT = motionGATT
        self.last_motion_detected = datetime.utcnow()

        self.x_vals = []
        self.y_vals = []
        self.z_vals = []

        self.x_max = None
        self.y_max = None
        self.z_max = None

        self.x_min = None
        self.y_min = None
        self.z_min = None

        self.debug = debug

    def handleNotification(self, cHandle, data):
        if cHandle == self.motionGATT and type(data) == str:
            x_accel = abs((twos_comp((ord(data[1]) << 8) + ord(data[0]), 16)) / 1000.)
            y_accel = abs((twos_comp((ord(data[3]) << 8) + ord(data[2]), 16)) / 1000.)
            z_accel = abs((twos_comp((ord(data[5]) << 8) + ord(data[4]), 16)) / 1000.)
            self.x_vals.append(x_accel)
            self.y_vals.append(y_accel)
            self.z_vals.append(z_accel)

            self.x_max = max(self.x_max, x_accel) if self.x_max else x_accel
            self.y_max = max(self.y_max, y_accel) if self.y_max else y_accel
            self.z_max = max(self.z_max, z_accel) if self.z_max else z_accel

            self.x_min = min(self.x_min, x_accel) if self.x_min else x_accel
            self.y_min = min(self.y_min, y_accel) if self.y_min else y_accel
            self.z_min = min(self.z_min, z_accel) if self.z_min else z_accel

            if (datetime.utcnow() - self.last_motion_detected).total_seconds() > INTERVAL_SECONDS_ACCEL:
                json_data = {
                    'x_min': self.x_min,
                    'y_min': self.y_min,
                    'z_min': self.z_min,
                    'x_max': self.x_max,
                    'y_max': self.y_max,
                    'z_max': self.z_max,
                    'x_avg': sum(self.x_vals) / len(self.x_vals),
                    'y_avg': sum(self.y_vals) / len(self.y_vals),
                    'z_avg': sum(self.z_vals) / len(self.z_vals)
                }

                try:
                    create_event(self.session, 'sensor_data', json_data)
                except ConnectionError as ce:
                    print("Connection error, resetting session: {}\n".format(ce.message))
                    if self.debug:
                        print("Connection error, resetting session: {}\n".format(ce.message))
                    self.session.close()
                    self.session = requests.session()
                    sleep(SLEEP_ON_RESET)
                except ReadTimeout as re:
                    print("Internet connection lost during read, resetting session: {}\n".format(re.message))
                    if self.debug:
                        print("Internet connection lost during read, resetting session: {}\n".format(re.message))
                    self.session.close()
                    self.session = requests.session()
                    sleep(SLEEP_ON_RESET)
                self.last_motion_detected = datetime.utcnow()
                self.x_vals = []
                self.y_vals = []
                self.z_vals = []

                self.x_max = None
                self.y_max = None
                self.z_max = None

                self.x_min = None
                self.y_min = None
                self.z_min = None

def run(ble, debug=None):
    """
    Once connected to the thundersense, tries to connect to Medium One through the internet. If it cannot connect,
    it will maintain the connection with the thundersense and keep trying to connect to the cloud until it is successful.
    After that, it collects the data and sends it to the cloud as long as the connection is maintained
    :param ble:
    :param debug:
    :return:
    """
    session = requests.session()
    while True: # Keep trying to send init event until you can connect
        try:
            print(session)
            break
        except ConnectionError as ce:
            print("Connection error, resetting session: {}\n".format(ce.message))
            if debug:
                print("Connection error, resetting session: {}\n".format(ce.message))
            session.close()
            session = requests.session()
            sleep(INTERVAL_SECONDS)
        except ReadTimeout as re:
            print("Internet connection lost during read, resetting session: {}\n".format(re.message))
            if debug:
                print("Internet connection lost during read, resetting session: {}\n".format(re.message))
            session.close()
            session = requests.session()
            sleep(SLEEP_ON_RESET)
    envService = ble.getServiceByUUID(ENVIRONMENTAL_SERVICE)
    battService = ble.getServiceByUUID(BATT_SERVICE)
    motionService = ble.getServiceByUUID(MOTION_SERVICE)
    airQualityService = ble.getServiceByUUID(AIR_QUALITY_SERVICE)
    io_service = ble.getServiceByUUID(IO_SERVICE)

    accel_chars = motionService.getCharacteristics(forUUID=ACCEL_CHAR)
    temperature_chars = envService.getCharacteristics(forUUID=TEMP_CHAR)
    humidity_chars = envService.getCharacteristics(forUUID=HUMIDITY_CHAR)
    pressure_chars = envService.getCharacteristics(forUUID=PRESSURE_CHAR)
    bat_chars = battService.getCharacteristics(forUUID=BATTERY_CHAR)
    co2_chars = airQualityService.getCharacteristics(forUUID=CO2_CHAR)
    voc_chars = airQualityService.getCharacteristics(forUUID=VOC_CHAR)
    light_chars = io_service.getCharacteristics(forUUID=LED_CHAR)

    ble.setDelegate(AccelerationDelegate(requests.session(), accel_chars[0].getHandle(), debug= debug))

    # Turn on acceleration data
    for accel_char in accel_chars:
        if 'NOTIFY' in accel_char.propertiesToString():
            setup_data = b"\x01\x00"
            notify_handle = accel_char.getHandle() + 1
            ble.writeCharacteristic(notify_handle, setup_data, withResponse=True)
    last_motion_detected = datetime.utcnow()
    while True:
        json_data = {}
        for bat_char in bat_chars:
            if bat_char.supportsRead():
                bat_data = bat_char.read()
                if type(bat_data) == str:
                    bat_data_value = ord(bat_data[0])
                    json_data['battery'] = bat_data_value
        for temperature_char in temperature_chars:
            if temperature_char.supportsRead():
                temperature_data = temperature_char.read()
                if type(temperature_data) == str:
                    temperature_data_value = ((twos_comp((ord(temperature_data[1]) << 8) + ord(temperature_data[0]),
                                                        16)) / 100. ) * 1.8 + 32.
                    json_data['temperature'] = temperature_data_value

        for humidity_char in humidity_chars:
            if humidity_char.supportsRead():
                humidity_data = humidity_char.read()
                if type(humidity_data) == str:
                    humidity_data_value = (twos_comp((ord(humidity_data[1]) << 8) + ord(humidity_data[0]), 16)) / 100.
                    json_data['humidity'] = humidity_data_value

        for pressure_char in pressure_chars:
            if pressure_char.supportsRead():
                # Unsigned int 32 bit
                pressure_data = pressure_char.read()
                if type(pressure_data) == str:
                    pressure_data_value = ((ord(pressure_data[3]) << 24) + (ord(pressure_data[2]) << 16) + (
                    ord(pressure_data[1]) << 8) + ord(pressure_data[0])) / 1000.
                    json_data['pressure'] = pressure_data_value

        for co2_char in co2_chars:
            if co2_char.supportsRead():
                # Unsigned int 16 bit
                co2_data = co2_char.read()
                if type(co2_data) == str:
                    co2_data_value = ((ord(co2_data[1]) << 8) + ord(co2_data[0]))
                    json_data['co2'] = co2_data_value

        for voc_char in voc_chars:
            if voc_char.supportsRead():
                # Unsigned int 16 bit
                voc_data = voc_char.read()
                if type(voc_data) == str:
                    voc_data_value = ((ord(voc_data[1]) << 8) + ord(voc_data[0]))
                    json_data['voc'] = voc_data_value
        if (datetime.utcnow() - last_motion_detected).total_seconds() > INTERVAL_SECONDS:
            # Blink light
            for light_char in light_chars:
                if "WRITE" in light_char.propertiesToString():
                    light_char.write("01".decode("hex"), True)
                    light_char.write("00".decode("hex"), True)
                    light_char.write("01".decode("hex"), True)
                    light_char.write("00".decode("hex"), True)
            try:
                create_event(session, 'sensor_data', json_data)
            except ConnectionError as ce:
                print("Connection error, resetting session: {}\n".format(ce.message))
                if debug:
                    print("Connection error, resetting session: {}\n".format(ce.message))
                session.close()
                session = requests.session()
                sleep(SLEEP_ON_RESET)
            except ReadTimeout as re:
                print("Internet connection lost during read, resetting session: {}\n".format(re.message))
                if debug:
                    print("Internet connection lost during read, resetting session: {}\n".format(re.message))
                session.close()
                session = requests.session()
                sleep(SLEEP_ON_RESET)
            last_motion_detected = datetime.utcnow()



def parse_args(argv):
    """Parse the command line arguments"""

    parser.add_argument('--deviceID', default="waveshareio", required=True, \
                        help='The id/name of the device that will be used for device \
                        authentication against the ClearBlade Platform or Edge, defined \
                        within the devices table of the ClearBlade platform.')

  
    parser.add_argument('--messagingUrl', dest="messagingURL", default="localhost", \
                        help='The MQTT URL of the ClearBlade Platform or Edge the adapter will \
                        connect to. The default is https://localhost.')

  
    parser.add_argument('--logLevel', dest="logLevel", default="INFO", choices=['CRITICAL', \
                        'ERROR', 'WARNING', 'INFO', 'DEBUG'], help='The level of logging that \
                        should be utilized by the adapter. The default is "INFO".')

    return vars(parser.parse_args(args=argv[1:]))

def drawText(img, text, x, y, color):
    draw = ImageDraw.Draw(img)
    shift=5
    pos=(x,y+shift)
    draw.line([x,y+shift, (LCD.width,y+shift)], fill=BGCOLOR, width=10)
    draw.text((x, y), text, font = FONT, fill = color)
    return img

def initLCD():
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
    LCD.LCD_Init(Lcd_ScanDir)
    LCD.LCD_Init(Lcd_ScanDir)
    bootImg = Image.new("RGB", (LCD.width, LCD.height), "Purple")
    LCD.LCD_ShowImage(bootImg,0,0)

def baseImage():
    img=imgResize("logo.png", (LCD.width,LCD.height))
    baseInfo(img)
    return img

def clock(value):
    global LASTINPUT
    LASTINPUT=value
    px=42
    py=2
    pos=(LCD.width-px,py)
    ts=time.time()
    t=datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    draw = ImageDraw.Draw(img)
    draw.line([pos, (LCD.width,py)], fill=BGCOLOR, width=20)
    draw.text(pos, t, font = FONT2, fill = "GREEN")

    draw.line([10,5, (50,5)], fill=BGCOLOR, width=20)
    draw.text((10,5),LASTINPUT,TEXT1_COLOR)
    baseInfo(img)
    LCD.LCD_ShowImage(img,0,0)

def baseInfo(img):
    IPADDR=""
    try:
        IPADDR=((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])
        img=drawText(img, "Host: " + socket.gethostname(), 5,LCD.height-28,TEXT2_COLOR)
        img=drawText(img, "IP: " + IPADDR, 5, LCD.height-15, TEXT2_COLOR)  
    except:
        img=drawText(img, "Initializing.....", 5, LCD.height-15, TEXT2_COLOR)

def imgResize(path_to_image, thumbnail_size=(128,128)):
    background = Image.new('RGBA', thumbnail_size, BGCOLOR)    
    source_image = Image.open(path_to_image).convert("RGBA")
    source_image.thumbnail(thumbnail_size)
    (w, h) = source_image.size
    background.paste(source_image, ((thumbnail_size[0] - w) / 2, (thumbnail_size[1] - h) / 2 ))
    return background

# The function will be called when the interrupt triggers.
def KeyPressInterrupt(KEY):
    for attrs in pinObject:
        if attrs['pin'] == KEY:
            value = attrs['name']
            print(value)
            #img=drawText(img, value, 10,5,TEXT1_COLOR)
            clock(value)
            LCD.LCD_ShowImage(img,0,0)
            break

def initGPIO():
# pin numbers are interpreted as BCM pin numbers.
    GPIO.setmode(GPIO.BCM)
    for p in pinObject:
        GPIO.setup(p["pin"], p["mode"], p["method"]) 
        GPIO.add_event_detect(p["pin"], GPIO.FALLING, KeyPressInterrupt, 200) #Key Down
        #GPIO.add_event_detect(p["pin"], GPIO.RISING, KeyPressInterrupt, 200) #Key Up

img=baseImage()
#try:
def main():
    initLCD()
    initGPIO()
    ble = Peripheral()
# print("GPIO Listeners Initialized")
    while True:
        try:
            ble.connect(DEVICE_ADDR, 'public')
            break
        except BTLEException as be:
            print("Could not connect to device : " + be.message)
            if DEBUG:
                print("{}: Could not connect to device : {}\n".format(datetime.utcnow(), be.message))
            sleep(SLEEP_ON_RESET)
    run(ble)

if __name__ == '__main__':
    print('Starting Up......')
    main()

