# Entwicklungsumgebung aufsetzen

Bevor du loslegst, stelle sicher, dass du Python 3.5 bzw. Python 3.5 installiert hast.
Dies kannst du machen, in dem du das Kommando `python3 --version` ausführst

```bash
$ python3 --version
Python 3.5.2
```

## PEP-8
[PEP-8](https://www.python.org/dev/peps/pep-0008/) ist der "Style Guide for Python Code". Er gilt für dieses Projekt.
Wenn du einen Editor wie [Atom](https://atom.io/packages/linter-pep8), Sublime etc. brauchst, dann installiere bitte das entsprechende Plugin/Addon, welches den code auf PEP-8 prüft.

PEP-8 kann auch über die Kommandozeile geprüft werden - ist aber mühsamer in der Handhabung als direkt im Editor.

```bash
$ sudo pip3 install pep8
$ pep8 openhsr_connect/ tests/
```

## Projekt klonen

```bash
cd path/to/my/projects
git clone https://github.com/openhsr/connect.git
```

## virtualenv einrichten
Ein Virtualenv ist eine isolierte Python-Umgebung, damit wir bei der Entwicklung keine Konflikte mit global installierten Paketen haben.

Dazu müssen wir eine neue solche virtuelle Umgebung erstellen:

```bash
$ python3 -m venv venv
```

Damit ist die einmalige Einrichtung abgeschlossen. Um das virtualenv zu aktivieren, muss folgendes Kommando ausgeführt werden, bevor man damit beginnt, am Projekt zu arbeiten.

```bash
$ source venv/bin/activate
```

Die Prompt beinhaltet den Text `(venv)` - dadurch wissen wir, dass ein virtualenv aktiv ist.

Wenn du mit deiner Arbeit fertig bist, dann kannst du das virtualenv mit dem Kommando `deactivate`
deaktivieren

```bash
$ deactivate
```

## Abhängigkeiten installieren
Die Abhängigkeiten des Projekts sind in der Datei `requirements.txt` aufgelistet. Abhängigkeiten, welche zur Entwicklung benötigt werden (wie bsp. Testframeworks) sind in der Datei `requirements-dev.txt` gelistet.

Die Installation mittels pep erfolgt wie folgt:

```bash
$ pip3 install -r requirements.txt
$ pip3 install -r requirements-dev.txt
```

Um sowohl die Tests auszuführen, als auch die Kommandozeile testen zu können, muss das `openhsr-connect` Paket installiert werden:
o   
```bash
$ pip install --editable .
```

## Tests ausführen
Als Testsuite brachen wir [pytest](http://doc.pytest.org/en/latest/). Alle Tests im Verzeichnis `tests/` laufen zu lassen geht mit dem folgenden Kommando:

```bash
pytest
```

und um die Testabdeckung zu sehen, kann der Parameter `--cov` angehängt werden:

```bash
pytest --cov
```
