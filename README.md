# Podatkovne-Baze-1-Seminarska-Naloga-Spletna-Trgovina-za-Leseno-Pohistvo
Podatkovne Baze 1 Seminarska Naloga: Spletna Trgovina za Leseno Pohištvo

To je preprosta spletna aplikacija za upravljanje spletne trgovine s pohištvom, kjer lahko uporabniki:
- brskajo po izdelkih,
- dodajajo izdelke v košarico,
- se registrirajo in prijavijo,
- upravljajo svojo košarico.

Aplikacija uporablja Python, Bottle spletni okvir in SQLite bazo podatkov.

---

## 📁 Struktura projekta

- `main.py` – inicializira bazo in zažene spletni strežnik.
- `Model.py` – vsebuje definicije razredov in funkcije za delo z bazo.
- `spletni_vmesnik.py` – vsebuje spletni vmesnik (rute, HTML predloge).
- `podatki.csv` – začetni podatki o izdelkih in dobaviteljih.
- `uporabniki.csv` – začetni podatki o uporabnikih.

---

## 🗃️ Struktura SQL tabel

### `izdelki`
| Stolpec         | Tip     | Opis                         |
|------------------|----------|------------------------------|
| `id`             | INTEGER | Primarni ključ               |
| `ime`            | TEXT    | Ime izdelka                  |
| `opis`           | TEXT    | Opis izdelka                 |
| `cena`           | REAL    | Cena izdelka                 |
| `zaloga`         | INTEGER | Količina na zalogi           |
| `dobavitelj_id`  | INTEGER | Tuji ključ na `dobavitelji`  |

### `dobavitelji`
| Stolpec              | Tip     | Opis              |
|-----------------------|----------|-------------------|
| `id`                  | INTEGER | Primarni ključ    |
| `ime`                 | TEXT    | Ime dobavitelja   |
| `naslov`              | TEXT    | Naslov            |
| `telefonska_stevilka` | TEXT    | Telefonska številka |

### `stranke`
| Stolpec   | Tip     | Opis                        |
|------------|----------|-----------------------------|
| `id`       | INTEGER | Primarni ključ              |
| `ime`      | TEXT    | Uporabniško ime (unikatno)  |
| `geslo`    | TEXT    | Geslo (trenutno v tekstovni obliki) |

### `kosarice`
| Stolpec      | Tip     | Opis                                 |
|---------------|----------|----------------------------------------|
| `stranka_id`  | INTEGER | Tuji ključ na `stranke`               |
| `izdelek_id`  | INTEGER | Tuji ključ na `izdelki`               |

---

## 🚀 Zagon aplikacije

1. Prepričaj se, da imaš nameščen Python 3.
2. Poženi main.py


