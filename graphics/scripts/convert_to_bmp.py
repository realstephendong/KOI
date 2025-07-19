from PIL import Image
import os

def convert_to_monochrome_bmp(png_path):
    try:
        bmp_path = os.path.splitext(png_path)[0] + ".bmp"
        with Image.open(png_path) as img:
            mono_img = img.convert("1")  # Convert to 1-bit pixels, black and white
            mono_img.save(bmp_path, format='BMP')
        print(f"Saved {bmp_path}")
    except Exception as e:
        print(f"Failed to convert {png_path}: {e}")

def convert_all_pngs_in_folder(root_folder):
    if not os.path.exists(root_folder):
        print(f"Folder does not exist: {root_folder}")
        return

    for dirpath, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(".png"):
                full_path = os.path.join(dirpath, file)
                convert_to_monochrome_bmp(full_path)

if __name__ == "__main__":
    folder = "../assets/soy"
    print(f"Starting conversion in folder: {folder}")
    convert_all_pngs_in_folder(folder)
