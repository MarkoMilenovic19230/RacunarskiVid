import cv2
import numpy as np

# Funkcija koja proverava da li je rupa sa leve ili desne strane (razlikuje P od q)
def izracunaj_stranu_rupe(kontura, rupa_kontura):
    momenti = cv2.moments(kontura)
    if momenti['m00'] == 0: return 0
    # Težište konture slova
    centar_x, centar_y = momenti['m10'] / momenti['m00'], momenti['m01'] / momenti['m00']

    momenti_r = cv2.moments(rupa_kontura)
    if momenti_r['m00'] == 0: return 0
    # Težište unutrašnje rupe
    rx, ry = momenti_r['m10'] / momenti_r['m00'], momenti_r['m01'] / momenti_r['m00']

    # Tražimo najdalju tačku od centra (obično vrh slova)
    udaljenosti = np.linalg.norm(kontura - [centar_x, centar_y], axis=2)
    max_idx = np.argmax(udaljenosti)
    tx, ty = kontura[max_idx][0]

    # Vektorski proizvod za određivanje orijentacije (znak je presudan)
    smer = (tx - centar_x) * (ry - centar_y) - (ty - centar_y) * (rx - centar_x)
    return np.sign(smer)

def procesiraj_sliku_i_nadji_p(path):
    izvorna = cv2.imread(path)
    if izvorna is None:
        print("Greška kod učitavanja!")
        return None

    # Prebacivanje u sivo i binarna maska
    gray_img = cv2.cvtColor(izvorna, cv2.COLOR_BGR2GRAY)
    # Koristimo bitwise OR za thresh tipove (isto kao +, ali izgleda profi)
    _, binary = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Nalazimo sve konture i njihovu hijerarhiju
    c_list, h_data = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if h_data is None: return izvorna

    p_sablon = None
    sablon_smer = 0 

    # PRVI PROLAZ: Tražimo prvo slovo P za uzorak
    for i, c in enumerate(c_list):
        if h_data[0][i][3] == -1: # Spoljašnja kontura
            px, py, pw, ph = cv2.boundingRect(c)
            velicina = cv2.contourArea(c)
            # Uslov za poziciju (gore levo) i površinu
            if px < izvorna.shape[1] / 2 and py < izvorna.shape[0] / 2 and 1500 < velicina < 15000:
                dete = h_data[0][i][2]
                if dete != -1 and h_data[0][dete][0] == -1:
                    p_sablon = c
                    sablon_smer = izracunaj_stranu_rupe(c, c_list[dete])
                    break

    izlazna_slika = izvorna.copy()

    # DRUGI PROLAZ: Provera svih kontura
    for i, c in enumerate(c_list):
        if h_data[0][i][3] != -1: continue # Preskačemo ako nije koren

        povrsina = cv2.contourArea(c)
        if povrsina < 100 or povrsina > 15000: continue

        # Provera broja rupa
        broj_rupa = 0
        idx_deteta = h_data[0][i][2]
        temp = idx_deteta
        while temp != -1:
            broj_rupa += 1
            temp = h_data[0][temp][0]

        if broj_rupa != 1: continue

        # Solidity i Hole ratio provere
        konveks = cv2.convexHull(c)
        s_area = cv2.contourArea(konveks)
        punoca = povrsina / s_area if s_area > 0 else 0

        rupa_povrsina = cv2.contourArea(c_list[idx_deteta])
        h_koeficijent = rupa_povrsina / povrsina

        # Shape matching (podudaranje oblika)
        if p_sablon is not None:
            razlika = cv2.matchShapes(p_sablon, c, cv2.CONTOURS_MATCH_I1, 0)
        else:
            razlika = 0.5

        # Provera strane rupe (ključno da se izbaci 'q')
        trenutni_smer = izracunaj_stranu_rupe(c, c_list[idx_deteta])

        # Glavni uslovi za detekciju
        if razlika < 0.41 and punoca < 0.82 and h_koeficijent > 0.5:
            if trenutni_smer == sablon_smer:
                x, y, w, h = cv2.boundingRect(c)
                # Iscrtavanje - promenjena boja u zelenu (0,255,0) čisto vizuelno
                cv2.rectangle(izlazna_slika, (x-4, y-4), (x+w+4, y+h+4), (0, 255, 0), 2)

    return izlazna_slika

# --- Main ---
putanja_do_slike = 'ulaz.png'
final_img = procesiraj_sliku_i_nadji_p(putanja_do_slike)

if final_img is not None:
    cv2.imshow('Rezultat Detekcije', final_img)
    cv2.imwrite('finalni_p_output.png', final_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()