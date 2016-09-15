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
