from collections import deque # Uvozimo strukturu "red" (queue) koja je neophodna za BFS algoritam (Traženje po širini)

# 1. FUNKCIJA CILJA - Proverava da li su kuglice ispravno grupisane
def proveri_cilj(stanje):
    # 'stanje' je niz od 12 elemenata (npr. prve 4 su zelene, druge 4 crvene...)
    grupa1 = set(stanje[0:4])   # Uzimamo prve četiri kuglice i pravimo skup (skup briše duplikate)
    grupa2 = set(stanje[4:8])   # Uzimamo srednje četiri kuglice i pravimo skup
    grupa3 = set(stanje[8:12])  # Uzimamo poslednje četiri kuglice i pravimo skup
    
    # Ako svaki skup ima samo 1 element, to znači da su u toj grupi sve kuglice iste boje
    # Primer: set(['G', 'G', 'G', 'G']) postaje {'G'}, što ima dužinu 1. To je cilj!
    return len(grupa1) == 1 and len(grupa2) == 1 and len(grupa3) == 1

# 2. OPERATOR PROMENE STANJA - Dinamički generiše nove mogućnosti (susedne zamene)
def dobij_sledbenike(stanje):
    sledbenici = []             # Lista u koju ćemo smestiti sve moguće nove rasporede
    lista_kuglica = list(stanje) # Pretvaramo torku u listu jer torke ne dozvoljavaju izmene (swap)
    
    # Prolazimo kroz niz i pokušavamo da zamenimo svaka dva susedna mesta (0 sa 1, 1 sa 2... do 10 sa 11)
    for i in range(len(lista_kuglica) - 1):
        nova_varijanta = lista_kuglica[:] # Pravimo kopiju trenutnog niza da ne bismo kvarili original
        
        # OPERATOR: Zamenjujemo mesta dvema susednim kuglicama (klasičan swap)
        nova_varijanta[i], nova_varijanta[i+1] = nova_varijanta[i+1], nova_varijanta[i]
        
        # Novo stanje pretvaramo nazad u torku (tuple) i dodajemo u listu sledbenika
        sledbenici.append(tuple(nova_varijanta))
        
    return sledbenici # Vraćamo listu svih 11 mogućih pomeraja iz trenutnog stanja

# 3. BFS ALGORITAM - Traženje po širini (modifikovan prema materijalima sa vežbi)
def trazenje_po_sirini(pocetno_stanje):
    # Formiramo RED (queue) koji inicijalno sadrži startni čvor i putanju koja do njega vodi
    # Putanja je lista koja pamti "redosled promena" kako zadatak zahteva
    red = deque([(pocetno_stanje, [pocetno_stanje])])
    
    # Skup 'poseceni' služi da ne bismo ponovo obrađivali isto stanje i upali u beskonačnu petlju
    poseceni = {pocetno_stanje}
    
    # Dokle god u redu ima elemenata za proveru:
    while red:
        # Uzimamo prvi element sa leve strane (popleft) - princip Prvi Ušao, Prvi Izašao (FIFO)
        (trenutno_stanje, putanja) = red.popleft()
        
        # Pozivamo funkciju za proveru da li je trenutni niz kuglica onaj koji tražimo
        if proveri_cilj(trenutno_stanje):
            return putanja # Ako jeste, vraćamo kompletnu istoriju poteza (putanju)
            
        # Ako nije cilj, pomoću OPERATORA generišemo sva moguća sledeća stanja (sledbenike)
        for sledbenik in dobij_sledbenike(trenutno_stanje):
            # Proveravamo da li smo taj raspored kuglica već ranije negde videli
            if sledbenik not in poseceni:
                poseceni.add(sledbenik) # Beležimo ga kao viđenog
                # Dodajemo ga u red za dalju proveru, a u putanju mu dopisujemo ovo novo stanje
                red.append((sledbenik, putanja + [sledbenik]))
    
    return None # Ako pretražimo sve i ne nađemo ništa (teoretski nemoguće ovde)



# Definišemo početni niz sa tvoje slike: 
# G - Zelena, R - Crvena, B - Plava
start = ('G', 'R', 'B', 'R', 'G', 'B', 'B', 'R', 'G', 'G', 'B', 'R')

print("Tražim najkraći put do rešenja...")
rezultat = trazenje_po_sirini(start) # Pokrećemo algoritam

# Ako smo pronašli rešenje, ispisujemo ga korak po korak
if rezultat:
    print(f"Pronađeno! Potrebno je {len(rezultat) - 1} zamena.")
    for korak_broj, raspored in enumerate(rezultat):
        # Ispisujemo redni broj koraka i vizuelni prikaz kuglica
        print(f"Korak {korak_broj}: {' '.join(raspored)}")
else:
    print("Nema rešenja.")