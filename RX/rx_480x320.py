import os
import time
import board
import displayio
import digitalio
import terminalio
from adafruit_display_text.label import Label
from simpleio import map_range
import adafruit_hx8357
import adafruit_tsc2007
import busio
import adafruit_rfm9x

displayio.release_displays()

spi = board.SPI()

tft_cs = board.D9
tft_dc = board.D10

display_width = 480
display_height = 320

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_hx8357.HX8357(display_bus, width=display_width, height=display_height)

i2c = board.STEMMA_I2C()

irq_dio = None
tsc = adafruit_tsc2007.TSC2007(i2c, irq=irq_dio)

import time
import board
import busio
import displayio
import digitalio
import terminalio
from adafruit_display_text.label import Label
from simpleio import map_range
import adafruit_rfm9x

THRESHOLD_TEMP=25

spi = board.SPI()

cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D11)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)

number_of_colors = 64
last_color = number_of_colors - 1
palette = displayio.Palette(number_of_colors)

color_A = [
    [0, 0, 0],
    [0, 0, 255],
    [0, 255, 255],
    [0, 255, 0],
    [255, 255, 0],
    [255, 0, 0],
    [255, 255, 255],
]
color_B = [[0, 0, 255], [0, 255, 255], [0, 255, 0], [255, 255, 0], [255, 0, 0]]
color_C = [[0, 0, 0], [255, 255, 255]]
color_D = [[0, 0, 255], [255, 0, 0]]

color = color_B
NUM_COLORS = len(color)

def MakeHeatMapColor():
    for c in range(number_of_colors):
        value = c * (NUM_COLORS - 1) / last_color
        idx1 = int(value)
        if idx1 == value:
            red = color[idx1][0]
            green = color[idx1][1]
            blue = color[idx1][2]
        else:
            idx2 = idx1 + 1
            fractBetween = value - idx1
            red = int(
                round((color[idx2][0] - color[idx1][0]) * fractBetween + color[idx1][0])
            )
            green = int(
                round((color[idx2][1] - color[idx1][1]) * fractBetween + color[idx1][1])
            )
            blue = int(
                round((color[idx2][2] - color[idx1][2]) * fractBetween + color[idx1][2])
            )
        palette[c] = (0x010000 * red) + (0x000100 * green) + (0x000001 * blue)

MakeHeatMapColor()

image_bitmap = displayio.Bitmap(32, 24, number_of_colors)
image_tile = displayio.TileGrid(image_bitmap, pixel_shader=palette)
image_group = displayio.Group(scale=8)
image_group.append(image_tile)

scale_bitmap = displayio.Bitmap(number_of_colors, 1, number_of_colors)
scale_group = displayio.Group(scale=4)
scale_tile = displayio.TileGrid(scale_bitmap, pixel_shader=palette, x=0, y=60)
scale_group.append(scale_tile)

for i in range(number_of_colors):
    scale_bitmap[i, 0] = i

group = displayio.Group()

min_label = Label(terminalio.FONT, color=palette[0], x=0, y=300, scale=3)
max_label = Label(terminalio.FONT, color=palette[last_color], x=0, y=300, scale=3)
skyeyerangelabel = Label(terminalio.FONT, color=(30, 144, 255), x=260, y=10, scale=2)
seperatelabel = Label(terminalio.FONT, color=(255, 255, 255), x=260, y=30, scale=2)
statustitlelabel = Label(terminalio.FONT, color=(255, 255, 255), x=260, y=50, scale=2)
statustextlabel = Label(terminalio.FONT, color=(255, 0, 0), x=260, y=70, scale=2)
timestamplabel = Label(terminalio.FONT, color=(255, 255, 255), x=260, y=90, scale=2)
lastimagelabel = Label(terminalio.FONT, color=(255, 255, 255), x=260, y=110, scale=2)
linelabel = Label(terminalio.FONT, color=(255, 255, 255), x=260, y=130, scale=2)
statslabel = Label(terminalio.FONT, color=(255, 255, 255), x=260, y=150, scale=2)
thresholdlabel = Label(terminalio.FONT, color=(255, 255, 255), x=260, y=170, scale=2)
thresholdValueLabel = Label(terminalio.FONT, color=(255, 255, 255), x=260, y=190, scale=2)

templabel = Label(terminalio.FONT, color=(255, 165, 0), x=260, y=210, scale=2)
humiditylabel = Label(terminalio.FONT, color=(0, 150, 255), x=260, y=230, scale=2)
pressurelabel = Label(terminalio.FONT, color=(0, 255, 128), x=260 , y=250,scale=2)
gaslabel = Label(terminalio.FONT, color=(255,204,0), x=260, y=270, scale=2)
voclabel = Label(terminalio.FONT, color=(175, 0, 255), x=260, y=290,scale=2)

