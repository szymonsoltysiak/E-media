from PIL import Image
import io
import tkinter as tk
import zlib

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
    # The first chunk is the keyword, and the rest are the text
    keyword = chunks[0].decode('utf-8')
    text = b'\x00'.join(chunks[1:]).decode('utf-8')
    return keyword, text

def read_zTXt(data):
    null_byte_index = data.find(b'\x00')
    if null_byte_index != -1:
        keyword = data[:null_byte_index].decode('utf-8')
        compression_method = data[null_byte_index + 1]
        compressed_text = data[null_byte_index + 2:]
        if compression_method == 0:  # Compression method 0 indicates zlib compression
            try:
                uncompressed_text = zlib.decompress(compressed_text).decode('utf-8')
                return keyword, uncompressed_text
            except zlib.error:
                return keyword, None  # Failed to decompress
    return None, None

def read_gAMA(data):
    gamma = int.from_bytes(data, byteorder='big') / 100000
    return gamma

def read_bKGD(data, color_type):
    if color_type == 3:  # Indexed-color image
        palette_index = byte_to_int(data)
        return palette_index
    elif color_type in [0, 4]:  # Grayscale image or grayscale with alpha
        grayscale_sample = byte_to_int(data)
        return grayscale_sample
    elif color_type in [2, 6]:  # Truecolor image or truecolor with alpha
        red_sample = byte_to_int(data[0:2])
        green_sample = byte_to_int(data[2:4])
        blue_sample = byte_to_int(data[4:6])
        return red_sample, green_sample, blue_sample
    else:
        return None  # Unsupported color type

def read_cHRM(data):
    white_point_x = byte_to_int(data[:4]) / 100000
    white_point_y = byte_to_int(data[4:8]) / 100000
    red_x = byte_to_int(data[8:12]) / 100000
    red_y = byte_to_int(data[12:16]) / 100000
    green_x = byte_to_int(data[16:20]) / 100000
    green_y = byte_to_int(data[20:24]) / 100000
    blue_x = byte_to_int(data[24:28]) / 100000
    blue_y = byte_to_int(data[28:32]) / 100000
    return {
        'white_point': (white_point_x, white_point_y),
        'red_primary': (red_x, red_y),
        'green_primary': (green_x, green_y),
        'blue_primary': (blue_x, blue_y)
    }

def read_png_metadata(file_path):
    with open(file_path, 'rb') as file:
        header = file.read(8)
        if header[:8] != b'\x89PNG\r\n\x1a\n':
            raise ValueError("This is not PNG flie")

        metadata = {}
        metadata['END'] = False
        palette = None

        while True:
            length_bytes = file.read(4)
            if len(length_bytes) != 4:
                break
            length = byte_to_int(length_bytes)

            block_type = file.read(4)
            data = file.read(length)
            crc = file.read(4)

            if block_type == b'IHDR':
                metadata = read_IHDR(data)
            elif block_type == b'PLTE':
                palette = read_PLTE(data)
                metadata['palette'] = palette
            elif block_type == b'tEXt':
                keyword, text = read_tEXt(data)
                metadata["text"] = keyword+": "+text
            elif block_type == b'zTXt':
                keyword, text = read_zTXt(data)
                metadata["z_text"] = keyword+": "+text
            elif block_type == b'gAMA':
                gamma = read_gAMA(data)
                metadata['gamma'] = gamma
            elif block_type == b'cHRM':
                chromaticity = read_cHRM(data)
                metadata['chromaticity'] = chromaticity
            elif block_type == b'bKGD':
                background_data = read_bKGD(data, metadata['color_type'])
                metadata['background'] = background_data
            elif block_type == b'IEND':
                metadata['END'] = True
                break

        return metadata


def recoginze_color_type(number):
    match number:
        case 0:
            return "Color, palette and alpha channel not used"
        case 2:
            return "Color used"
        case 3:
            return "Color and palette used"
        case 4:
            return "Alpha channel used"
        case 6:
            return "Color, palette and alpha channel used"
        case _:
            return "Wrong number"


def show_png_image(file_path):
    with open(file_path, 'rb') as file:
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image.show()


def show_palette(palette):
    if palette:
        root = tk.Tk()
        root.title("Palette")
        for i, color in enumerate(palette):
            frame = tk.Frame(root, bg='#%02x%02x%02x' % color, width=7, height=100)
            frame.grid(row=0, column=i, padx=0, pady=5)
        root.mainloop()
    else:
        print("No palette found.")

file_path = 'example6.png'
metadata = read_png_metadata(file_path)
print("Width:", metadata.get('width'))
print("Height:", metadata.get('height'))
print("Bit depth:", metadata.get('bit_depth'))
print("Color type:", metadata.get('color_type'), ", ", recoginze_color_type(metadata.get('color_type')))
print("Compression method:", metadata.get('compression_method'))
print("Filter method:", metadata.get('filter_method'))
print("Interlace method:", metadata.get('interlace_method'))
print(metadata.get('text'))
print(metadata.get('z_text'))
print("Gamma:", metadata.get('gamma'))
print("Chromaticity:", metadata.get('chromaticity'))
print("Background:", metadata.get('background'))


show_palette(metadata.get('palette'))

if metadata.get('END'):
    print("File ends properly")
else:
    print("No IEND chunk")

show_png_image(file_path)
