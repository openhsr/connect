# Installation

Wir stellen für diverse Distributionen vorgefertigte Pakete zur Verfügung.
Du solltest wann immer möglich diese Pakete verwenden, denn damit bekommst du auch bequem Updates. Eine manuelle Installation bedeutet auch manuelle Updates.

Solltest du ein exotisches Betriebssystem verwenden oder einfach aus Spass den open\HSR-connect von Hand installieren, dann kannst du wie folgt vorgenen.

## Drucker
Damit CUPS das E-Mail-Backend nutzen kann muss dieses verlinkt werden.

```bash
ln -s $INSTALLATIONSPFAD/scripts/hsr-email-print /usr/lib/cups/backend/hsr-email-print
```

Zudem müssen die Berechtigungen angepasst werden:

```bash
chmod 700 /usr/lib/cups/backend/hsr-email-print
chown root:root /usr/lib/cups/backend/hsr-email-print
```

Nun muss auch ein Drucker eingerichtet werden.
```bash
# Add the printer if not yet installed
lpstat -a openhsr-connect 2&> /dev/null
if [ $? -ne 0 ]; then
    echo "Adding printer openhsr-connect"
    lpadmin -p openhsr-connect -E -v openhsr-connect:/tmp -P $INSTALLATIONSPFAD/scripts/Generic-PostScript_Printer-Postscript.ppd
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
