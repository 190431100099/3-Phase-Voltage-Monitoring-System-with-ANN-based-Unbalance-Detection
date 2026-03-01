import serial
import time
import math
import random

def generate_voltage(t, amplitude, offset, noise_level):
    base = offset + amplitude * math.sin(2 * math.pi * 0.5 * t)
    noise = random.uniform(-noise_level, noise_level)
    voltage = base + noise
    return round(voltage, 2)

def main():
    port = 'COM2'  # Ganti sesuai port serial kamu
    baudrate = 9600

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Koneksi serial berhasil di {port} dengan baudrate {baudrate}")

        t = 0
        dt = 0.1  # interval 100 ms

        while True:
            # R: Gelombang kecil tapi tinggi offset
            r = generate_voltage(t, amplitude=5, offset=220, noise_level=1.5)

            # S: Gelombang lebih besar dan offset lebih rendah
            s = generate_voltage(t + 0.33, amplitude=15, offset=210, noise_level=2.5)

            # T: Sangat fluktuatif dan offset menengah
            t_val = generate_voltage(t + 0.66, amplitude=10, offset=200, noise_level=5)

            data_str = f"{r},{s},{t_val}\n"
            ser.write(data_str.encode('utf-8'))
            print(f"Dikirim: {data_str.strip()}")

            t += dt
            time.sleep(dt)

    except serial.SerialException as e:
        print(f"Error membuka port serial: {e}")

    except KeyboardInterrupt:
        print("Pengiriman dihentikan user.")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Port serial ditutup.")

if __name__ == "__main__":
    main()
