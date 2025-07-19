# GPIO Setup Instructions

## For Raspberry Pi 5 (and newer):
The Raspberry Pi 5 requires the `gpiod` library instead of `RPi.GPIO`.

### Install gpiod:
```bash
sudo apt update
sudo apt install python3-libgpiod
```

Or via pip:
```bash
pip install gpiod
```

## For Raspberry Pi 4 and earlier:
Use the traditional `RPi.GPIO` library:
```bash
pip install RPi.GPIO
```

## For Development (Windows/Mac/Linux):
The mock GPIO is automatically used for development on non-Raspberry Pi systems.

## GPIO Pin Configuration:
- Button 1 (Select): GPIO 17
- Button 2 (Confirm): GPIO 27

## Hardware Setup:
Connect buttons between GPIO pins and ground with pull-up resistors, or use the internal pull-up resistors (enabled in code).

```
GPIO Pin -> Button -> Ground
```

The code automatically detects:
1. Raspberry Pi 5: Uses gpiod
2. Raspberry Pi 4 and earlier: Uses RPi.GPIO
3. Development systems: Uses mock GPIO
