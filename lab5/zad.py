import copy  # Uvozimo biblioteku 'copy'. Python po defaultu kopira samo adresu (referencu) objekta.
             # Nama treba 'deepcopy' (duboko kopiranje) da bismo napravili potpunu kopiju domena.
             # To radimo da bi svaki nivo pretrage imao svoju verziju domena koju može da kvari, 
             # a da ne uništi podatke nivoima iznad sebe.

# Definisanje konstanti (simbola) - ovi brojevi nemaju specijalnu moć, služe samo nama radi jasnoće.
EMPTY = 0    # Broj 0 koristimo kao mentalnu oznaku za "ovde nema ničega".
QUEEN = 1    # Broj 1 koristimo kao mentalnu oznaku za "ovde je kraljica".

def is_safe(row, col, assignment):
    """
    Svrha: Proverava da li bi nova kraljica na poziciji (row, col) bila 'pojedena'.
    row: Red u koji želimo da stavimo kraljicu (npr. 2).
    col: Kolona u koju želimo da stavimo kraljicu (npr. 3).
    assignment: Rečnik koji čuva već postavljene kraljice u formatu {red: kolona}.
    """
    # .items() pretvara rečnik u listu parova. r je red stare kraljice, c je njena kolona.
    for r, c in assignment.items():
        # PROVERA KOLONE:
        # Ako je kolona nove kraljice (col) ista kao kolona stare kraljice (c), napadaju se.
        if c == col:
            return False  # Vrati 'False' - NIJE BEZBEDNO.
            
        # PROVERA DIJAGONALA:
        # Koristimo matematiku: na dijagonali je razmak između redova isti kao razmak između kolona.
        # abs() je apsolutna vrednost (pretvara negativan broj u pozitivan).
        # npr. (0,0) i (2,2) -> abs(0-2) je 2, abs(0-2) je 2. 2 == 2 znači da su na istoj dijagonali.
        if abs(r - row) == abs(c - col):
            return False  # Vrati 'False' - NIJE BEZBEDNO.
            
    # Ako prođemo kroz celu petlju i nijedan 'if' se ne aktivira, znači da je polje sigurno.
    return True  # Vrati 'True' - MOŽEŠ OVDE STAVITI KRALJICU.

def get_degree(var, unassigned_vars, domains):
    """
    Svrha: Računa koliko 'problema' ovaj red pravi drugim redovima koji još nemaju kraljicu.
    var: Red koji trenutno analiziramo.
    unassigned_vars: Lista redova koji još uvek čekaju svoju kraljicu.
    domains: Rečnik koji sadrži moguće kolone za svaki red.
    """
    degree = 0  # Počinjemo brojanje od nule.
    # Prolazimo kroz sve ostale slobodne redove.
    for other_var in unassigned_vars:
        # Ako taj drugi red nije ovaj naš trenutni red...
        if var != other_var:
            degree += 1  # Povećaj brojač. U šahu, kraljica u jednom redu utiče na svaki drugi red.
            # Degree heuristika uvek bira varijablu koja ima najviše veza sa ostalima.
    return degree  # Vraća ukupan broj suseda na koje ovaj red utiče.

def select_unassigned_variable(unassigned_vars, domains):
    """
    Svrha: Donosi odluku koji ćemo red (varijablu) sledeći pokušati da popunimo.
    Koristi 'Degree Heuristic' - strategiju 'napadni najteži deo problema prvo'.
    """
    # max() funkcija traži element sa najvećom vrednošću.
    # key=lambda v: ... govori Pythonu: "Nemoj porediti same brojeve redova, 
    # već pozovi get_degree za svaki red i uporedi njihove rezultate."
    return max(unassigned_vars, key=lambda v: get_degree(v, unassigned_vars, domains))

def forward_checking(var, value, domains, unassigned_vars):
    """
    Svrha: 'Gledanje u budućnost'. Čim stavimo kraljicu, odmah brišemo polja 
    koja ona napada iz domena svih budućih redova.
    var: Red u koji smo upravo stavili kraljicu.
    value: Kolona u koju smo je stavili.
    domains: Trenutne liste mogućih kolona za sve redove.
    unassigned_vars: Redovi koji još uvek nemaju kraljicu.
    """
    # Pravimo 'deepcopy' celog rečnika domena. Ovo je neophodno jer ako ovaj put
    # pretrage ne uspe, moramo imati sačuvan originalni domen da se vratimo nazad.
    new_domains = copy.deepcopy(domains)
    
    # Prolazimo kroz svaki red koji tek treba da dobije kraljicu.
    for other_var in unassigned_vars:
        to_remove = []  # Lista u koju ćemo privremeno staviti kolone koje postaju nemoguće.
        
        # Proveravamo svaku preostalu kolonu (val) u tom budućem redu (other_var).
        for val in new_domains[other_var]:
            # Ako ta pozicija (other_var, val) dolazi pod udar naše nove kraljice (var, value)...
            # Koristimo istu logiku za kolonu i dijagonalu kao u is_safe.
            if val == value or abs(other_var - var) == abs(val - value):
                to_remove.append(val)  # Zapamti ovu kolonu za brisanje.
        
        # Sada stvarno brišemo te nemoguće kolone iz domena tog budućeg reda.
        for val in to_remove:
            new_domains[other_var].remove(val)
            
        # PROVERA KATASTROFE: Ako je neki red ostao sa praznim domenom (not new_domains[other_var])...
        # To znači da smo stavili kraljicu tako da u nekom od budućih redova VIŠE NEMA MESTA.
        if not new_domains[other_var]:
            return None  # Vraćamo 'None' kao alarm: "Ovaj potez je loš, vrati se nazad!"
            
    # Ako su svi budući redovi preživeli (imaju bar jednu slobodnu kolonu), vraćamo nove domene.
    return new_domains

