import sqlite3
from dataclasses import dataclass
from typing import List, Optional

DB_NAME = "pohistvo.sqlite"
CSV_UPORABNIKI = "uporabniki.csv"
@dataclass
class Izdelek:
    id: Optional[int]
    ime: str
    opis: str
    cena: float
    zaloga: int
    dobavitelj_id: int  # NOV STOLPEC

    @staticmethod
    def ustvari_tabelo():
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS izdelki (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ime TEXT NOT NULL,
                    opis TEXT,
                    cena REAL NOT NULL,
                    zaloga INTEGER NOT NULL,
                    dobavitelj_id INTEGER NOT NULL,
                    FOREIGN KEY(dobavitelj_id) REFERENCES dobavitelji(id) ON DELETE CASCADE
                )
            ''')

    @classmethod
    def vsi_izdelki(cls):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute('SELECT id, ime, opis, cena, zaloga, dobavitelj_id FROM izdelki')
            return [cls(*row) for row in cursor.fetchall()]

    @classmethod
    def najdi_po_id(cls, izdelek_id):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute("SELECT id, ime, opis, cena, zaloga, dobavitelj_id FROM izdelki WHERE id = ?", (izdelek_id,))
            rezultat = cursor.fetchone()
            if rezultat:
                return cls(*rezultat)
            return None

@dataclass
class Dobavitelj:
    id: Optional[int]
    ime: str
    naslov: str
    telefonska_stevilka: str

    @staticmethod
    def ustvari_tabelo():
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS dobavitelji (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ime TEXT NOT NULL,
                    naslov TEXT NOT NULL,
                    telefonska_stevilka TEXT NOT NULL
                )
            ''')

    @classmethod
    def najdi_po_id(cls, dobavitelj_id):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute("SELECT id, ime, naslov, telefonska_stevilka FROM dobavitelji WHERE id = ?", (dobavitelj_id,))
            rezultat = cursor.fetchone()
            if rezultat:
                return cls(*rezultat)
            return None


@dataclass
class Stranka:
    id: Optional[int]
    ime: str
    geslo: str
    kosarica: list  # seznam ID-jev izdelkov kot int

    @staticmethod
    def ustvari_tabelo():
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stranke (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ime TEXT UNIQUE NOT NULL,
                    geslo TEXT NOT NULL,
                    kosarica TEXT DEFAULT ''
                )
            ''')

    def shrani(self):
        with sqlite3.connect(DB_NAME) as conn:
            kosarica_csv = ",".join(str(i) for i in self.kosarica)
            if self.id is None:
                cursor = conn.execute('''
                    INSERT INTO stranke (ime, geslo, kosarica)
                    VALUES (?, ?, ?)
                ''', (self.ime, self.geslo, kosarica_csv))
                self.id = cursor.lastrowid
            else:
                conn.execute('''
                    UPDATE stranke
                    SET ime = ?, geslo = ?, kosarica = ?
                    WHERE id = ?
                ''', (self.ime, self.geslo, kosarica_csv, self.id))

    @classmethod
    def najdi_po_imenu(cls, ime):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute("SELECT id, ime, geslo, kosarica FROM stranke WHERE ime = ?", (ime,))
            rezultat = cursor.fetchone()
            if rezultat:
                id, ime, geslo, kosarica_csv = rezultat
                if kosarica_csv.strip():
                    kosarica = [int(i) for i in kosarica_csv.split(",")]
                else:
                    kosarica = []
                return cls(id, ime, geslo, kosarica)
            return None

    def dodaj_v_kosarico(self, izdelek_id):
        self.kosarica.append(izdelek_id)
        self.shrani()

    def odstrani_iz_kosarice(self, index):
        if 0 <= index < len(self.kosarica):
            self.kosarica.pop(index)
            self.shrani()

    def pridobi_kosarico(self):
        return [Izdelek.najdi_po_id(iz_id) for iz_id in self.kosarica if Izdelek.najdi_po_id(iz_id) is not None]

    def posodobi_csv(self):
        uporabniki = {}
        try:
            with open(CSV_UPORABNIKI, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for vrstica in reader:
                    if len(vrstica) > 1:
                        uporabniki[vrstica[0]] = [vrstica[1]] + vrstica[2:]
        except FileNotFoundError:
            pass

        kosarica_ids = [str(i) for i in self.kosarica]
        uporabniki[self.ime] = [self.geslo] + kosarica_ids

        with open(CSV_UPORABNIKI, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for uporabnik, podatki in uporabniki.items():
                writer.writerow([uporabnik] + podatki)




@dataclass
class Narocilo:
    id: Optional[int]
    datum: str
    vrednost: float
    status: str
    stranka_id: int

    @staticmethod
    def ustvari_tabelo():
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS narocila (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datum TEXT NOT NULL,
                    vrednost REAL NOT NULL,
                    status TEXT NOT NULL,
                    stranka_id INTEGER NOT NULL,
                    FOREIGN KEY(stranka_id) REFERENCES stranke(id)
                )
            ''')

    def shrani(self):
        with sqlite3.connect(DB_NAME) as conn:
            if self.id is None:
                cursor = conn.execute('''
                    INSERT INTO narocila (datum, vrednost, status, stranka_id)
                    VALUES (?, ?, ?, ?)
                ''', (self.datum, self.vrednost, self.status, self.stranka_id))
                self.id = cursor.lastrowid
            else:
                conn.execute('''
                    UPDATE narocila
                    SET datum = ?, vrednost = ?, status = ?, stranka_id = ?
                    WHERE id = ?
                ''', (self.datum, self.vrednost, self.status, self.stranka_id, self.id))

