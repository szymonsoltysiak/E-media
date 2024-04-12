from PIL import Image
import io
import tkinter as tk
import zlib
from PIL.ExifTags import TAGS
import struct

def byte_to_int(data):
    return int.from_bytes(data, byteorder='big')

def read_IHDR(data):
    metadata = {}
    metadata['width'] = byte_to_int(data[0:4])
    metadata['height'] = byte_to_int(data[4:8])
    metadata['bit_depth'] = byte_to_int(data[8:9])
    metadata['color_type'] = byte_to_int(data[9:10])
    metadata['compression_method'] = byte_to_int(data[10:11])
    metadata['filter_method'] = byte_to_int(data[11:12])
    metadata['interlace_method'] = byte_to_int(data[12:13])
    return metadata

def read_PLTE(data):
    palette = []
    for i in range(0, len(data), 3):
        color = tuple(data[i:i + 3])
        palette.append(color)
    return palette

def read_tEXt(data):
    chunks = data.split(b'\x00')
    keyword = chunks[0].decode('utf-8')
    text = b'\x00'.join(chunks[1:]).decode('utf-8')
    return keyword, text

def read_zTXt(data):
    null_byte_index = data.find(b'\x00')
    if null_byte_index != -1:
        keyword = data[:null_byte_index].decode('utf-8')
        compression_method = data[null_byte_index + 1]
        compressed_text = data[null_byte_index + 2:]
        try:
            uncompressed_text = zlib.decompress(compressed_text).decode('utf-8')
            return keyword, uncompressed_text
        except zlib.error:
            return keyword, None
    return None, None

def read_gAMA(data):
    gamma = int.from_bytes(data, byteorder='big') / 100000
    return gamma

def read_bKGD(data, color_type):
    if color_type == 3:
        return byte_to_int(data)
    elif color_type in [0, 4]:
        return byte_to_int(data)
    elif color_type in [2, 6]:
        return (byte_to_int(data[0:2]), byte_to_int(data[2:4]), byte_to_int(data[4:6]))
    return None

def read_cHRM(data):
    return {
        'white_point': (byte_to_int(data[:4]) / 100000, byte_to_int(data[4:8]) / 100000),
        'red_primary': (byte_to_int(data[8:12]) / 100000, byte_to_int(data[12:16]) / 100000),
        'green_primary': (byte_to_int(data[16:20]) / 100000, byte_to_int(data[20:24]) / 100000),
        'blue_primary': (byte_to_int(data[24:28]) / 100000, byte_to_int(data[28:32]) / 100000)
    }

def read_png_metadata(file_path):
    with open(file_path, 'rb') as file:
        header = file.read(8)
        if header[:8] != b'\x89PNG\r\n\x1a\n':
            raise ValueError("This is not PNG file")

        metadata = {'END': False, 'text': {}, 'z_text': {}}
        while True:
            length_bytes = file.read(4)
            if len(length_bytes) != 4:
                break
            length = byte_to_int(length_bytes)
            block_type = file.read(4)
            data = file.read(length)
            file.read(4)  # Skip CRC

            if block_type == b'IHDR':
                metadata.update(read_IHDR(data))
            elif block_type == b'PLTE':
                metadata['palette'] = read_PLTE(data)
            elif block_type == b'tEXt':
                keyword, text = read_tEXt(data)
                metadata['text'][keyword] = text
            elif block_type == b'zTXt':
                keyword, text = read_zTXt(data)
                metadata['z_text'][keyword] = text
            elif block_type == b'gAMA':
                metadata['gamma'] = read_gAMA(data)
            elif block_type == b'cHRM':
                metadata['chromaticity'] = read_cHRM(data)
            elif block_type == b'bKGD':
                metadata['background'] = read_bKGD(data, metadata['color_type'])
            elif block_type == b'IEND':
                metadata['END'] = True
                break

        return metadata

def recoginze_color_type(number):
    match number:
        case 0: return "Color, palette and alpha channel not used"
        case 2: return "Color used"
        case 3: return "Color and palette used"
        case 4: return "Alpha channel used"
        case 6: return "Color, palette and alpha channel used"
        case _: return "Wrong number"

def show_png_image(image_path):
    with Image.open(image_path) as image:
        image.show()

def show_palette(palette):
    if palette:
        root = tk.Tk()
        root.title("Palette")
        for i, color in enumerate(palette):
            frame = tk.Frame(root, bg='#%02x%02x%02x' % color, width=7, height= 100)
            frame.grid(row=0, column=i, padx=0, pady=5)
        root.mainloop()
    else:
        print("No palette found.")
