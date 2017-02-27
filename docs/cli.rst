 
Konsoleparameter
================

Aktionen:

**update-password**: Setzt das Passwort neu

**daemonize**: Startet connect als Hintergrund-Prozess

**sync**: Synchronisiert die Daten vom HSR Server ins lokale Verzeichnis.

.. _local-changes:

    **--local-changes**: Parameter was mit lokalen Änderungen gemacht werden soll, diese Option überschreibt die
    Einstellung im Konfigurations-File.
        
        **ask**: Default: Frage vor jeder Überschreibung
        
        **override**: Überschreibe ohne Nachfragen
        
        **keep**: Behalte die lokale kopie
        
        **makeCopy**: Benennt die alte, lokale Kopie um auf Filename-Datum.ext

.. _remote_deleted:

    **--remote-deleted**: Was mit den lokalen Kopien gemacht werden soll wenn die Server Kopie gelöscht wurde,
    diese Option überschreibt die Einstellung im Konfigurations-File.
    
        **ask**: Frage für jedes File nach
        
        **delete**: Lösche die lokale Kopie ohne nachzufragen
        
        **keep**: Behalte die lokale Kopie

**edit**: Öffnet die Konfiguration im default Editor
    
**help**: Öffnet die Dokumentation im Browser
        
Optionale Parameter:

**-v**, **--verbose**: Genaues Ausgabe Logging aktivieren
 
**-q**, **--quiet**:   Keine Informationen auf die Ausgabe schreiben
