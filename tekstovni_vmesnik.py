from model import Izdelek
from enum import Enum

class Meni(Enum):
    PREGLED_IZDELKOV = 'Pregled vseh izdelkov'
    IZDELEK_PODROBNOSTI = 'Podrobnosti izdelka'
    IZHOD = 'Izhod'

def vnesi_izbiro(moznosti, izpis=lambda x: x):
    """
    Prikaži možne izbire in vrni izbrano.
    """
    moznosti = list(moznosti)
    for i, moznost in enumerate(moznosti, 1):
        print(f'{i}) {izpis(moznost)}')
    while True:
        vnos = input('> ')
        try:
            if vnos == '':
                raise KeyboardInterrupt
            izbira = int(vnos) - 1
            if izbira < 0:
                raise IndexError
            return moznosti[izbira]
        except (ValueError, IndexError):
            print("Napačna izbira, poskusi znova!")

def prikazi_izdelke():
    """
    Izpiši vse izdelke v bazi.
    """
    izdelki = Izdelek.vsi_izdelki()
    if not izdelki:
        print("V bazi ni izdelkov.")
    else:
        print("Izdelki v bazi:")
        for izdelek in izdelki:
            print(f'- {izdelek.id}: {izdelek.ime} (Cena: {izdelek.cena}€, Zaloga: {izdelek.zaloga})')

def podrobnosti_izdelka():
    """
    Izpiši podrobnosti za izbran izdelek.
    """
    id_izdelka = input("Vnesi ID izdelka: ")
    try:
        izdelek = Izdelek.najdi_po_id(id_izdelka)
        if izdelek:
            print(f"Podrobnosti izdelka:")
            print(f"Ime: {izdelek.ime}")
            print(f"Opis: {izdelek.opis}")
            print(f"Cena: {izdelek.cena}€")
            print(f"Zaloga: {izdelek.zaloga}")
        else:
            print("Izdelek s tem ID-jem ne obstaja.")
    except Exception as e:
        print(f"Napaka: {e}")

def glavni_meni():
    print("Dobrodošli v bazi pohištva!")
    while True:
        print("Kaj želite narediti?")
        try:
            izbira = vnesi_izbiro(Meni, lambda x: x.value)
        except KeyboardInterrupt:
            izbira = Meni.IZHOD
        if izbira == Meni.PREGLED_IZDELKOV:
            try:
                prikazi_izdelke()
            except KeyboardInterrupt:
                continue
        elif izbira == Meni.IZDELEK_PODROBNOSTI:
            podrobnosti_izdelka()
        elif izbira == Meni.IZHOD:
            print("Nasvidenje!")
            return

glavni_meni()