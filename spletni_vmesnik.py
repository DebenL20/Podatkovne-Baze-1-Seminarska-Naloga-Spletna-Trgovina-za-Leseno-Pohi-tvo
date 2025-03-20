from bottle import Bottle, run, template, static_file, request, redirect
from model import Izdelek, Dobavitelj
import os

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
    izdelki = Izdelek.vsi_izdelki()
    return template("""
        <!DOCTYPE html>
        <html lang="sl">
        <head>
            <meta charset="UTF-8">
            <title>Izdelki</title>
        </head>
        <body>
            <h1>Seznam izdelkov</h1>
            <a href="/kosarica" style="position: absolute; top: 10px; right: 10px;"><button>Košarica</button></a>
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
    """, izdelki=izdelki)


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

if __name__ == "__main__":
    run(app, host='localhost', port=8080, debug=True)
