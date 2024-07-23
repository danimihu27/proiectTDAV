# -*- coding: utf-8 -*-
"""proiectdav.jpynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Ji5OFcBKZ7i4joIx1CqAXNm0FFOz7q6r

**Obiectiv: **


Algoritmul Watershed utilizează informații topografice pentru a împărți o imagine în mai multe segmente sau regiuni. Algoritmul vede o imagine ca o suprafață topografică, fiecare pixel reprezentând o înălțime diferită. Algoritmul Watershed utilizează aceste informații pentru a identifica bazinele de colectare, asemănătoare cu modul în care apa se acumulează în văi pe o hartă topografică reală.

Algoritmul Watershed identifică minimele locale, adică punctele cele mai joase, din imagine. Aceste puncte sunt apoi marcate ca și markeri. Algoritmul inundă apoi imaginea cu culori diferite, pornind de la acești markeri marcați. Pe măsură ce culoarea se extinde, aceasta umple bazinele de colectare până când atinge limitele obiectelor sau regiunilor din imagine.

Basinul de colectare în algoritmul Watershed se referă la o regiune din imagine care este umplută de culoarea care se extinde, pornind de la un marker. Basinul de colectare este definit de limitele obiectului sau regiunii din imagine și de minimele locale din valorile de intensitate ale pixelilor. Algoritmul utilizează bazinele de colectare pentru a împărți imaginea în regiuni separate și apoi identifică limitele dintre aceste bazine pentru a crea o segmentare a imaginii utilizată în recunoașterea obiectelor, analiza imaginii și extragerea de caracteristici.

Importarea librariilor necesare
"""

from __future__ import print_function
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from scipy import ndimage
import argparse
import imutils
import cv2
from IPython.display import Image, display
import numpy as np
from matplotlib import pyplot as plt

"""Definim o funcție numită "imshow" pentru a afișa imaginea procesată. Codul încarcă o imagine cu numele "inpcoins.jpg" și o convertește în tonuri de gri folosind metoda "cvtColor" din OpenCV. Imaginea în tonuri de gri este stocată într-o variabilă numită "gray"."""

# Funcție pentru afișarea imaginilor
def imshow(img, ax=None):
    if ax is None:
        ret, encoded = cv2.imencode(".png", img)
        display(Image(encoded))
    else:
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax.axis('off')

# Încărcarea imaginii
img = cv2.imread("inpcoins8.png")


imshow(img)

"""Treshold proccessing.

Un parametru cv2.THRESH_OTSU este adăugat la cv2.THRESH_BINARY_INV. Acesta reprezintă procesul de binarizare Otsu, iar atunci când împărțim pixelii în două grupuri în funcție de caracteristicile lor, ideea este să luăm pragul de gândire că este mai bine să colectăm cât mai mult posibil aceleași grupuri și să separăm cât mai mult posibil grupurile diferite.
"""

# Aplicarea filtrului mean-shift
shifted = cv2.pyrMeanShiftFiltering(img, 21, 51)
# Convertirea imaginii la nivel de gri
gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
# Aplicarea unei praguri pentru a obține imaginea binară
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
imshow(thresh)

"""Detectia Contururilor"""

# Detectarea contururilor în imaginea binară
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)


# Parcurgerea contururilor și desenarea lor pe imagine
for c in cnts:
    cv2.drawContours(img, [c], -1, (0, 255, 0), 2)

# Afișarea imaginii finale cu contururile
imshow(img)
cv2.waitKey(0)

"""Primul pas în aplicarea algoritmului watershed pentru segmentare este să calculăm Transformata Euclidiană a Distanței (Euclidean Distance Transform - EDT) folosind funcția distance_transform_edt . Așa cum sugerează și numele, această funcție calculează distanța euclidiană până la cel mai apropiat zero (adică pixelul de fundal) pentru fiecare dintre pixelii din prim-plan."""

# Calcularea distanței Euclidiene exacte de la fiecare pixel binar la cel mai apropiat pixel zero,
# apoi găsirea vârfurilor în acest mapaj al distanței
D = ndimage.distance_transform_edt(thresh)
localMax = peak_local_max(D, indices=False, min_distance=20, labels=thresh)

# Realizarea unei analize a componentelor conectate pe vârfurile locale,
# folosind conectivitatea 8, apoi aplicarea algoritmului Watershed
markers = ndimage.label(localMax, structure=np.ones((3, 3)))[0]
labels = watershed(-D, markers, mask=thresh)

"""Ultimul pas constă în a parcurge pur și simplu valorile unice de etichetă și în a extrage fiecare dintre obiectele unice."""

# Parcurgerea etichetelor unice returnate de algoritmul Watershed
for label in np.unique(labels):
    # Dacă eticheta este zero, examinăm 'background-ul',
    # așa că o ignorăm simplu
    if label == 0:
        continue

    # Altfel, alocăm memorie pentru regiunea etichetei și o desenăm pe masca
    mask = np.zeros(gray.shape, dtype="uint8")
    mask[labels == label] = 255

    # Detectăm contururile în masca și luăm cel mai mare
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)

    # Desenăm un cerc care înconjoară obiectul
    ((x, y), r) = cv2.minEnclosingCircle(c)
    cv2.circle(img, (int(x), int(y)), int(r), (0, 255, 0), 2)

# Afișăm imaginea finală cu obiectele detectate
imshow(img)
cv2.waitKey(0)