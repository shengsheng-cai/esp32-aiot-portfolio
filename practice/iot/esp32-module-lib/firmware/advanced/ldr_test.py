from machine import Pin, ADC
import time

a = ADC(Pin(35))
a.atten(ADC.ATTN_11DB)
a.width(ADC.WIDTH_12BIT)

while True:
    print("LDR:", a.read())
    time.sleep_ms(500)
