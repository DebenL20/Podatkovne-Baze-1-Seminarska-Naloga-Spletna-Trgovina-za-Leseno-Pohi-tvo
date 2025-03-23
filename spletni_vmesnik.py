from bottle import Bottle, run, template, static_file, request, redirect, response
from model import Izdelek, Dobavitelj, Stranka
import os
import csv

app = Bottle()

kosarice = {}  # Shramba za košarice uporabnikov v pomnilniku

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

@app.route('/izdelki')
def prikazi_izdelke():
    uporabnik = request.get_cookie("trenutni_uporabnik")
    izdelki = Izdelek.vsi_izdelki()
    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Izdelki</title>
            <style>
                .top-right {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                }
                .top-right a {
                    margin-left: 10px;
                }
            </style>
        </head>
        <body>
            <h1>Seznam izdelkov</h1>
            
            <div class="top-right">
                <a href="/kosarica"><button>Košarica</button></a>
                % if uporabnik:
                    <a href="/odjava"><button>Odjava ({{uporabnik}})</button></a>
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
    """, izdelki=izdelki, uporabnik=uporabnik)



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
            <h1>Dobavitelj</h1>
            <p>Ime: {{dobavitelj.ime}}</p>
            <p>Naslov: {{dobavitelj.naslov}}</p>
            <p>Telefon: {{dobavitelj.telefonska_stevilka}}</p>
            <form action="/dodaj_v_kosarico/{{izdelek.id}}" method="post">
                <button type="submit">Dodaj v košarico</button>
            </form>
            <a href="/izdelki"><button>Nazaj na izdelke</button></a>
        </body>
        </html>
    """, dobavitelj=dobavitelj, izdelek=izdelek)


# Funkcija za shranjevanje košarice v CSV
def shrani_kosarico(uporabnisko_ime):
    uporabniki = {}
    try:
        with open(CSV_UPORABNIKI, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for vrstica in reader:
                if len(vrstica) > 1:
                    uporabniki[vrstica[0]] = [vrstica[1]] + vrstica[2:]  # Geslo + izdelki
    except FileNotFoundError:
        pass

    if uporabnisko_ime in uporabniki:
        geslo = uporabniki[uporabnisko_ime][0]  # Ohrani geslo
    else:
        geslo = ""

    # Preprečimo gnezdenje seznamov
    izdelki = [str(izdelek.id) for izdelek in kosarice.get(uporabnisko_ime, [])]
    uporabniki[uporabnisko_ime] = [geslo] + izdelki

    with open(CSV_UPORABNIKI, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for uporabnik, podatki in uporabniki.items():
            writer.writerow([uporabnik] + podatki)


def nalozi_kosarico(uporabnisko_ime):
    kosarice[uporabnisko_ime] = []
    try:
        with open(CSV_UPORABNIKI, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for vrstica in reader:
                if len(vrstica) > 2 and vrstica[0] == uporabnisko_ime:
                    izdelek_ids = vrstica[2:]  # ID-ji izdelkov
                    izdelki = [Izdelek.najdi_po_id(int(id)) for id in izdelek_ids if id.isdigit()]
                    kosarice[uporabnisko_ime] = [izdelek for izdelek in izdelki if izdelek is not None]  # Filtriramo None vrednosti
    except FileNotFoundError:
        pass



@app.route('/dodaj_v_kosarico/<izdelek_id>', method='POST')
def dodaj_v_kosarico(izdelek_id):
    uporabnik = request.get_cookie("trenutni_uporabnik")
    if not uporabnik:
        return template("""
            <!DOCTYPE html>
            <html lang="sl">
            <head>
                <meta charset="UTF-8">
                <title>Prijava potrebna</title>
            </head>
            <body>
                <h1>Prosim prijavite se v račun, da lahko dodajate izdelke v košarico.</h1>
                <a href="/prijava"><button>Prijava</button></a>
                <a href="/izdelki"><button>Nazaj na izdelke</button></a>
            </body>
            </html>
        """)
    
    if uporabnik not in kosarice:
        kosarice[uporabnik] = []
    
    izdelek = Izdelek.najdi_po_id(izdelek_id)
    if izdelek:
        kosarice[uporabnik].append(izdelek)
        shrani_kosarico(uporabnik)
    redirect('/kosarica')


@app.route('/kosarica')
def prikazi_kosarico():
    uporabnik = request.get_cookie("trenutni_uporabnik")
    if not uporabnik:
        return template("""
            <!DOCTYPE html>
            <html lang="sl">
            <head>
                <meta charset="UTF-8">
                <title>Košarica</title>
            </head>
            <body>
                <h1>Prosim prijavite se, da lahko vidite svojo košarico.</h1>
                <a href="/prijava"><button>Prijava</button></a>
                <a href="/izdelki"><button>Nazaj na izdelke</button></a>
            </body>
            </html>
        """)
    
    izdelki = kosarice.get(uporabnik, [])
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
                % for izdelek in izdelki:
                    <li>{{ izdelek.ime }} - {{ izdelek.cena }} €</li>
                % end
            </ul>
            <a href="/izdelki"><button>Nazaj na izdelke</button></a>
        </body>
        </html>
    """, izdelki=izdelki)

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
            nalozi_kosarico(uporabnisko_ime)
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
        stranka = Stranka(None, uporabnisko_ime, geslo)
        stranka.shrani()

        # Shrani tudi v CSV
        shrani_uporabnika(uporabnisko_ime, geslo)

        return "<h1>Uspešna registracija!</h1><a href='/prijava'>Prijava</a>"

    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Registracija</title>
        </head>
        <body>
            <h1>Registracija</h1>
            <form method="POST">
                <label>Uporabniško ime:</label>
                <input type="text" name="uporabnisko_ime" required><br>
                <label>Geslo:</label>
                <input type="password" name="geslo" required><br>
                <label>Ponovi geslo:</label>
                <input type="password" name="potrdi_geslo" required><br>
                <button type="submit">Registracija</button>
            </form>
            <a href="/prijava"><button>Prijava</button></a>
        </body>
        </html>
    """)


@app.route('/odjava')
def odjava():
    uporabnik = request.get_cookie("trenutni_uporabnik")
    if uporabnik:
        shrani_kosarico(uporabnik)
    response.delete_cookie("trenutni_uporabnik")
    redirect('/izdelki')


if __name__ == "__main__":
    run(app, host='localhost', port=8080, debug=True)
