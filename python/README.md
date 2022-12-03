# Pokewiki Scraper by ~ hmmh.SCOM

# Was macht dieses Python-Skript?
    - Dieses Programm sammelt Daten von der Seite 'pokewiki.de'
    und speichert diese in einer lokalen Datenbank

# Wie führt man das ganze aus?
    - Ziemlich simpel müssen einmal alle requirements aus derselbigen Datei
    installiert werden und anschließend muss nur noch die Datei 'main.py'
    ausgeführt werden. Dann ein paar Minuten warten und die Daten werden in
    eine lokale Datenbank gespeichert.

# Wie lege ich diese Datenbank an?
    - Das ganze passiert ganz automatisch wenn die docker-compose.yml
    ausgeführt wird.
    - Das funktioniert mit dem Befehler docker compose up -d --build

# Darstellung der Daten
    - Im apache Ordner befindet sich eine Beispiel website welche
    die Daten aus der Datenbank in einem Angular Projekt darstellt

# Kurzform
    - docker compose up -d --build
    - python main.py
    - Kurz warten, fertig!