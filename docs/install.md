# Installation

Wir stellen für diverse Distributionen vorgefertigte Pakete zur Verfügung.
Du solltest wann immer möglich diese Pakete verwenden, denn damit bekommst du auch bequem Updates. Eine manuelle Installation bedeutet auch manuelle Updates.

Solltest du ein exotisches Betriebssystem verwenden oder einfach aus Spass den open\HSR-connect von Hand installieren, dann kannst du wie folgt vorgenen.

Führe folgende Befehle als root aus!

## Für Linux-Distributionen:

### Drucker
Damit CUPS das E-Mail-Backend nutzen kann muss dieses verlinkt werden.

```bash
ln -s $INSTALLATIONSPFAD/openhsr_connect/resources/openhsr-connect /usr/lib/cups/backend/openhsr-connect
```

Zudem müssen die Berechtigungen angepasst werdenn:

```bash
chmod 700 /usr/lib/cups/backend/openhsr-connect
chown root:root /usr/lib/cups/backend/openhsr-connect
```

Nun muss auch ein Drucker eingerichtet werden.
```bash
# Add the printer if not yet installed
lpstat -a openhsr-connect 2&> /dev/null
if [ $? -ne 0 ]; then
    echo "Adding printer openhsr-connect"
    lpadmin -p openhsr-connect -E -v openhsr-connect:/tmp -P $INSTALLATIONSPFAD/openhsr_connect/resources/Generic-PostScript_Printer-Postscript.ppd
fi
```


Dieser kann bei einer deinstallation wie folgt entfernt werden:
```bash
lpstat -a openhsr-connect 2&> /dev/null
if [ $? -eq 0 ]; then
    echo "Removing printer openhsr-connect"
    lpadmin -x openhsr-connect
fi
```
## Für Mac OS X:
### Drucker
Damit CUPS das E-Mail-Backend nutzen kann muss dieses verlinkt werden.
```bash
ln -s $INSTALLATIONSPFAD/openhsr_connect/resources/openhsr-connect /usr/libexec/cups/backend/openhsr-connect
```

Zudem müssen die Berechtigungen angepasst werdenn:

```bash
chmod 700 /usr/libexec/cups/backend/openhsr-connect
chown root:wheel /usr/libexec/cups/backend/openhsr-connect
```

Nun muss auch ein Drucker eingerichtet werden.
```bash
# Add the printer if not yet installed
lpstat -a openhsr-connect 2&> /dev/null
if [ $? -ne 0 ]; then
    echo "Adding printer openhsr-connect"
    lpadmin -p openhsr-connect -E -v openhsr-connect:/tmp -P $INSTALLATIONSPFAD/openhsr_connect/resources/Generic-PostScript_Printer-Postscript.ppd
fi
```


Dieser kann bei einer deinstallation wie folgt entfernt werden:
```bash
lpstat -a openhsr-connect 2&> /dev/null
if [ $? -eq 0 ]; then
    echo "Removing printer openhsr-connect"
    lpadmin -x openhsr-connect
fi
```
