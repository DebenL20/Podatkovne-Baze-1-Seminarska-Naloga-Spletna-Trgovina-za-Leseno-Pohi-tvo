from bottle import Bottle, run, template, static_file, request, redirect, response
from model import Izdelek, Dobavitelj, Stranka
import os
import csv

app = Bottle()


CSV_UPORABNIKI = "uporabniki.csv"

@app.route('/')
def zacetna_stran():
    return template("Začetna_stran.html")

@app.route('/izdelki')
def prikazi_izdelke():
    uporabnik = request.get_cookie("trenutni_uporabnik")
    izdelki = Izdelek.vsi_izdelki()
    sort = request.query.get('sort')
    if sort == 'asc':
        izdelki.sort(key=lambda x: x.cena)
    elif sort == 'desc':
        izdelki.sort(key=lambda x: x.cena, reverse=True)
    return template("Seznam_izdelkov.html", izdelki=izdelki, uporabnik=uporabnik)

# Strezba statične CSS datoteke
@app.route('/static/<filename>')
def serve_static(filename):
    return static_file(filename, root=os.path.join(os.getcwd(), 'static'))



@app.route('/dobavitelj/<dobavitelj_id>/<izdelek_id>')
def prikazi_dobavitelja(dobavitelj_id, izdelek_id):
    dobavitelj = Dobavitelj.najdi_po_id(dobavitelj_id)
    izdelek = Izdelek.najdi_po_id(izdelek_id)
    return template("Dobavitelj_izdelka.html", dobavitelj=dobavitelj, izdelek=izdelek)


@app.route('/dodaj_v_kosarico/<izdelek_id>', method='POST')
def dodaj_v_kosarico(izdelek_id):
    uporabnik_ime = request.get_cookie("trenutni_uporabnik")
    if not uporabnik_ime:
        return template("Obvestilo_o_prijavi.html")

    stranka = Stranka.najdi_po_imenu(uporabnik_ime)
    if not stranka:
        return redirect('/prijava')

    izdelek = Izdelek.najdi_po_id(izdelek_id)
    if izdelek:
        stranka.dodaj_v_kosarico(izdelek.id)
        

    return redirect('/kosarica')




@app.route('/kosarica')
def prikazi_kosarico():
    uporabnik_ime = request.get_cookie("trenutni_uporabnik")
    if not uporabnik_ime:
        return template("Obvestilo_o_prijavi.html")

    stranka = Stranka.najdi_po_imenu(uporabnik_ime)
    if not stranka:
        return redirect('/prijava')

    izdelki = stranka.pridobi_kosarico()
    skupna_cena = sum(izdelek.cena for izdelek in izdelki)

    return template("Košarica.html", izdelki=izdelki, skupna_cena=skupna_cena)

@app.route('/izbrisi/<index:int>', method="POST")
def izbrisi_izdelek(index):
    uporabnik_ime = request.get_cookie("trenutni_uporabnik")
    if uporabnik_ime:
        stranka = Stranka.najdi_po_imenu(uporabnik_ime)
        if stranka:
            stranka.odstrani_iz_kosarice(index)
            
    return redirect('/kosarica')


@app.route('/slike_izdelkov/<filename>')
def serviraj_sliko(filename):
    return static_file(filename, root=os.path.join(os.getcwd(), 'slike_izdelkov'))

CSV_UPORABNIKI = "uporabniki.csv"

# Funkcija za shranjevanje uporabnikov v CSV
def shrani_uporabnika(uporabnisko_ime, geslo):
    with open(CSV_UPORABNIKI, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([uporabnisko_ime, geslo])

# Funkcija za branje uporabnikov iz CSV
def preberi_uporabnike():
    uporabniki = {}
    try:
        with open(CSV_UPORABNIKI, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for vrstica in reader:
                if len(vrstica) > 1:
                    uporabniki[vrstica[0]] = vrstica[1]  # Shranimo samo geslo
    except FileNotFoundError:
        pass
    return uporabniki


@app.route('/prijava', method=['GET', 'POST'])
def prijava():
    if request.method == 'POST':
        uporabnisko_ime = request.forms.get('uporabnisko_ime')
        geslo = request.forms.get('geslo')
        uporabniki = preberi_uporabnike()
        if uporabnisko_ime in uporabniki and uporabniki[uporabnisko_ime] == geslo:
            response.set_cookie("trenutni_uporabnik", uporabnisko_ime, path='/')
            redirect('/izdelki')
        else:
            return "<h1>Nepravilno uporabniško ime ali geslo!</h1><a href='/prijava'>Poskusi znova</a>"
    return template("prijava.html")


@app.route('/registracija', method=['GET', 'POST'])
def registracija():
    if request.method == 'POST':
        uporabnisko_ime = request.forms.get('uporabnisko_ime')
        geslo = request.forms.get('geslo')
        potrdi_geslo = request.forms.get('potrdi_geslo')

        if geslo != potrdi_geslo:
            return "<h1>Napaka: Gesli se ne ujemata!</h1><a href='/registracija'>Poskusi znova</a>"

        # Preveri, ali uporabnik že obstaja v bazi
        if Stranka.najdi_po_imenu(uporabnisko_ime):
            return "<h1>Napaka: Uporabniško ime že obstaja!</h1><a href='/registracija'>Poskusi znova</a>"

        # Shrani v bazo
        stranka = Stranka(None, uporabnisko_ime, geslo, [])
        stranka.shrani()

        # Shrani tudi v CSV
        shrani_uporabnika(uporabnisko_ime, geslo)

        return "<h1>Uspešna registracija!</h1><a href='/prijava'>Prijava</a>"

    return template("registracija.html")


@app.route('/odjava')
def odjava():
    uporabnik = request.get_cookie("trenutni_uporabnik")
    if uporabnik:
        stranka = Stranka.najdi_po_imenu(uporabnik)
        if stranka:
            stranka.shrani_kosarico()
    response.delete_cookie("trenutni_uporabnik")
    redirect('/izdelki')

@app.route('/zakljucek', method='POST')
def zakljucek_nakupa():
    uporabnik_ime = request.get_cookie("trenutni_uporabnik")
    if not uporabnik_ime:
        return redirect('/prijava')

    stranka = Stranka.najdi_po_imenu(uporabnik_ime)
    if not stranka:
        return redirect('/prijava')

    # Po potrditvi nakupa izprazni košarico
    stranka.kosarica = []
    stranka.shrani_kosarico()

    return template("Zaključen_nakup.html")

if __name__ == "__main__":
    run(app, host='localhost', port=8080, debug=True)
