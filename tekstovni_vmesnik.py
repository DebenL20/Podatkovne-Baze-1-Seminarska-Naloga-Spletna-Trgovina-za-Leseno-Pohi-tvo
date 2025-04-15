from model import Izdelek, Dobavitelj

kosarica = []


def prikazi_izdelke():
    izdelki = Izdelek.vsi_izdelki()
    print("\n--- SEZNAM IZDELKOV ---")
    for i, izdelek in enumerate(izdelki, start=1):
        print(f"{i}) {izdelek.ime} - {izdelek.cena:.2f} €")
    return izdelki


def prikazi_dobavitelja(izdelek):
    dobavitelj = Dobavitelj.najdi_po_id(izdelek.dobavitelj_id)
    print("\n--- PODATKI O DOBAVITELJU ---")
    print(f"Izdelek: {izdelek.ime} ({izdelek.cena:.2f} €)")
    if dobavitelj:
        print(f"Dobavitelj: {dobavitelj.ime}")
        print(f"Naslov: {dobavitelj.naslov}")
        print(f"Telefon: {dobavitelj.telefonska_stevilka}")
    else:
        print("Dobavitelj ni najden.")

    izbira = input("\nŽelite ta izdelek dodati v košarico? (d/n): ").lower()
    if izbira == 'd':
        kosarica.append(izdelek)
        print(f"Izdelek '{izdelek.ime}' dodan v košarico.")
    else:
        print("Izdelek ni bil dodan.")


def prikazi_kosarico():
    print("\n--- VAŠA KOŠARICA ---")
    if not kosarica:
        print("Košarica je prazna.")
    else:
        skupna = sum(izdelek.cena for izdelek in kosarica)
        for izdelek in kosarica:
            print(f"- {izdelek.ime} ({izdelek.cena:.2f} €)")
        print(f"Skupna cena: {skupna:.2f} €")


def glavni_meni():
    while True:
        print("\n--- GLAVNI MENI ---")
        print("1) Prikaži izdelke")
        print("2) Prikaži košarico")
        print("3) Izhod")
        izbira = input("Izbira: ")

        if izbira == "1":
            izdelki = prikazi_izdelke()
            try:
                index = int(input("\nVnesi številko izdelka za podrobnosti: "))
                if 1 <= index <= len(izdelki):
                    prikazi_dobavitelja(izdelki[index - 1])
                else:
                    print("Neveljavna izbira.")
            except ValueError:
                print("Vnesi številko.")
        elif izbira == "2":
            prikazi_kosarico()
        elif izbira == "3":
            print("Nasvidenje!")
            break
        else:
            print("Neveljavna izbira.")


if __name__ == "__main__":
    glavni_meni()
