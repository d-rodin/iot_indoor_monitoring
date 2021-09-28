from network import WLAN
import time
import machine
wlan = WLAN(mode=WLAN.STA)

wlan.connect(ssid='YOUR_WIFI_SSID', auth=(WLAN.WPA2, 'WIFI_PASSWD'))
while not wlan.isconnected():
    #time.sleep(5)
    machine.idle()
print("WiFi connected succesfully")
print(wlan.ifconfig())
