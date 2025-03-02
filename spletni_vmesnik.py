from bottle import Bottle, run, template
from model import Izdelek

app = Bottle()

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
            <ul>
                % for izdelek in izdelki:
                    <li>{{izdelek.ime}} - {{izdelek.cena}}€ (Zaloga: {{izdelek.zaloga}})</li>
                % end
            </ul>
            <a href="/"><button>Na začetno stran</button></a>
        </body>
        </html>
    """, izdelki=izdelki)

if __name__ == "__main__":
    run(app, host='localhost', port=8080, debug=True)
