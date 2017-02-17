 
Konfiguration
=============

Beispiel Konfiguration:

.. code-block:: yaml

    login:
        username: rzimmerm
        email: raphael.zimmermann@hsr.ch
    sync:
        global-exclude:
            - .DS_Store
            - Thumbs.db

    conflict-handling:
        local-changes: ask # ask | keep | overwrite | makeCopy
        remote-deleted: ask # ask | delete | keep

    default-local-dir: /home/rzi/HSR/module/<name>/skript/

    repositories:
        WED2:
            remote-dir: Informatik/Fachbereich/Web_Engineering_+_Design_2/WED2
        MGE:
            remote-dir: Informatik/Fachbereich/Mobile_and_GUI_Engineering/MGE
        AD2:
            remote-dir: Informatik/Fachbereich/Algorithmen_und_Datenstrukturen_2/AD2
        BuPl:
            remote-dir: Kommunikation_Wirtschaft_Recht/Business_und_Recht_1/BuPl/Aberer/
        ReIng:
            remote-dir: Kommunikation_Wirtschaft_Recht/Business_und_Recht_1/ReIng/
        CPl:
            remote-dir: Informatik/Fachbereich/C++/CPl
        MsTe:
            remote-dir: Informatik/Fachbereich/DotNet_Technologien/MsTe
        exclude:
            - '/(Archiv)'

Login-Daten
-----------

Unter login werden der HSR-Benutzername und die Mail angegeben. Wichtig: Die lange, ausgeschriebene Mail-Adresse verwenden, da Mobile-Print nur diese kennt.

Sync
----

Unter *global-exclude* kannst du file-namen eintragen, die nie übertragen werden sollen, aus keinem Verzeichnis.

Conflict-handling
-----------------

Die Option *local-changes* beschreibt, was die Software machen soll mit lokal editierten Files. Wenn du ein file editierst und dann diese wieder speicherst, dann sind die lokale, synchronisierte Kopie und das HSR Original verschieden. Wenn du den HSR Connect wieder ausführst möchtest du vielleicht nicht, dass deine lokalen Änderungen überschrieben werden mit dem Original.

==========      ========================================================================================================
Option          Beschreibung
==========      ========================================================================================================
ask             (default) Fragt bei jeder synchronisierung, für jedes veränderte File nach
keep            Behaltet die lokale Kopie und stoppt die Synchronisierung vom File
overwrite       Überschreibt alle Änderungen ohne nachfragen mit dem Original vom HSR server
makeCopy        Benennt die alte, lokale Kopie um auf Filename-Datum.ext
==========      ========================================================================================================

Die Option *remote-deleted* beschreibt, was connect machen soll wenn das File auf dem Server nicht mehr vorhanden ist. Wenn der Professor ein file, das du vorhin auf den Laptop synchronisiert hast, auf dem Server löscht, gibt dir die Option verschiedene Möglichkeiten wie connect dann reagieren soll.

============    ============================================================================
    Option      Beschreibung
============    ============================================================================
    ask         (default) Fragt bei jeder synchronisierung, für jedes veränderte File nach
    keep        Behaltet die lokale Kopie auch weiterhin
    delete      Löscht das lokale File ohne nachzufragen
============    ============================================================================
    
default-local-dir
-----------------


repositories
------------
