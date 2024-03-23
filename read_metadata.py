from PIL import Image
import io
import matplotlib.pyplot as plt

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
        color = tuple(data[i:i+3])
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

def visualize_palette(palette):
    if palette:
        num_colors = len(palette)
        fig, ax = plt.subplots(1, num_colors, figsize=(num_colors, 1))
        for i, color in enumerate(palette):
            ax[i].imshow([[color]], extent=[0, 1, 0, 1], aspect='auto')
            ax[i].axis('off')
        plt.show()
    else:
        print("No palette found.")

file_path = 'example4.png'
metadata = read_png_metadata(file_path)
print("Width:", metadata.get('width'))
print("Height:", metadata.get('height'))
print("Bit depth:", metadata.get('bit_depth'))
print("Color type:", metadata.get('color_type'),", ", recoginze_color_type(metadata.get('color_type')))
print("Compression method:", metadata.get('compression_method'))
print("Filter method:", metadata.get('filter_method'))
print("Interlace method:", metadata.get('interlace_method'))

visualize_palette(metadata.get('palette'))

if metadata.get('END'):
    print("File ends properly")
else:
    print("No IEND chunk")

#show_png_image(file_path)
