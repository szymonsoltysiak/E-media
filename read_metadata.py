from PIL import Image, ImageTk
import io
import tkinter as tk
import numpy as np
from numpy.fft import fftshift, ifftshift
from scipy.fft import fft2, ifft2

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


def apply_fourier_transform(file_path):
    with open(file_path, 'rb') as file:
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)

        # Transformata Fouriera
        image_fft = fft2(image_array)
        image_fft_shifted = fftshift(image_fft)

        # Odwrotna
        image_restored_fft = ifftshift(image_fft_shifted)
        image_restored = ifft2(image_restored_fft)

        # rzeczywista czesc przywroconego obrazu
        image_restored = np.real(image_restored)

        # przetwarzanie na obraz
        restored_image = Image.fromarray(image_restored.astype('uint8'))
        restored_image.show()

def anonymize_image(image_array, box):
    # zamazywanie obszaru
    #box[0] gorna granica wiersz, box[1] lewa granica kolumn, box[2] dolna granica wierszy, box[3] prawa granica kolumn
    blurred_region = image_array[box[0]:box[2], box[1]:box[3]]
    blurred_region[:] = np.mean(blurred_region, axis=(0, 1), keepdims=True)#srednia kolorow,do koloru zamazywania
    image_array[box[0]:box[2], box[1]:box[3]] = blurred_region #zastep oryg obszar zamazanym fragmentem
    return image_array


file_path = 'example4.png'
metadata = read_png_metadata(file_path)
print("Width:", metadata.get('width'))
print("Height:", metadata.get('height'))
print("Bit depth:", metadata.get('bit_depth'))
print("Color type:", metadata.get('color_type'), ", ", recoginze_color_type(metadata.get('color_type')))
print("Compression method:", metadata.get('compression_method'))
print("Filter method:", metadata.get('filter_method'))
print("Interlace method:", metadata.get('interlace_method'))

show_palette(metadata.get('palette'))

if metadata.get('END'):
    print("File ends properly")
else:
    print("No IEND chunk")

apply_fourier_transform(file_path)

image = Image.open(file_path)
image_array = np.array(image)
anonymized_image_array = anonymize_image(image_array, (100, 100, 200, 200))  # Specify the box to be anonymized
anonymized_image = Image.fromarray(anonymized_image_array)
anonymized_image.show()

show_png_image(file_path)
