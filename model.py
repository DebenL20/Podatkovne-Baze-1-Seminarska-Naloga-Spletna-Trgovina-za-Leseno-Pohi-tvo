import sqlite3
from dataclasses import dataclass
from typing import List, Optional

DB_NAME = "pohistvo.sqlite"

@dataclass
class Izdelek:
    id: Optional[int]
    ime: str
    opis: str
    cena: float
    zaloga: int

    @staticmethod
    def vsi_izdelki():
        """
        Vrne seznam vseh izdelkov v bazi.
        """
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute('SELECT id, ime, opis, cena, zaloga FROM izdelki')
            return [Izdelek(*row) for row in cursor.fetchall()]

    @staticmethod
    def ustvari_tabelo():
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS izdelki (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ime TEXT NOT NULL,
                    opis TEXT,
                    cena REAL NOT NULL,
                    zaloga INTEGER NOT NULL
                )
            ''')

    def shrani(self):
        with sqlite3.connect(DB_NAME) as conn:
            if self.id is None:
                cursor = conn.execute('''
                    INSERT INTO izdelki (ime, opis, cena, zaloga)
                    VALUES (?, ?, ?, ?)
                ''', (self.ime, self.opis, self.cena, self.zaloga))
                self.id = cursor.lastrowid
            else:
                conn.execute('''
                    UPDATE izdelki
                    SET ime = ?, opis = ?, cena = ?, zaloga = ?
                    WHERE id = ?
                ''', (self.ime, self.opis, self.cena, self.zaloga, self.id))

    @staticmethod
    def vsi():
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute('SELECT id, ime, opis, cena, zaloga FROM izdelki')
            return [Izdelek(*row) for row in cursor.fetchall()]

    @classmethod
    def najdi_po_id(cls, izdelek_id):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.execute("SELECT id, ime, opis, cena, zaloga FROM izdelki WHERE id = ?", (izdelek_id,))
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

    def shrani(self):
        with sqlite3.connect(DB_NAME) as conn:
            if self.id is None:
                cursor = conn.execute('''
                    INSERT INTO dobavitelji (ime, naslov, telefonska_stevilka)
                    VALUES (?, ?, ?)
                ''', (self.ime, self.naslov, self.telefonska_stevilka))
                self.id = cursor.lastrowid
            else:
                conn.execute('''
                    UPDATE dobavitelji
                    SET ime = ?, naslov = ?, telefonska_stevilka = ?
                    WHERE id = ?
                ''', (self.ime, self.naslov, self.telefonska_stevilka, self.id))
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
    naslov: str
    telefonska_stevilka: str

    @staticmethod
    def ustvari_tabelo():
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stranke (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ime TEXT NOT NULL,
                    naslov TEXT NOT NULL,
                    telefonska_stevilka TEXT NOT NULL
                )
            ''')

    def shrani(self):
        with sqlite3.connect(DB_NAME) as conn:
            if self.id is None:
                cursor = conn.execute('''
                    INSERT INTO stranke (ime, naslov, telefonska_stevilka)
                    VALUES (?, ?, ?)
                ''', (self.ime, self.naslov, self.telefonska_stevilka))
                self.id = cursor.lastrowid
            else:
                conn.execute('''
                    UPDATE stranke
                    SET ime = ?, naslov = ?, telefonska_stevilka = ?
                    WHERE id = ?
                ''', (self.ime, self.naslov, self.telefonska_stevilka, self.id))

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
            izdelek = Izdelek(None, vrstica["izdelek_ime"], vrstica["izdelek_opis"],
                              float(vrstica["izdelek_cena"]), int(vrstica["izdelek_zaloga"]))
            izdelek.shrani()

            dobavitelj = Dobavitelj(None, vrstica["dobavitelj_ime"], vrstica["dobavitelj_naslov"],
                                    vrstica["dobavitelj_telefon"])
            dobavitelj.shrani()

            stranka = Stranka(None, vrstica["stranka_ime"], vrstica["stranka_naslov"],
                              vrstica["stranka_telefon"])
            stranka.shrani()

            narocilo = Narocilo(None, vrstica["narocilo_datum"], float(vrstica["narocilo_vrednost"]),
                                vrstica["narocilo_status"], stranka.id)
            narocilo.shrani()


if __name__ == "__main__":
    pobrisi_bazo()
    ustvari_bazo()
    
    # Uvozi podatke iz CSV
    uvozi_podatke("podatki.csv")

    print("Baza je bila uspešno napolnjena s podatki.")