skyeyerangelabel.text = "Sky Eye Range V.1"
seperatelabel.text = "-----------------"
statustitlelabel.text = "SIGNAL STATUS:"
statustextlabel.text = "No Signal..."
lastimagelabel.text = "Latest Image: N/A"
timestamplabel.text = "0"
linelabel.text = "-----------------"
statslabel.text = "FIRE STATUS:"
thresholdlabel.text = "AI Detection: %"
thresholdValueLabel.text = "-----------------"
templabel.text = "Temperature: C"
humiditylabel.text = "Humidity: %"
pressurelabel.text = "Pressure: hPa"
gaslabel.text = "Gas: ppb"
voclabel.text = "VOC: ppb"

group.append(image_group)
group.append(scale_group)
group.append(min_label)
group.append(max_label)
group.append(skyeyerangelabel)
group.append(seperatelabel)
group.append(statustitlelabel)
group.append(statustextlabel)
group.append(lastimagelabel)
group.append(timestamplabel)
group.append(linelabel)
group.append(statslabel)
group.append(thresholdlabel)
group.append(thresholdValueLabel)
group.append(templabel)
group.append(humiditylabel)
group.append(pressurelabel)
group.append(gaslabel)
group.append(voclabel)

display.show(group)

min_t = 20
max_t = 37

image_size = 24 * 32

image = []
image_index = 0

start_time = time.monotonic()
timeout = 5

stamp = time.monotonic() - start_time

def showImage():
    global image
    global packet_index
    global image_bitmap
    global last_color
    global min_t, max_t

    if len(image) == image_size:

        statustextlabel.text = "Image Recieved!"
        lastimagelabel.text = "Latest Image: %0.0f" % (stamp)

        fire_count = 0

        mini = image[0]
        maxi = image[0]

        for h in range(24):
            for w in range(32):
                t = image[h * 32 + w]
                if(t >= THRESHOLD_TEMP):
                    fire_count = fire_count + 1
                if t > maxi:
                    maxi = t
                if t < mini:
                    mini = t
                image_bitmap[w, (23 - h)] = int(map_range(t, min_t, max_t, 0, last_color))

        fire_percent = fire_count / 768
        thresholdlabel.text  = "Fire Detect: {:.0%}".format(fire_percent)

        min_label.text = "%0.2f" % (min_t)

        max_string = "%0.2f" % (max_t)
        max_label.x = 120 - (5 * len(max_string))
        max_label.text = max_string

        min_t = mini
        max_t = maxi
    else:
        statustextlabel.text = "Image Lost..."

    packet_index = 0
    print(len(image))
    image = []

imageSize = 768
packets = 16
packetLength = imageSize // packets

packet_index = 0

while True:
    stamp = time.monotonic() - start_time
    timestamplabel.text = "Scout Time: %0.0f" % (stamp)

    packet = rfm9x.receive()

    if packet is not None:
        packet_text = str(packet, 'ascii')
        packet_data =  packet_text.split(':')

        print(packet_data[0])

        if not packet_data[0].isdigit():

            if packet_data[0] == "temp":
                print("Temperature:", packet_data[1])
                templabel.text = "Temp: {} C".format(packet_data[1])

            if packet_data[0] == "rhum":
                print("Relative Humidity:", packet_data[1])
                humiditylabel.text = "Hum: {} %".format(packet_data[1])

            if packet_data[0] == "pressure":
                print("Pressure:", packet_data[1])
                pressurelabel.text = "Pres: {} hPa".format(packet_data[1])

            if packet_data[0] == "gas_spg_com":
                print("Compensated Gas:", packet_data[1])
                gaslabel.text = "Gas: {} ppb".format(packet_data[1])

            if packet_data[0] == "voc":
                print("VOC:", packet_data[1])
                voclabel.text = "VOC: {} ppb".format(packet_data[1])

            if packet_data[0] == "hum":
                print("Humidity:", packet_data[1])

            if packet_data[0] == "gas_bme":
                print("Gas:", packet_data[1])

            if packet_data[0] == "gas_spg":
                print("RAW Gas:", packet_data[1])

            continue

        if int(packet_data[0]) == packet_index:
            packet_index += 1
            str_data = packet_data[1].split(',')
            for s in str_data:
                image.append(int(s))
        else:
            pixel = 30
            if len(image) > 1:
                pixel = image[-1]
            for x in range(packetLength):
                pass
                image.append(pixel)

            print('Missed Packet...', packet_index, packet_data[0])
            print(packet_data)
            packet_index = int(packet_data[0]) + 1
            str_data = packet_data[1].split(',')
            for s in str_data:
                image.append(int(s))
            pass

        if packet_index >= packets:
            print('showImage')
            showImage()

    else:
        print('Listining...')
