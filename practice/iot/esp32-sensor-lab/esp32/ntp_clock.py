import network
import ntptime
import time

UTC_OFFSET = 8 * 3600  # UTC+8 台灣


def connect_wifi(ssid, password, timeout=20):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return wlan
    wlan.connect(ssid, password)
    for _ in range(timeout):
        if wlan.isconnected():
            print('WiFi connected:', wlan.ifconfig())
            return wlan
        time.sleep(1)
    raise RuntimeError('WiFi connect timeout')


def sync_ntp():
    ntptime.settime()
    print('NTP synced (UTC)')


def localtime():
    t = time.time() + UTC_OFFSET
    return time.localtime(t)


def time_str():
    lt = localtime()
    return '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*lt[:6])
