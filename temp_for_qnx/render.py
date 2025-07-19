from config import DEVICE_HEIGHT, DEVICE_WIDTH
from graphics.pet import Pet
from temp_for_qnx.parse_for_qnx import load_1bit_bmp, pack_pixels_8vertical, send_buffer_to_oled


def compose_frame(pet_pixels, health_bar_pixels, width=DEVICE_WIDTH, height=DEVICE_HEIGHT):
    frame = [[0]*width for _ in range(height)]

    # Paste sprite at (x,y), e.g. (0,0)
    sprite_x, sprite_y = 0, 0
    for y, row in enumerate(pet_pixels):
        for x, pixel in enumerate(row):
            if 0 <= sprite_x + x < width and 0 <= sprite_y + y < height:
                frame[sprite_y + y][sprite_x + x] = pixel

    # Paste health bar at (x,y), e.g. (0, 70)
    hb_x, hb_y = 0, 70
    for y, row in enumerate(health_bar_pixels):
        for x, pixel in enumerate(row):
            if 0 <= hb_x + x < width and 0 <= hb_y + y < height:
                frame[hb_y + y][hb_x + x] = pixel

    return frame

def render_frame(frame_pixels):
    buf = pack_pixels_8vertical(frame_pixels, DEVICE_WIDTH, DEVICE_HEIGHT)
    send_buffer_to_oled(buf)  # Your SPI write function

def run_graphics_loop():
    import time

    koi = Pet("idle", 0, 3)
    koi_frames = koi.create_pet_frames("koi")

    while True:
        frame_index = 0

        current_frame = compose_frame(koi_frames["idle"][frame_index])
        frame_index = (frame_index + 1) % len(koi_frames["idle"])
        time.sleep(1)

        render_frame(current_frame)
    