def ustvari_bazo():
    Izdelek.ustvari_tabelo()
    Dobavitelj.ustvari_tabelo()
    Stranka.ustvari_tabelo()
    Narocilo.ustvari_tabelo()

def pobrisi_bazo():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('DROP TABLE IF EXISTS izdelki')
        conn.execute('DROP TABLE IF EXISTS dobavitelji')
        conn.execute('DROP TABLE IF EXISTS stranke')
        conn.execute('DROP TABLE IF EXISTS narocila')


import csv

def preberi_csv(ime_datoteke):
    """
    Prebere podatke iz CSV datoteke in jih vrne kot seznam slovarjev.
    """
    with open(ime_datoteke, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def uvozi_podatke(ime_datoteke):
    """
    Prebere podatke iz CSV in jih shrani v bazo.
    """
    podatki = preberi_csv(ime_datoteke)
    
    with sqlite3.connect(DB_NAME) as conn:
        for vrstica in podatki:
            # Preveri, ali dobavitelj že obstaja
            cursor = conn.execute('''
                SELECT id FROM dobavitelji WHERE ime = ? AND naslov = ? AND telefonska_stevilka = ?
            ''', (vrstica["dobavitelj_ime"], vrstica["dobavitelj_naslov"], vrstica["dobavitelj_telefon"]))
            
            rezultat = cursor.fetchone()
            if rezultat:
                dobavitelj_id = rezultat[0]
            else:
                cursor = conn.execute('''
                    INSERT INTO dobavitelji (ime, naslov, telefonska_stevilka)
                    VALUES (?, ?, ?)
                ''', (vrstica["dobavitelj_ime"], vrstica["dobavitelj_naslov"], vrstica["dobavitelj_telefon"]))
                dobavitelj_id = cursor.lastrowid
            
            # Dodaj izdelek
            cursor = conn.execute('''
                INSERT INTO izdelki (ime, opis, cena, zaloga, dobavitelj_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (vrstica["izdelek_ime"], vrstica["izdelek_opis"], float(vrstica["izdelek_cena"]),
                  int(vrstica["izdelek_zaloga"]), dobavitelj_id))
            izdelek_id = cursor.lastrowid



        conn.commit()


def uvozi_stranke(ime_datoteke):
    """
    Prebere uporabnike iz CSV datoteke in jih shrani v tabelo stranke.
    Format CSV:
    ime,geslo[,izdelek_id1,izdelek_id2,...]
    """
    with open(ime_datoteke, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for vrstica in reader:
            if len(vrstica) >= 2:
                ime = vrstica[0]
                geslo = vrstica[1]
                kosarica = [int(i) for i in vrstica[2:]] if len(vrstica) > 2 else []
                stranka = Stranka(id=None, ime=ime, geslo=geslo, kosarica=kosarica)
                stranka.shrani()



if __name__ == "__main__":
    pobrisi_bazo()
    ustvari_bazo()
    
    # Uvozi podatke iz CSV
    uvozi_podatke("podatki.csv")
    # Uvozi stranke
    uvozi_stranke("uporabniki.csv")

    print("Baza je bila uspešno napolnjena s podatki.")
