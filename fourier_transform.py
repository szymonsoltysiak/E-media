import cv2
import numpy as np
import matplotlib.pyplot as plt


def fourier_transform_image(file_path):
    image = cv2.imread(file_path)
    if image is None:
        raise ValueError("Unable to load image.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fourier = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
    fourier_shift = np.fft.fftshift(fourier)

    magnitude_spectrum = 20 * np.log(cv2.magnitude(fourier_shift[:,:,0], fourier_shift[:,:,1]))
    magnitude_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)


    fft=fourier_shift[:,:,0]+1j*fourier_shift[:,:,1]
    phase_spectrum = np.angle(fft)

    fig = plt.figure(figsize=(10, 4))
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)

    ax1.imshow(gray, cmap='gray')
    ax1.set_title('Grayscale')

    ax2.imshow(magnitude_spectrum, cmap='gray')
    ax2.set_title('Magnitude')

    ax3.imshow(phase_spectrum, cmap='gray')
    ax3.set_title('Phase')

    for ax in [ax1, ax2, ax3]:
        ax.axis('off')

    plt.tight_layout()
    plt.show()

