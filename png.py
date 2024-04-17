from anonim import PNG  
from chunks import (
    read_png_metadata,
    show_palette,
    show_png_image
)
from fourier_transform import fourier_transform_image

def process_image(file_path, output_file):
    print("Czytanie metadanych PNG...")
    metadata = read_png_metadata(file_path)
    print("Szerokość:", metadata.get('width'))
    print("Wysokość:", metadata.get('height'))
    print("Głębokość bitów:", metadata.get('bit_depth'))
    print("Metoda kompresji:", metadata.get('compression_method'))
    print("Metoda filtrowania:", metadata.get('filter_method'))
    print("Metoda przeplotu:", metadata.get('interlace_method'))
    print("Text:", metadata.get('text'))
    print("Text:", metadata.get('z_text'))
    print("Gamma:", metadata.get('gamma'))
    print("Chrominancja:", metadata.get('chromaticity'))
    print("Tło:", metadata.get('background'))
    print("EXIF:", metadata.get('exif'))

    if metadata.get('END'):
        print("Plik zakończony poprawnie")
    else:
        print("Brak chunku IEND")

    if 'palette' in metadata:
        print("\nWyświetlanie palety...")
        show_palette(metadata['palette'])

    print("\nAnonimizacja obrazu PNG...")
    original_png = PNG(file_path)
    original_png.anonymize(output_file)

    print("\nTransformacja Fouriera obrazu...")
    fourier_transform_image(output_file)

    print("\nWyświetlanie obrazu PNG...")
    show_png_image(output_file)

if __name__ == "__main__":
    input_file = "example8.png"
    output_file = "example8_anonymized.png"

    # Wczyt oryginalnego pliku PNG
    original_png = PNG(input_file)
    print("Liczba chunków przed anonimizacją:", len(original_png.chunks))
    original_png.print_chunk_info()

    # Anonimizacja
    original_png.anonymize(output_file)

    # Wczyt zanonimizowanego pliku PNG
    anonymized_png = PNG(output_file)
    print("Liczba chunków po anonimizacji:", len(anonymized_png.chunks))
    anonymized_png.print_chunk_info()

    # Opcjonalnie, uruchomienie głównej funkcji przetwarzającej na zanonimizowanym pliku
    process_image(input_file, output_file)
