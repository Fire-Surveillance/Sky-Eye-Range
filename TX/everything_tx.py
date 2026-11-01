import time
import adafruit_bme680
import adafruit_sgp40
import board
import busio
import digitalio

import adafruit_mlx90640
import adafruit_rfm9x
import adafruit_pcf8523

import adafruit_sdcard
import storage

spi = board.SPI()
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D6)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)

rfm9x.tx_power = 20

i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)
mlx = adafruit_mlx90640.MLX90640(i2c)
print("MLX90640 Detected On I2C")
sgp = adafruit_sgp40.SGP40(i2c)
print("SGP40 Detected On I2C")
bme = adafruit_bme680.Adafruit_BME680_I2C(i2c)
print("BME680 Detected On I2C")
print([hex(i) for i in mlx.serial_number])
print("RFM9x Output Power Set To:", rfm9x.tx_power, "dBm")

rtc = adafruit_pcf8523.PCF8523(i2c)

mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ

sd_cs = digitalio.DigitalInOut(board.D10)

try:
    sd_card = adafruit_sdcard.SDCard(spi, sd_cs)
    vfs = storage.VfsFat(sd_card)
    storage.mount(vfs, "/sd")
    print("SD Card Mounted Successfully!")

    with open("/sd/Flight_Log.txt", "w") as log_file:
        log_file.write("=== Flight Data Log ===\n")
        log_file.write("Timestamp,Temperature,Humidity,Relative Humidity,Gas (BME680),Pressure,Altitude,Raw Gas (SGP40),Compensated Gas,VOC Index\n")
    print("Log File Erased And Initialized.")

except OSError as e:
    print("Failed To Mount SD Card:", e)
    sd_card = None

def get_elapsed_time(start_time):
    elapsed = time.monotonic() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    return "{:02}:{:02}:{:02}".format(hours, minutes, seconds)

def log_to_sd(data):
    if sd_card:
        try:
            with open("/sd/Flight_Log.txt", "a") as log_file:
                log_file.write(data + "\n")
            print("Data Logged To SD Card.")
        except OSError as e:
            print("Failed To Log Data To SD Card:", e)
    else:
        print("SD Card Not Available, Skipping Log.")

frame = [0] * 768

def sendImage(frame):
    imageSize = 768
    packets = 16
    packetLength = imageSize // packets

    for i in range(packets):
        j = i * packetLength
        subFrame = frame[j : j + packetLength]
        message = str(i) + ":"
        for k in subFrame:
            message += str(round(k)) + ","
        rfm9x.send(message[:-1])
    print("Image Frame Sent.")

start_time = time.monotonic()
frame_capture_time = start_time - 1

while True:
    stamp = time.monotonic()

    elapsed_time = get_elapsed_time(start_time)
    print("Elapsed Time:", elapsed_time)

    if (stamp - frame_capture_time) > 0:
        try:
            mlx.getFrame(frame)
        except ValueError:
            continue
        print("Sending Image Frame...")
        sendImage(frame)
        frame_capture_time = stamp

    temperature = bme.temperature
    humidity = bme.humidity
    relative_humidity = bme.relative_humidity
    gas = bme.gas
    pressure = bme.pressure
    altitude = bme.altitude

    compensated_raw_gas = sgp.measure_raw(temperature=temperature, relative_humidity=humidity)
    voc_index = sgp.measure_index(temperature=temperature, relative_humidity=humidity)
    spg_raw = sgp.raw

    log_entry = (
        "=== Sky Eye Range Flight Data Log ===\n"
        "Elapsed Time: {}\n"
        "Temperature: {:.1f} C\n"
        "Humidity: {:.1f}%\n"
        "Relative Humidity: {:.1f}%\n"
        "Gas (BME680): {:.1f} ohms\n"
        "Pressure: {:.1f} hPa\n"
        "Altitude: {:.2f} meters\n"
        "Raw Gas (SGP40): {:.1f}\n"
        "Compensated Raw Gas: {:.1f}\n"
        "VOC Index: {:.1f}\n"
        "======================="
    ).format(
        elapsed_time, temperature, humidity, relative_humidity, gas, pressure, altitude, spg_raw, compensated_raw_gas, voc_index
    )

    log_to_sd(log_entry)

    messages = [
        ("temp", temperature),
        ("hum", humidity),
        ("rhum", relative_humidity),
        ("gas_bme", gas),
        ("pressure", pressure),
        ("gas_spg_com", compensated_raw_gas),
        ("voc", voc_index),
        ("gas_spg", spg_raw)
    ]

    for label, value in messages:
        message = "{}:{:.1f}".format(label, value)
        print("\tSending:", message)
        rfm9x.send(message)

    time.sleep(0.1)
