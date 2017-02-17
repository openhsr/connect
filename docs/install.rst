
Installation
============

Debian/Ubuntu Linux
-------------------

 1. Die Repository (Ablage für Programme) dem Linux bekannt machen.

    sudo add-apt-repository DEBIAN-REPOSITORY

 2. Das Program vom Repository herunterladen und installieren.
 
    sudo apt install DEBIAN-PACKAGE
    
 3. Das Program mit der Konsole aufzurufen.

    PROG-NAME
    

Manuelle Installation
---------------------

Wir stellen für diverse Distributionen vorgefertigte Pakete zur Verfügung. Du solltest wann immer möglich diese Pakete verwenden, denn damit bekommst du auch bequem Updates. Eine manuelle Installation bedeutet auch manuelle Updates.

Solltest du ein exotisches Betriebssystem verwenden oder einfach aus Spass den open\HSR-connect von Hand installieren, dann kannst du die folgende Anleitung für Debian als Hilfestellung verwenden.

 1. Installiere PIP auf dem System
 
    sudo apt install python3-pip python3-setuptools
    
 2. Lade die Sources herunter von unserem Git
 
    git clone https://github.com/openhsr/connect.git
    
 3. Führe setup.py aus
 
    python3 setup.py install
    
 4. Führe das installierte Program aus
    
    openhsr-connect ...
    
 5. Für die deinstallation die Schritte 1-2 ausführen.
 
 6. setup.py aufrufen und das Program neu installieren und die Filenamen in *programfiles.txt* schreiben lassen
 
    python3 setup.py install --record programfiles.txt
    
 7. Das file einlesen mit cat und xargs rm -rf verwenden um alle Verzeichnisse zu löschen

    cat programfiles.txt | xargs rm -rf
