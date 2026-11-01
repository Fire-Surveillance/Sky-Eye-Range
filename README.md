# Sky-Eye-Range

CircuitPython code for the Sky Eye Range fire-surveillance system. To run a file on a board, copy it to the board as `code.py`.

## TX (transmitter)

| File | Description |
|---|---|
| [`TX/everything_tx.py`](TX/everything_tx.py) | Reads the MLX90640 thermal camera, BME680 and SGP40 sensors, logs to the SD card, and sends everything over RFM9x LoRa at 20 dBm. Loop delay: 0.1 s |
| [`TX/everything_tx_1s_delay.py`](TX/everything_tx_1s_delay.py) | Same as above, with a 1 s loop delay |

## RX (receivers)

| File | Description |
|---|---|
| [`RX/wrist_watch_rx.py`](RX/wrist_watch_rx.py) | Wrist watch receiver on the built-in display, with colored sensor labels |
| [`RX/wrist_watch_rx_v2.py`](RX/wrist_watch_rx_v2.py) | Wrist watch receiver, grey-text layout variant |
| [`RX/rx_480x320.py`](RX/rx_480x320.py) | Receiver for the 480 x 320 HX8357 display with TSC2007 touchscreen |

## Credits

The RX code is based on Adafruit examples released under the MIT License:

- SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries (SPDX-License-Identifier: MIT)
- SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries (SPDX-License-Identifier: MIT)

The heatmap colors are based on http://www.andrewnoske.com/wiki/Code_-_heatmaps_and_color_gradients
