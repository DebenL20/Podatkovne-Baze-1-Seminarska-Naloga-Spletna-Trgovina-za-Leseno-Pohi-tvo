from bottle import Bottle, run, template, static_file, request, redirect, response
from model import Izdelek, Dobavitelj, Stranka
import os
import csv

app = Bottle()


CSV_UPORABNIKI = "uporabniki.csv"

@app.route('/')
def zacetna_stran():
    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Pohištvo</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <header>
                <h1>Dobrodošli v spletni trgovini s pohištvom</h1>
                <nav>
                    <a href="/izdelki">Pregled izdelkov</a>
                </nav>
            </header>
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
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <header>
                <h1>Seznam izdelkov</h1>
                <div class="top-nav">
                    <a href="/kosarica">🛒 Košarica</a>
                    % if uporabnik:
                        <a href="/odjava">Odjava ({{uporabnik}})</a>
                    % else:
                        <a href="/prijava">Prijava</a>
                    % end
                </div>
            </header>
            <main class="product-grid">
                % for izdelek in izdelki:
                    <div class="product">
                        <a href="/dobavitelj/{{izdelek.dobavitelj_id}}/{{izdelek.id}}">
                            <img class="product-img" src="/slike_izdelkov/{{izdelek.ime.lower().replace(' ', '_')}}.png" alt="{{izdelek.ime}}">
                        </a>
                        <h2>{{ izdelek.ime }}</h2>
                        <p>{{ izdelek.cena }} €</p>
                    </div>
                % end
            </main>
            <footer>
                <a href="/">Na začetno stran</a>
            </footer>
        </body>
        </html>
    """, izdelki=izdelki, uporabnik=uporabnik)

# Strezba statične CSS datoteke
@app.route('/static/<filename>')
def serve_static(filename):
    return static_file(filename, root=os.path.join(os.getcwd(), 'static'))



@app.route('/dobavitelj/<dobavitelj_id>/<izdelek_id>')
def prikazi_dobavitelja(dobavitelj_id, izdelek_id):
    dobavitelj = Dobavitelj.najdi_po_id(dobavitelj_id)
    izdelek = Izdelek.najdi_po_id(izdelek_id)
    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Dobavitelj</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <header><h1>Dobavitelj izdelka</h1></header>
            <main class="detail-view">
                <h2>{{ izdelek.ime }}</h2>
                <p><strong>Opis:</strong> {{ izdelek.opis }}</p>
                <p><strong>Cena:</strong> {{ izdelek.cena }} €</p>
                <hr>
                <h3>Dobavitelj</h3>
                <p><strong>Ime:</strong> {{ dobavitelj.ime }}</p>
                <p><strong>Naslov:</strong> {{ dobavitelj.naslov }}</p>
                <p><strong>Telefon:</strong> {{ dobavitelj.telefonska_stevilka }}</p>
                <form action="/dodaj_v_kosarico/{{ izdelek.id }}" method="post">
                    <button type="submit">Dodaj v košarico</button>
                </form>
            </main>
            <footer>
                <a href="/izdelki">Nazaj na izdelke</a>
            </footer>
        </body>
        </html>
    """, dobavitelj=dobavitelj, izdelek=izdelek)









@app.route('/dodaj_v_kosarico/<izdelek_id>', method='POST')
def dodaj_v_kosarico(izdelek_id):
    uporabnik_ime = request.get_cookie("trenutni_uporabnik")
    if not uporabnik_ime:
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
        return template("""
            <!DOCTYPE html>
            <html lang="sl">
            <head>
                <meta charset="UTF-8">
                <title>Košarica</title>
                <link rel="stylesheet" href="/static/style.css">
            </head>
            <body>
                <h1>Prosim prijavite se, da lahko vidite svojo košarico.</h1>
                <a href="/prijava"><button>Prijava</button></a>
                <a href="/izdelki"><button>Nazaj na izdelke</button></a>
            </body>
            </html>
        """)

    stranka = Stranka.najdi_po_imenu(uporabnik_ime)
    if not stranka:
        return redirect('/prijava')

    izdelki = stranka.pridobi_kosarico()
    skupna_cena = sum(izdelek.cena for izdelek in izdelki)

    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Košarica</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <header><h1>Vaša košarica</h1></header>
            <main class="cart-view">
                % if izdelki:
                    <ul>
                        % for i, izdelek in enumerate(izdelki):
                            <li>
                                {{ izdelek.ime }} - {{ izdelek.cena }} €
                                <form action="/izbrisi/{{i}}" method="post" style="display:inline;">
                                    <button type="submit">Odstrani</button>
                                </form>
                            </li>
                        % end
                    </ul>
                    <p><strong>Skupna cena:</strong> {{ skupna_cena }} €</p>
                    <form action="/zakljucek" method="post">
                        <button type="submit">Zaključi nakup</button>
                    </form>
                % else:
                    <p>Košarica je prazna.</p>
                % end
                <a href="/izdelki"><button>Nazaj na izdelke</button></a>
            </main>
        </body>
        </html>
    """, izdelki=izdelki, skupna_cena=skupna_cena)

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
    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Prijava</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <header><h1>Prijava</h1></header>
            <main class="form-container">
                <form method="POST">
                    <label>Uporabniško ime:</label>
                    <input type="text" name="uporabnisko_ime" autocomplete="off" required>
                    <label>Geslo:</label>
                    <input type="password" name="geslo" required><br>
                    <button type="submit">Prijava</button>
                </form>
                <a href="/registracija">Registracija</a>
            </main>
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
        stranka = Stranka(None, uporabnisko_ime, geslo, [])
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
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <header><h1>Registracija</h1></header>
            <main class="form-container">
                <form method="POST">
                    <label>Uporabniško ime:</label>
                    <input type="text" name="uporabnisko_ime" autocomplete="off" required>
                    <label>Geslo:</label>
                    <input type="password" name="geslo" required><br>
                    <label>Ponovi geslo:</label>
                    <input type="password" name="potrdi_geslo" required><br>
                    <button type="submit">Registracija</button>
                </form>
                <a href="/prijava">Nazaj na prijavo</a>
            </main>
        </body>
        </html>
    """)


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

    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Zaključen nakup</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <header><h1>Hvala za vaš nakup!</h1></header>
            <main>
                <p>Vaše naročilo je bilo uspešno zaključeno.</p>
                <a href="/izdelki"><button>Nazaj v trgovino</button></a>
            </main>
        </body>
        </html>
    """)

if __name__ == "__main__":
    run(app, host='localhost', port=8080, debug=True)
