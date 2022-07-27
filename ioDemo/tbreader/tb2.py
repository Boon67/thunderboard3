
import sys
import time
import asyncio
import logging
import tbProperites 

from bleak import discover
from bleak import BleakClient
import struct
#from ble_const import *
WAITTIME=1 #Time to wait between calls

RED=0
GREEN=64
BLUE=0
LIGHT=15

async def readThunderboards():
    devices = await discover()
    for d in devices:
        if "Thunder Sense" in d.name:
            print(d.name + '::' + d.address ) 
            await list_Services(d.address, True)

async def list_Services(address, debug=False):
    log = logging.getLogger(__name__)
    if debug:
        log.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        log.addHandler(h)

    async with BleakClient(address) as client:
        x = await client.is_connected()
        log.info("Connected: {0}".format(x))
        value = await client.read_gatt_char(tbProperites.thunderboardProps.UUID_CHARACTERISTIC_RGB_LEDS)
        print("LED Data Value: {0}".format(value))
        COLOR=bytearray([LIGHT,RED,GREEN,BLUE])
        print(COLOR)
        await client.write_gatt_char(UUID_CHARACTERISTIC_RGB_LEDS, COLOR)

        for service in client.services:
            log.info("[Service] {0}: {1}".format(service.uuid, service.description))
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = bytes(await client.read_gatt_char(char.uuid))
                    except Exception as e:
                        value = str(e).encode()
                else:
                    value = None
                if (value!=None):
                    #Formatting to regular values for known characteristics
                    if (char.uuid==UUID_CHARACTERISTIC_UV_INDEX):
                        value = ord(value)
                    if (char.uuid==UUID_CHARACTERISTIC_HUMIDITY):
                        value = struct.unpack('<H', value)
                        value = value[0] / 100
                    if (char.uuid==UUID_CHARACTERISTIC_TEMPERATURE):
                        value = struct.unpack('<H', value)
                        value = value[0] / 100
                    if (char.uuid==UUID_CHARACTERISTIC_PRESSURE):
                        value = struct.unpack('<L', value)
                        value = value[0] / 1000
                    if (char.uuid==UUID_CHARACTERISTIC_AMBIENT_LIGHT_REACT):
                        value = struct.unpack('<L', value)
                        value = value[0] / 100
                    if (char.uuid==UUID_CHARACTERISTIC_SOUND_LEVEL):
                        value = struct.unpack('<h', value)
                        value = value[0] / 100
                    if (char.uuid==UUID_CHARACTERISTIC_CO2_READING):
                        value = struct.unpack('<h', value)
                        value = value[0]
                    if (char.uuid==UUID_CHARACTERISTIC_TVOC_READING):
                        value = struct.unpack('<h', value)
                        value = value[0]
                    if (char.uuid==UUID_CHARACTERISTIC_POWER_SOURCE):
                        value = ord(value)
                    log.info(
                        "\t[Characteristic] {0}: (Handle: {1}) ({2}) | Name: {3}, Value: {4} ".format(
                            char.uuid,
                            char.handle,
                            ",".join(char.properties),
                            char.description,
                            value
                        )
                    )
                for descriptor in char.descriptors:
                    value = await client.read_gatt_descriptor(descriptor.handle)
                    log.info(
                        "\t\t[Descriptor] {0}: (Handle: {1}) | Value: {2} ".format(
                            descriptor.uuid, descriptor.handle, value
                        )
                    )


        if await client.is_connected():
            await client.disconnect()

loop = asyncio.get_event_loop()
while 0!=1:
    loop.run_until_complete(readThunderboards())
    time.sleep(WAITTIME)