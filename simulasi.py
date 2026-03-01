import serial
import time
import random

# Ganti dengan COM port virtual yang dipasangkan ke aplikasi GUI Anda
port = "COM1"  # contoh: COM5
baudrate = 9600

ser = serial(port, baudrate)

try:
    while True:
        r = round(random.uniform(210.0, 230.0), 1)
        s = round(random.uniform(210.0, 230.0), 1)
        t = round(random.uniform(210.0, 230.0), 1)
        line = f"{r},{s},{t}\n"
        ser.write(line.encode())
        print("", line.strip())
        time.sleep(1)
except KeyboardInterrupt:
    ser.close()
