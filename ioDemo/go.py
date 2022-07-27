#!/usr/bin/python

import socket
import argparse
import time
import datetime
import json
import sys
import signal
import LCD_1in44
import LCD_Config
import Image
import ImageDraw
import ImageFont
import ImageColor
import RPi.GPIO as GPIO


# Defaults
BASETOPIC = "device/v1/event/"
LASTINPUT = ""
mqtt = {}
BGCOLOR = "BLACK"
TEXT1_COLOR = "RED"
TEXT2_COLOR = "WHITE"
FONT = ImageFont.truetype("./arial.ttf", 11)
FONT2 = ImageFont.truetype("./arial.ttf", 10)
IPADDR = ""

pinObject = [
    {"name": "Key1", "pin": 21, "mode": GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Key2", "pin": 20, "mode": GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Key3", "pin": 16, "mode": GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Up", "pin": 6, "mode": GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Down", "pin": 19, "mode": GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Left", "pin": 5, "mode": GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Right", "pin": 26, "mode": GPIO.IN, "method": GPIO.PUD_UP},
    {"name": "Click", "pin": 13, "mode": GPIO.IN, "method": GPIO.PUD_UP}
]


LCD = LCD_1in44.LCD() # LCD Module
RUN=True
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
LCD.LCD_Init(Lcd_ScanDir) 


def parse_args(argv):
    """Parse the command line arguments"""

    parser.add_argument('--deviceID', default="waveshareio", required=True,
                        help='The id/name of the device that will be used for device \
                        authentication against the ClearBlade Platform or Edge, defined \
                        within the devices table of the ClearBlade platform.')

    parser.add_argument('--messagingUrl', dest="messagingURL", default="localhost",
                        help='The MQTT URL of the ClearBlade Platform or Edge the adapter will \
                        connect to. The default is https://localhost.')

    parser.add_argument('--logLevel', dest="logLevel", default="INFO", choices=['CRITICAL',
                        'ERROR', 'WARNING', 'INFO', 'DEBUG'], help='The level of logging that \
                        should be utilized by the adapter. The default is "INFO".')

    return vars(parser.parse_args(args=argv[1:]))


def drawText(img, text, x, y, color):
    draw = ImageDraw.Draw(img)
    shift = 5
    pos = (x, y+shift)
    draw.line([x, y+shift, (LCD.width, y+shift)], fill=BGCOLOR, width=10)
    draw.text((x, y), text, font=FONT, fill=color)
    return img


def initLCD():

    bootImg = Image.new("RGB", (LCD.width, LCD.height), "Purple")
    LCD.LCD_ShowImage(bootImg, 0, 0)


def clearLCD():
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
    bootImg = Image.new("RGB", (LCD.width, LCD.height), "Blue")
    LCD.LCD_ShowImage(bootImg, 0, 0)


def baseImage():
    img = imgResize("logo.png", (LCD.width, LCD.height))
    baseInfo(img)
    return img


def clock(value):
    global LASTINPUT
    LASTINPUT = value
    px = 42
    py = 2
    pos = (LCD.width-px, py)
    ts = time.time()
    t = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    draw = ImageDraw.Draw(img)
    draw.line([pos, (LCD.width, py)], fill=BGCOLOR, width=20)
    draw.text(pos, t, font=FONT2, fill="GREEN")

    draw.line([10, 5, (50, 5)], fill=BGCOLOR, width=20)
    draw.text((10, 5), LASTINPUT, TEXT1_COLOR)
    baseInfo(img)
    LCD.LCD_ShowImage(img, 0, 0)


def baseInfo(img):
    IPADDR = ""
    try:
        IPADDR = ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(
            ("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])
        img = drawText(img, "Host: " + socket.gethostname(),
                       5, LCD.height-28, TEXT2_COLOR)
        img = drawText(img, "IP: " + IPADDR, 5, LCD.height-15, TEXT2_COLOR)
    except:
        img = drawText(img, "Initializing.....", 5, LCD.height-15, TEXT2_COLOR)


def imgResize(path_to_image, thumbnail_size=(128, 128)):
    background = Image.new('RGBA', thumbnail_size, BGCOLOR)
    source_image = Image.open(path_to_image).convert("RGBA")
    source_image.thumbnail(thumbnail_size)
    (w, h) = source_image.size
    background.paste(
        source_image, ((thumbnail_size[0] - w) / 2, (thumbnail_size[1] - h) / 2))
    return background

# The function will be called when the interrupt triggers.


def KeyPressInterrupt(KEY):
    for attrs in pinObject:
        if attrs['pin'] == KEY:
            value = attrs['name']
            print(value)
            #img=drawText(img, value, 10,5,TEXT1_COLOR)
            clock(value)
            LCD.LCD_ShowImage(img, 0, 0)
            break


def initGPIO():
    # pin numbers are interpreted as BCM pin numbers.
    GPIO.setmode(GPIO.BCM)
    for p in pinObject:
        GPIO.setup(p["pin"], p["mode"], p["method"])
        GPIO.add_event_detect(p["pin"], GPIO.FALLING,
                              KeyPressInterrupt, 200)  # Key Down
        # GPIO.add_event_detect(p["pin"], GPIO.RISING, KeyPressInterrupt, 200) #Key Up

def handler_stop_signals(signum, frame):
    global RUN
    RUN = False
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
    #LCD.LCD_Init(Lcd_ScanDir)
    #LCD.LCD_Init(Lcd_ScanDir)
    bootImg = Image.new("RGB", (LCD.width, LCD.height), "Blue")
    LCD.LCD_ShowImage(bootImg, 0, 0)

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)
signal.signal(signal.SIGQUIT, handler_stop_signals)

img=baseImage()

def main():
    initLCD()
    initGPIO()
    while RUN:
        clock(LASTINPUT)
        time.sleep(1)

if __name__ == '__main__':
    print('Starting Up......')
    main()
