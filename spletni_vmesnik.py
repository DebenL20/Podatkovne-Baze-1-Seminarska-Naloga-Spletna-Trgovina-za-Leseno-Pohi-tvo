from bottle import Bottle, run, template, static_file, request, redirect, response
from model import Izdelek, Dobavitelj
import os
import csv

app = Bottle()

kosarica = []  # Seznam za shranjevanje izdelkov v košarici

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
                if len(vrstica) == 2:
                    uporabniki[vrstica[0]] = vrstica[1]
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

        # Preveri, ali gesli ustrezata
        if geslo != potrdi_geslo:
            return "<h1>Napaka: Gesli se ne ujemata!</h1><a href='/registracija'>Poskusi znova</a>"

        # Preveri, ali uporabnik že obstaja
        uporabniki = preberi_uporabnike()
        if uporabnisko_ime in uporabniki:
            return "<h1>Napaka: Uporabniško ime že obstaja!</h1><a href='/registracija'>Poskusi znova</a>"

        # Shrani novega uporabnika
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
    response.delete_cookie("trenutni_uporabnik")
    redirect('/izdelki')



if __name__ == "__main__":
    run(app, host='localhost', port=8080, debug=True)