def backtracking_search(assignment, unassigned_vars, domains):
    """
    Svrha: Srce algoritma. Sistematski isprobava sve opcije dok ne nađe rešenje.
    assignment: Rečnik koji se postepeno puni {red: kolona}.
    unassigned_vars: Lista redova koji su još slobodni.
    domains: Trenutne mogućnosti za svaki red.
    """
    # USLOV ZA KRAJ (USPEH): Ako više nema slobodnih redova, znači da smo sve popunili!
    if not unassigned_vars:
        return assignment  # Vrati rečnik sa kompletnim rešenjem.

    # 1. KORAK: Odaberi najuticajniji slobodan red koristeći našu heuristiku.
    var = select_unassigned_variable(unassigned_vars, domains)
    
    # Pravimo kopiju liste slobodnih varijabli i iz nje izbacujemo ovaj red koji smo upravo izabrali.
    # To radimo da bi sledeći rekurzivni poziv znao da je ovaj red 'zauzet'.
    new_unassigned_vars = [v for v in unassigned_vars if v != var]

    # 2. KORAK: Isprobavaj redom svaku kolonu (value) koja je preostala u domenu za taj red.
    for value in domains[var]:
        # Provera: Da li je uopšte bezbedno staviti kraljicu na (var, value) s obzirom na trenutno stanje?
        if is_safe(var, value, assignment):
            # Ako jeste, 'zapiši' to u privremeno rešenje.
            assignment[var] = value
            
            # 3. KORAK: Forward Checking (pogledaj u budućnost).
            # new_domains će biti ili None (ako je potez blokirao budućnost) ili očišćeni domeni.
            new_domains = forward_checking(var, value, domains, new_unassigned_vars)
            
            # Ako potez nije uništio šanse za buduće redove:
            if new_domains is not None:
                # REKURZIJA: Pozovi backtracking ponovo da pokušaš da popuniš sledeći red.
                result = backtracking_search(assignment, new_unassigned_vars, new_domains)
                
                # Ako taj poziv duboko dole u stablu pretrage nađe rešenje...
                if result is not None:
                    return result  # Šalji rešenje skroz do vrha!
            
            # 4. KORAK: BACKTRACK (Povratak).
            # Ako smo došli ovde, znači da ovaj 'value' (kolona) NIJE vodio do rešenja.
            # Brišemo je iz assignment-a i petlja ide dalje da proba sledeći 'value' iz domena.
            del assignment[var]

    # Ako smo probali sve kolone iz domena i nijedna nije uspela, vrati None.
    return None

def print_board(result):
    """Svrha: Pretvara rečnik {red: kolona} u vizuelni prikaz šahovske table."""
    if not result:
        print("Nema rešenja.")
        return
    # Spoljna petlja ide kroz redove (od 0 do 3).
    for r in range(4):
        row_str = ""  # Svaki red počinje kao prazan tekst.
        # Unutrašnja petlja ide kroz kolone (od 0 do 3).
        for c in range(4):
            # result[r] nam kaže u kojoj je koloni kraljica u redu 'r'.
            # Ako je to baš trenutna kolona 'c', pišemo Q.
            if result[r] == c:
                row_str += " Q "
            else:
                row_str += " . "  # Inače pišemo tačku za prazno polje.
        print(row_str)  # Ispiši ceo formiran string za taj red.

# --- GLAVNI DEO PROGRAMA ---

n = 4  # Postavljamo problem za 4 kraljice.

# DOMENI: Pravimo rečnik gde je za svaki red (0,1,2,3) vrednost lista [0,1,2,3].
# To znači da svaka kraljica na početku može biti u bilo kojoj koloni.
# List comprehension [i for i in...] je brz način za pravljenje liste.
initial_domains = {i: list(range(n)) for i in range(n)}

# UNASSIGNED: Na početku, svi redovi (0,1,2,3) su bez kraljice.
initial_unassigned = list(range(n))

# POKRETANJE:
# {} -> Počinjemo sa totalno praznim rešenjem (nula postavljenih kraljica).
solution = backtracking_search({}, initial_unassigned, initial_domains)

# FINALNI ISPIS:
print("Rešenje za 4 kraljice (Backtracking + Forward Checking + Degree Heuristic):")
print_board(solution)