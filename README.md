# Podatkovne-Baze-1-Seminarska-Naloga-Spletna-Trgovina-za-Leseno-Pohistvo
Podatkovne Baze 1 Seminarska Naloga: Spletna Trgovina za Leseno Pohištvo

Najina seminsrska naloga je spletna trgovina za leseno pohištvo. V sql bi imela pet tabel. Ena bi bila dobavitelji, 
ki bi imela elemente id, ki je glavni ključ, ime_dobavitelja, telefonska_številka in naslov. Druga tabela bi bila Izdelki. 
Glavni ključ je id_izdelka, tuji klkuč id_dobavitelja, cena, ime_izdelka, opis, zaloga. Potem bi imela tabelo stranke, 
kjer bi bil glavni ključ id_stranke, ostale vrstice pa ime, naslov, telefonska številka in email. 
Četrta tabela bi bila Naročila, ki bi imela glavni ključ id_naročila, ostale vrstice so datum, vrednost in status. 
Zadnja tabela bi bila postavke naročila, kjer bi imela zunanja ključa id izdelka in id naročila. Ostali vrstici pa količina in cena za kos.

Izdelki in dobavitelji bi bili povezani med seboj. En dobavitelj lahko uvozi več različnih izdelkov, zato bi bila relacija dobavlja 1:n.
Stranke in Naročila bi bili povezani med seboj in ena stranka lahko opravi več naročil, tako, da je relacija med njima odda 1:n.
Naročila so povezana s Psotavkami naročila v relaciji vsebuje. Eno naročilo ima lahko več postavk, tako, da bi bila povezava vsebuje 1:n.
