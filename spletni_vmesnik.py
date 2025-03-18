from bottle import Bottle, run, template, static_file, request, redirect, response
from model import Izdelek, Dobavitelj
import os
import csv

app = Bottle()

kosarica = []  # Seznam za shranjevanje izdelkov v košarici
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
                if len(vrstica) == 2:
                    uporabniki[vrstica[0]] = vrstica[1]
    except FileNotFoundError:
        pass
    return uporabniki

@app.route('/')
def zacetna_stran():
    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Pohištvo</title>
        </head>
        <body>
            <h1>Dobrodošli v spletni trgovini s pohištvom</h1>
            <a href="/izdelki"><button>Pregled izdelkov</button></a>
        </body>
        </html>
    """)

@app.route('/dobavitelj/<dobavitelj_id>/<izdelek_id>')
def prikazi_dobavitelja(dobavitelj_id, izdelek_id):
    dobavitelj = Dobavitelj.najdi_po_id(dobavitelj_id)
    izdelek = Izdelek.najdi_po_id(izdelek_id)

    if not dobavitelj or not izdelek:
        return "<h1>Napaka: Dobavitelj ali izdelek ne obstajata</h1>"

    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Dobavitelj</title>
        </head>
        <body>
            <h1>Dobavitelj za izdelek: {{ izdelek.ime }}</h1>
            <p>Ime dobavitelja: {{ dobavitelj.ime }}</p>
            <p>Naslov: {{ dobavitelj.naslov }}</p>
            <p>Telefon: {{ dobavitelj.telefonska_stevilka }}</p>
            <form action="/dodaj_v_kosarico/{{ izdelek.id }}" method="post">
                <button type="submit">Dodaj v košarico</button>
            </form>
            <a href="/izdelki"><button>Nazaj na izdelke</button></a>
        </body>
        </html>
    """, izdelek=izdelek, dobavitelj=dobavitelj)
@app.route('/dodaj_v_kosarico/<izdelek_id>', method='POST')
def dodaj_v_kosarico(izdelek_id):
    izdelek = Izdelek.najdi_po_id(izdelek_id)
    if izdelek:
        kosarica.append(izdelek)
    redirect('/kosarica')
@app.route('/kosarica')
def prikazi_kosarico():
    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Košarica</title>
        </head>
        <body>
            <h1>Košarica</h1>
            <ul>
                % for izdelek in kosarica:
                    <li>{{ izdelek.ime }} - {{ izdelek.cena }} €</li>
                % end
            </ul>
            <a href="/izdelki"><button>Nazaj na izdelke</button></a>
        </body>
        </html>
    """, kosarica=kosarica)

@app.route('/izdelki')
def prikazi_izdelke():
    izdelki = Izdelek.vsi_izdelki()
    print(f"Naloženih izdelkov: {len(izdelki)}")  # Debug izpis
    trenutni_uporabnik = request.get_cookie("trenutni_uporabnik")
    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Izdelki</title>
        </head>
        <body>
            <h1>Seznam izdelkov</h1>
            <div style="position: absolute; top: 10px; right: 10px;">
                <a href="/kosarica"><button>Košarica</button></a>
                % if trenutni_uporabnik:
                    <span>Prijavljeni kot: {{ trenutni_uporabnik }}</span>
                    <a href="/odjava"><button>Odjava</button></a>
                % else:
                    <a href="/prijava"><button>Prijava</button></a>
                % end
            </div>
            <div>
                % for izdelek in izdelki:
                    <div style="display: inline-block; text-align: center; margin: 10px;">
                        <a href="/dobavitelj/{{izdelek.dobavitelj_id}}/{{izdelek.id}}">
                            <img src="/slike_izdelkov/{{izdelek.ime.lower().replace(' ', '_')}}.png" alt="{{izdelek.ime}}" width="150">
                        </a>
                        <p>{{ izdelek.ime }}</p>
                        <p>{{ izdelek.cena }} €</p>
                    </div>
                % end
            </div>
            <a href="/"><button>Na začetno stran</button></a>
        </body>
        </html>
    """, izdelki=izdelki, trenutni_uporabnik=trenutni_uporabnik)

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
    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Prijava</title>
        </head>
        <body>
            <h1>Prijava</h1>
            <form method="POST">
                <label>Uporabniško ime:</label>
                <input type="text" name="uporabnisko_ime" required><br>
                <label>Geslo:</label>
                <input type="password" name="geslo" required><br>
                <button type="submit">Prijava</button>
            </form>
            <a href="/registracija"><button>Registracija</button></a>
        </body>
        </html>
    """)

@app.route('/odjava')
def odjava():
    response.delete_cookie("trenutni_uporabnik")
    redirect('/izdelki')

if __name__ == "__main__":
    run(app, host='localhost', port=8080, debug=True)
