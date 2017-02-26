 
Konfiguration
=============

Du kannst die Konfiguration direkt aus dem *connect* aufrufen, wenn du *connect* mit dem Kommando `edit` ausführst.

.. code-block:: shell

    PROGRAM_NAME edit

Die nachfolgenden Erklärungen basieren auf der folgenden Beispielskonfiguration:

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

Unter login kannst du der HSR-Benutzername und die Mail angegeben. Wichtig: Verwende die lange, ausgeschriebene Mail-Adresse, da Mobile-Print nur diese kennt.

..  _exclude:

exclude
-------

Unter *global-exclude* kannst du file-namen eintragen, die nie übertragen werden sollen, aus keinem Verzeichnis. Die
oben eingetragenen Einstellungen können in den meisten Fällen übernommen werden. Denn sie verhindern, dass
Windows und Mac OS X spezifische Betriebssystem-Einstellungen mit synchronisiert werden.
Ausserdem können excludes für jedes Fach einzeln angegeben werden.

exclude in den einzelnen Repositories werden zusätzlich zu den global-excludes angefügt. Dies funktioniert momentan so:

 * Beginnt die Ausnahme mit einem `/` (z.B. `/Archiv`), wird der angegebne Pfad ausgehend vom root des Repositories
    ausgenommen, im Beispiel also alles unter `InfSi1/Archiv/`, nicht aber `InfSi1/Vorlesungen/Archiv`

 * Beginnt der Pfad nicht mit einem `/`, kann er irgendwo im Repository vorkommen, um ausgenommen zu werden.
    Mit `Filme` wird also auch alles unter `InfSi1/Vorlesungen/bla/Filme` ausgelassen

 * Alternativ können bestimmte Dateinamen ausgenommen werden. Hier sind Wildcards (*) erlaubt,
    also z.B `*.tmp, file-*.*` etc.

Wichtig: Momentan können Pfadangaben nicht mit Wildcards kombiniert werden, `/Archiv/*.txt` ist also nicht möglich

Konflikt Bewältigung
--------------------

Die Option *local-changes* beschreibt, was die Software machen soll mit lokal editierten Files. Diese Einstellungen können
durch die Kommando-Parameter :ref:`local-changes <local-changes>` und :ref:`remote_deleted <remote_deleted>`
überschrieben werden.

Wenn du ein file editierst und dann diese wieder speicherst, dann sind die lokale, synchronisierte Kopie und das
HSR Original verschieden. Wenn du den HSR *connect* wieder ausführst möchtest du vielleicht nicht, dass deine
eigenen Änderungen überschrieben werden mit dem Original.

==========      ========================================================================================================
Option          Beschreibung
==========      ========================================================================================================
ask             (Vorgabe) Fragt bei jeder synchronisierung, für jedes veränderte File nach
keep            Behaltet die lokale Kopie und stoppt die Synchronisierung vom File
overwrite       Überschreibt alle Änderungen ohne nachzufragen mit dem Original vom HSR server
makeCopy        Benennt die alte, lokale Kopie um auf Filename-Datum.ext und behält beide
==========      ========================================================================================================

Die Option *remote-deleted* beschreibt, was *connect* machen soll wenn das File auf dem Server nicht mehr vorhanden ist.
Wenn der Professor ein file, das du vorhin auf den Laptop synchronisiert hast, auf dem Server löscht, gibt dir die
Option verschiedene Möglichkeiten wie *connect* dann reagieren soll.

============    ============================================================================
Option          Beschreibung
============    ============================================================================
ask             (Vorgabe) Fragt bei jeder synchronisierung, für jedes veränderte File nach
keep            Behaltet die lokale Kopie auch weiterhin
delete          Löscht das lokale File ohne nachzufragen
============    ============================================================================

.. _repositories:

repositories
------------

Ein repository beschreibt ein Fach, das synchronisiert werden soll. Der *connect* besitzt selbst keine Beschränkung
für File-Typen, Grössen oder Pfade. Die Fächer können auf dem ganzen lokalen File-System verstreut werden solange
connect Rechte besitzt ins Verzeichnis zu schreiben. Ausserdem können auch nicht Fach-Kürzel-Ordner als Repositories
angegeben werden, auch wenn nachfolgend nur noch von diesen die Rede ist.

Als **zwingende** Optionen muss sowohl eine Fach-Abkürzung als auch die Option `remote-dir` angegeben werden.

.. code-block:: yaml

    Fach-Abk:
        local-dir:  Absoluter-Lokaler-Fach-Pfad
        remote-dir: Absoluter-Server-Fach-Pfad
        exclude:
            -   File-to-exclude
            -   second-to-exclude

Als Titel wird die Abkürzung des Fachs angegeben, dieser sollte sich 4 Leerschläge vom Dokumentenrand befinden und mit
einem Doppelpunkt (:) aufhören. Der Doppelpunkt gehört nicht mehr zur Fach-Bezeichnung.

Die **local-dir**-Option überschreibt die globale Option `default-local-dir` für das jeweilige Fach. So können auch
individuelle Speicherorte angegeben werden. Diese Option kann mit `<name>`-Anweisungen **nicht** umgehen.

Die **remote-dir**-Option beinhaltet den Pfad zum Verzeichnis auf dem *HSR Server* dessen Inhalt synchronisiert werden
soll.

Unterhalb der **exclude**-Option können Files angegeben werden die nicht synchronisiert werden. Für weitere Informationen
siehe :ref:`exclude`.

Die Option **default-local-dir** setzt den Pfad, der benutzt wird, wenn dieser nicht von der *Repository*-Konfiguration
mithilfe von `local-dir` überschrieben wird. An der Stelle, an der der *Repository*-Name eingefügt werden soll,
kannst du die Markierung `<name>` benutzen.