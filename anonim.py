import zlib

class PNG:
    def __init__(self, file_name) -> None:
        self._file_name = file_name
        self.chunks = []
        self.read_png()

    def read_png(self):
        with open(self._file_name, "rb") as file:
            png_data = file.read()

        # Sprawdzenie nagłówka
        header = png_data[:8]
        if header != b"\x89PNG\r\n\x1a\n":
            raise ValueError("Plik nie jest plikiem PNG")

        # Odczyt chunków
        end_of_last_chunk = 8
        while True:
            # Odczyt długości chunka (4 bajty)
            length_bytes = png_data[end_of_last_chunk: end_of_last_chunk + 4]
            length = int.from_bytes(length_bytes, byteorder="big")

            # Odczyt typu chunka (4 bajty)
            chunk_type = png_data[end_of_last_chunk + 4: end_of_last_chunk + 8].decode("ascii")

            # Odczyt danych chunka (length bajtów)
            data = png_data[end_of_last_chunk + 8: end_of_last_chunk + length + 8]

            # Odczyt sumy kontrolnej CRC (4 bajty)
            crc = png_data[end_of_last_chunk + length + 8: end_of_last_chunk + length + 12]

            # Ustawienie wskaźnika na koniec chunka
            end_of_last_chunk = end_of_last_chunk + length + 12

            # Dodanie chunka do listy
            self.chunks.append(_Chunk(length, chunk_type, data, crc))

            # Koniec pliku PNG
            if chunk_type == "IEND":
                break

    def save_png(self, output_file):
        with open(output_file, 'wb') as file:
            # Zapis nagłówka
            header = b"\x89PNG\r\n\x1a\n"
            file.write(header)

            for chunk in self.chunks:
                # dług chunka (4 bajty, big endian)
                length_bytes = chunk.length.to_bytes(4, byteorder='big')
                file.write(length_bytes)

                # typ chunka (4 bajty)
                chunk_type_bytes = chunk.chunk_type.encode('ascii')
                file.write(chunk_type_bytes)

                # dane chunka (length bajtów)
                file.write(chunk.chunk_data)

                # sumy kontrolnej CRC (4 bajty)
                file.write(chunk.crc)

    def anonymize(self, output_file, save_data=False):
        critical_chunks = ['IHDR', 'PLTE', 'IDAT', 'IEND']
        self.chunks = [chunk for chunk in self.chunks if chunk.chunk_type in critical_chunks]

        if not save_data:
            # Usunięcie nieistotnych chunków, jeśli save_data jest False
            self.chunks = [chunk for chunk in self.chunks if chunk.chunk_type in critical_chunks]

        self.save_png(output_file)

    def print_chunk_info(self):
        print("Informacje o chunkach:")
        for i, chunk in enumerate(self.chunks, start=1):
            print(f"Chunk {i}:")
            print(f"  Typ: {chunk.chunk_type}")
            print(f"  Długość: {chunk.length} bajtów")
            print(f"  CRC: {chunk.crc.hex()}")
            print("")

class _Chunk:
    def __init__(self, length, chunk_type, chunk_data, crc) -> None:
        self.length = length
        self.chunk_type = chunk_type
        self.chunk_data = chunk_data
        self.crc = crc


if __name__ == "__main__":
    input_file = "example3.png"
    output_file = "example3_anonymized.png"

    # Wczyt oryg plik PNG
    original_png = PNG(input_file)

    # info o chunkach przed anonim
    print("Liczba chunków przed anonimizacją:", len(original_png.chunks))
    original_png.print_chunk_info()

    #  anonim
    original_png.anonymize(output_file)

    # Wczyt zanonimizowany plik PNG
    anonymized_png = PNG(output_file)

    #  info o chunkach po anonimizacji
    print("Liczba chunków po anonimizacji:", len(anonymized_png.chunks))
    anonymized_png.print_chunk_info()




