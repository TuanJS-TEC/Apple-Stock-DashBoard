**How to Run This Project**
There are two ways to run this project. The Docker method is highly recommended as it handles all dependencies automatically.

Option 1: Using Docker (Recommended)
This method automatically builds the static files and serves them using an Nginx server.

Prerequisite: You must have Docker Desktop installed and running on your system.

1.Clone the Repository:
- git clone [URL_CUA_BAN_DEN_REPOSITORY]
  cd [TEN_REPOSITORY_CUA_BAN]

2.Build the Docker Image: Open a terminal in the project's root directory (where the Dockerfile is located) and run:
- docker build -t apple-dashboard .

3. Run the Docker Container: Once the build is complete, run the container:
- docker run -p 8080:80 apple-dashboard.

4. Access the Website: Open your web browser and navigate to: http://localhost:8080

Option 2: Running Locally (For Development)
This method is for running the Python script manually to generate the files.

Prerequisites: You must have Python 3.10+ and pip installed.
1. Clone the Repository (if not already done).
2. Create and Activate a Virtual Environment:
  * macOS / Linux:
    - python3 -m venv venv
    - source venv/bin/activate
  * Windows:
    - python -m venv venv
    - .\venv\Scripts\activate
3. Install Dependencies:
- pip install -r requirements.txt
4. Run the Build Script: Execute the Python script to generate all HTML and chart files:
- python build_website.py
5.View the Website: The script does not start a server. To view the site, simply open the index.html file directly in your web browser.

**So führen Sie dieses Projekt aus**
Es gibt zwei Möglichkeiten, dieses Projekt auszuführen. Die Docker-Methode wird dringend empfohlen, da sie alle Abhängigkeiten automatisch verwaltet.

Option 1: Mit Docker (Empfohlen)
Diese Methode erstellt automatisch die statischen Dateien und stellt sie über einen Nginx-Server bereit.

Voraussetzung: Sie müssen Docker Desktop auf Ihrem System installiert haben und es muss ausgeführt werden.
1. Repository klonen:
   - git clone [IHRE_REPOSITORY_URL]
   - cd [IHR_REPOSITORY_NAME]
2. Docker-Image erstellen: Öffnen Sie ein Terminal im Stammverzeichnis des Projekts (wo sich das Dockerfile befindet) und führen Sie aus:
   - docker build -t apple-dashboard .
3. Docker-Container ausführen: Sobald der Build abgeschlossen ist, starten Sie den Container:
   -  docker run -p 8080:80 apple-dashboard
4. Website aufrufen: Öffnen Sie Ihren Webbrowser und navigieren Sie zu: http://localhost:8080.

Option 2: Lokal ausführen (Für die Entwicklung)
Diese Methode dient dazu, das Python-Skript manuell auszuführen, um die Dateien zu generieren.

Voraussetzungen: Sie müssen Python 3.10+ und pip installiert haben.

1. Repository klonen (falls noch nicht geschehen).

2. Virtuelle Umgebung erstellen und aktivieren:
   * macOS / Linux:
     - python3 -m venv venv
     - source venv/bin/activate
   * Windows:
     - python -m venv venv
     - .\venv\Scripts\activate
3. Abhängigkeiten installieren:
  - pip install -r requirements.txt
4. Build-Skript ausführen: Führen Sie das Python-Skript aus, um alle HTML- und Diagrammdateien zu generieren:
  - python build_website.py
5. Website ansehen: Das Skript startet keinen Server. Um die Website anzuzeigen, öffnen Sie einfach die Datei index.html direkt in Ihrem Webbrowser.
