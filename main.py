

from model import pobrisi_bazo, ustvari_bazo, uvozi_podatke
from spletni_vmesnik import app
from bottle import run

if __name__ == "__main__":
    pobrisi_bazo()
    ustvari_bazo()
    
    # Uvozi podatke iz CSV
    uvozi_podatke("podatki.csv")

    print("Baza je bila uspešno napolnjena s podatki.")
    
    # Zaženi spletni vmesnik
    run(app, host='localhost', port=8080, debug=True)
