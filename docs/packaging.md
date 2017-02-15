# "Native" Pakete

Das Tool `openhsr-connect` wird "native" für verschidene Distributionen (und Versionen) packetiert.

Pakete werden automatisch mit [Travis](https://travis-ci.org) bei einem Release gebaut und auf [pool.openhsr.ch](https://pool.openhsr.ch) hochgeladen.

Der Bau der einzelnen Pakete ist modular aufgebaut und kann lokal mit `make` getestet/ausgeführt werden.

```bash
$ make ubuntu/xenial
```

## Struktur / Konventionen 

Da Paketierung auf den verschiedenen Distributionen ganz unterschiedlich funktionieren kann nur wenig Information geteilt werden. Darum werden die Pakete für die Distributionen/Versionen in getrennten Modulen gebaut. Grundsätzlich gibt es je Distribution und Version ein Verzeichnis (Bsp. `ubuntu/xenial`). In jedem dieser Verzeichnisse liegt ein Dockerfile 

Dieser Docker-Container darf (nur) folgende Annahmen treffen:

* Das Container-Image wird neu gebaut (ohne speizifische Umgebungsvariablen)
* Ein neuer temporärer Container wird gestartet und ausgeführt - ohne weitere Parameter. Folgende Umgebungsvariablen stehen zur Verfügung
    * DOCKER_GID: Die Gruppen-ID, welche als Datei-Gruppe in `/repo` erwarted wird.
    * DOCLKER_UID: Die User-ID, welche als Datei-Owner in `/repo` erwartet wird.
* Das Git-Repository wird (im aktuellen branch) unter `/source` als Volume eingehängt. Auf dieses kann nur lesend zugegriffen werden.
* Es wird erwartet, das nach dem Container Aufruf ein gültiges und nutzbares Paket-Repository unter `/repo` hinterlässt. (`dist/<distribution>/<version>/`)

Alles weitere ist dem Container überlassen. 

Pakete für macOS (und Windows) werden nicht über diesen Mechanismus generiert.
