import numpy as np # type: ignore
import cv2 # type: ignore
import matplotlib.pyplot as plt # type: ignore

def morphological_reconstruction(marker, mask, kernel_size=(7, 7)): # morfoloska rekonstrukcija
    kernel = np.ones(kernel_size, np.uint8)
    while True:
        dilated = cv2.dilate(marker, kernel) # prosiruje bele pixele
        reconstructed = cv2.bitwise_and(dilated, mask) # zadrzava samo deo prosirenja koji se slaze sa maskom

        if np.array_equal(marker, reconstructed): # marker poklapa sa prethodno restruktovanim markerom?
            return reconstructed
        marker = reconstructed

if __name__ == '__main__':
    img = cv2.imread("coins.png")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.subplot(2, 3, 1)
    plt.imshow(img_rgb)
    plt.title("Originalna slika")

    blur_img = cv2.medianBlur(img, 11) #u cilju smanjenja suma

    # konverzija u grayscale i prikaz sive slike
    gray_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2GRAY)
    plt.subplot(2, 3, 2)
    plt.imshow(gray_img, cmap='gray')
    plt.title("Grayscale slika")

    # kreiranje maske za sve novcice
    _, coins_mask = cv2.threshold(gray_img, 220, 255, cv2.THRESH_BINARY_INV) #kreira binarnu masku gde pixeli svetliji od 220 stavlja na 0 (crno) a ostali na 255 (belo)
    # vraca prag i binarnu masku, prag nam ne treba
    coins_mask = cv2.morphologyEx(coins_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) #radi smanjenja malih rupa i spajanja objekata
    coins_mask = cv2.morphologyEx(coins_mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) # uklananje sumova
    plt.subplot(2, 3, 3)
    plt.imshow(coins_mask, cmap='gray')
    plt.title("Maska novcica")

    hsv_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2HSV)
    saturation_channel = hsv_img[:, :, 1] #nivo zasicenja / za detekciju boja na slici
    plt.subplot(2, 3, 4)
    plt.imshow(saturation_channel, cmap='gray')
    plt.title("Saturation kanal")

    # kreiranje maske za bakarni novcic na osnovu saturation kanala
    _, copper_mask = cv2.threshold(saturation_channel, 60, 255, cv2.THRESH_BINARY)

    # dodatne morfoloske operacije za bakarni novcic
    copper_mask = cv2.morphologyEx(copper_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    copper_mask = cv2.morphologyEx(copper_mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

    # morfoloska rekonstrukcija za bolju segmentaciju bakarnog novcica
    copper_mask = morphological_reconstruction(copper_mask, coins_mask)
    plt.subplot(2, 3, 5)
    plt.imshow(copper_mask, cmap='gray')
    plt.title("Konacna maska bakarnog novcica")

    # primena maske za izdvajanje bakarnog novcica iz originalne slike
    extracted_copper_coin = cv2.bitwise_and(img_rgb, img_rgb, mask=copper_mask)
    plt.subplot(2, 3, 6)
    plt.imshow(extracted_copper_coin)
    plt.title("Izdvojeni bakarni novcic")

    plt.tight_layout()
    plt.show()

    # snimanje maske
    cv2.imwrite('mask.png', copper_mask)
