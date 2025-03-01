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

if __name__ == "__main__":
    pobrisi_bazo()
    ustvari_bazo()
    
    # Dodajanje primera podatkov
    izdelek = Izdelek(None, "Miza", "Lesena miza", 120.0, 10)
    izdelek.shrani()

    dobavitelj = Dobavitelj(None, "Lesni Dobavitelj", "Ljubljana", "040123456")
    dobavitelj.shrani()

    stranka = Stranka(None, "Janez Novak", "Maribor", "031987654")
    stranka.shrani()

    narocilo = Narocilo(None, "2025-01-11", 120.0, "Oddano", stranka.id)
    narocilo.shrani()
