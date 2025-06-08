import cv2
import numpy as np
THRESHOLD = 5

img = cv2.imread("./Resultados/recon_usuario_37_cgne_g-30x30-2.png", cv2.IMREAD_GRAYSCALE)
cv2.imshow('teste', img)
clahe = cv2.createCLAHE(4.0, (13, 13))
img_clahe = clahe.apply(img)
cv2.imshow('equalizada', img_clahe)
img_lim = np.where(img > THRESHOLD, img, 0)
cv2.imshow('limiarizada', img_lim)
cv2.waitKey()
cv2.destroyAllWindows()