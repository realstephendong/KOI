import os
import spidev

def detect_spi_device(bus=0, device=0):
    try:
        spi = spidev.SpiDev()
        spi.open(bus, device)
        spi.max_speed_hz = 500000

        # Try to read/write a dummy byte
        response = spi.xfer2([0x00])
        print("SPI device responded:", response)

        spi.close()
        return True
    except FileNotFoundError:
        print(f"/dev/spidev{bus}.{device} not found.")
        return False
    except PermissionError:
        print("Permission denied. Try running as root or with sudo.")
        return False
    except Exception as e:
        print("Unexpected error while accessing SPI:", e)
        return False

if __name__ == "__main__":
    print("Checking SPI device presence at /dev/spidev0.0...")
    if detect_spi_device(0, 0):
        print("✔️  SPI device appears responsive.")
    else:
        print("❌  Could not detect SPI device response. Check wiring and device health.")
