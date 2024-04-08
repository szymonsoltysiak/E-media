import cv2
import numpy as np

image = cv2.imread(r"example4.png")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

fourier = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)

fourier_shift = np.fft.fftshift(fourier)

magnitude = 20 * np.log(cv2.magnitude(fourier_shift[:, :, 0], fourier_shift[:, :, 1]))
phase = np.angle(fourier_shift[:, :, 0] + 1j * fourier_shift[:, :, 1])

magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

cv2.imshow('Original Image', gray)
cv2.imshow('Fourier Transform Magnitude', magnitude)
cv2.imshow('Fourier Transform Phase', phase)

cv2.waitKey(0)
cv2.destroyAllWindows()
