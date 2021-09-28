import time
import pycom
import icons
import ujson
import ubinascii
from mqtt import MQTTClient
from machine import Pin, I2C
from dht import DHT # https://github.com/JurassicPork/DHT_PyCom
import SSD1306  # for the oled screen


i2c = I2C(0)
i2c = I2C(0, I2C.MASTER)
i2c = I2C(0, pins=('P9','P10')) # create and use default PIN assignments (P9=SDA, P10=SCL)
i2c.init(I2C.MASTER, baudrate=10000) # init as a master

th = DHT(Pin('P23', mode=Pin.OPEN_DRAIN), 0) # Type 0 = dht11

'''
Import and define parameters for the SSD1306 OLED-screen.

'''

import CCS811
ccs = CCS811.CCS811(i2c=i2c,addr=90)

OLED_WIDTH = 128
OLED_HEIGHT = 64

# initalize the ssd1306 oled screen
oled = SSD1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
black = 0x000000 # Black color

# draw a black rectangle as a way to clear the screen
def clear_oled(oled):
    oled.fill_rect(0,0,OLED_WIDTH,OLED_HEIGHT,black)

# draw a symbol from icons.py list-icons
def draw_symbol(oled, shape, x=0, y=0):
    for i, row in enumerate(shape):
        for j, c in enumerate(row):
            oled.pixel(j+x, i+y, c)

def sub_cb(topic, msg):
   print(msg)

#topic_pub = 'devices/indoorenv/'
#topic_sub = 'devices/indoorenv/control'
broker_url = '192.168.1.254'
client_id = '1'

client = MQTTClient(client_id, 'BROKER_IPADDRESS', port=1883)
client.set_callback(sub_cb)
client.connect()
client.subscribe(topic="devices/indoorenv/control")

'''
 Loop to get env. readings and control LoPy4 RGB-LED
 according to temperature.
'''

while True:
    time.sleep(5) # give the sensor some breathing room ...
    ccs.data_ready() # read from CSS811
    eco2 = ccs.eCO2
    tVOC = ccs.tVOC

    result = th.read()
    while not result.is_valid():
        time.sleep(.5)
        result = th.read()

    if result.temperature < 20:
        pycom.rgbled(0x000011)
    elif result.temperature > 25:
        pycom.rgbled(0x110000)
    else:
        pycom.rgbled(0x001100)

    #print("Temp (DHT11): "+str(result.temperature)+chr(176)+"C")
    #print("rH (DHT11): "+str(result.humidity)+"%")
    #print("eCO2 (CCS811): "+str(eco2)+" ppm")
    #print("tVOC (CCS811): "+str(tVOC)+" ppb")

    clear_oled(oled)
    draw_symbol(oled,icons.temp,0,0)
    oled.text("Temp: "+str(result.temperature)+"C",32,15)
    draw_symbol(oled,icons.rh,0,34)
    oled.text("rH: "+str(result.humidity)+"%",32,49)
    oled.show()
    time.sleep(10)
    clear_oled(oled)
    draw_symbol(oled,icons.co2,0,0)
    oled.text("eCO2: "+str(eco2)+" ppm",32,15)
    draw_symbol(oled,icons.tvoc,0,34)
    oled.text("tVOC: "+str(tVOC)+" ppb",32,49)
    oled.show()
    time.sleep(10)
    clear_oled(oled)
    oled.show()
    time.sleep(60)

    client.publish(topic="devices/indoorenv", msg='{"indoor_sensor": {"eco2":' + str(eco2) +
                          ',"tvoc":'+ str(tVOC) +
                          ',"temp":' + str(result.temperature) +
                          ',"rh":' + str(result.humidity) +
                          '}}')
    print('Sensor data sent!')
