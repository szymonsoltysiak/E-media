def read_IHDR(data):
    metadata = {}

    metadata['width'] = int.from_bytes(data[0:4], byteorder='big')
    metadata['height'] = int.from_bytes(data[4:8], byteorder='big')
    metadata['bit_depth'] = int.from_bytes(data[8:9], byteorder='big')
    metadata['color_type'] = int.from_bytes(data[9:10], byteorder='big')
    metadata['compression_method'] = int.from_bytes(data[10:11], byteorder='big')
    metadata['filter_method'] = int.from_bytes(data[11:12], byteorder='big')
    metadata['interlace_method'] = int.from_bytes(data[12:13], byteorder='big')

    return metadata

def read_png_metadata(file_path):
    with open(file_path, 'rb') as file:
        header = file.read(8)
        if header[:8] != b'\x89PNG\r\n\x1a\n':
            raise ValueError("This is not PNG flie")

        metadata = {}

        while True:
            length_bytes = file.read(4)
            if len(length_bytes) != 4:
                break
            length = int.from_bytes(length_bytes, byteorder='big')

            block_type = file.read(4)
            data = file.read(length)
            crc = file.read(4)

            if block_type == b'IHDR':
                metadata = read_IHDR(data)

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

file_path = 'example.png'
metadata = read_png_metadata(file_path)
print("Width:", metadata.get('width'))
print("Height:", metadata.get('height'))
print("Bit depth:", metadata.get('bit_depth'))
print("Color type:", metadata.get('color_type'),", ", recoginze_color_type(metadata.get('color_type')))
print("Compression method:", metadata.get('compression_method'))
print("Filter method:", metadata.get('filter_method'))
print("Interlace method:", metadata.get('interlace_method'))
