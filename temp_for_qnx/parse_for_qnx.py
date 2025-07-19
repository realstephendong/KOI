def load_1bit_bmp(path):
    with open(path, 'rb') as f:
        data = f.read()

    pixel_offset = int.from_bytes(data[10:14], 'little')
    width = int.from_bytes(data[18:22], 'little')
    height = int.from_bytes(data[22:26], 'little')
    row_size = ((width + 31) // 32) * 4

    pixels = []
    for y in range(height):
        row_start = pixel_offset + (height - 1 - y) * row_size
        row = []
        for x in range(width):
            byte_index = row_start + (x // 8)
            bit_index = 7 - (x % 8)
            pixel_byte = data[byte_index]
            bit = (pixel_byte >> bit_index) & 1
            row.append(bit)
        pixels.append(row)
    return pixels, width, height

def pack_pixels_8vertical(pixels, width, height):
    pages = height // 8
    buf = bytearray(width * pages)
    for page in range(pages):
        for x in range(width):
            byte = 0
            for bit in range(8):
                y = page * 8 + bit
                if y < height and pixels[y][x]:
                    byte |= (1 << bit)
            buf[page * width + x] = byte
    return buf

def gpio_write(pin, value):
    # Export pin if not already
    try:
        with open("/sys/class/gpio/export", "w") as f:
            f.write(str(pin))
    except:
        pass  # already exported

    with open(f"/sys/class/gpio/gpio{pin}/direction", "w") as f:
        f.write("out")

    with open(f"/sys/class/gpio/gpio{pin}/value", "w") as f:
        f.write("1" if value else "0")

def spi_write(data):
    with open("/dev/spidev0.0", "wb") as f:
        f.write(data)

def send_buffer_to_oled(buf, dc_pin=22):
    gpio_write(dc_pin, 1)   # DC = 1 for data mode
    spi_write(buf)

def reset_display(rst_pin=13):
    import time
    gpio_write(rst_pin, 1)
    time.sleep(0.1)
    gpio_write(rst_pin, 0)
    time.sleep(0.1)
    gpio_write(rst_pin, 1)
    time.sleep(0.1)
