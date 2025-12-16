# XFakturist

Minimalistische Anwendung zum autonomen Erstellen von elektronischen Rechnungen (XRechnung)

## Überblick

Software für das Erstellen **XML-basierter elektronischer Rechnungen**, die [**eigenständig lauffähig**](https://de.wikipedia.org/wiki/Standalone) und gleichzeitig [**quelloffen**](https://opensource.org/osd) ist, bleibt eine Rarität. Genau solch eine Lösung wird mit **XFakturist** angeboten. **XFakturist** konzentriert sich dabei auf einfache Rechnungen mit einer geringen Anzahl von Rechnungspositionen. Obwohl **XFakturist** ein minimalistisches Werkzeug zum Ausstellen elektronischer Rechnungen ist, unterstützt es die Einbettung von **Rechnungsanhängen**, wie PDF-Dokumenten, in die XML-Datei. Als **Kommandozeilenanwendung** mit knapp gehaltener Dokumentation richtet sich **XFakturist** in erster Linie an technisch versierte Anwender.

## Wesentliche Merkmale

**XFakturist** ist [freie Software](https://opensource.org/osd) und dient der Erstellung von [elektronischen Rechnungen](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/What+is+eInvoicing), die dem Standard [XRechnung](https://xeinkauf.de/xrechnung/) entsprechen sollen. XRechnung ist ein deutsches, [XML](https://de.wikipedia.org/wiki/XML)-basiertes Datenformat mit einem zugehörigen semantischen Modell (vgl. [XRechnung-FAQ](https://e-rechnung-bund.de/faq/#xrechnung)). Die Software **XFakturist** ist eigenständig und wird ausschließlich lokal auf dem jeweiligen Rechner ausgeführt. Sie setzt weder eine Netzwerkverbindung voraus noch greift sie auf eine [API](https://de.wikipedia.org/wiki/Programmierschnittstelle) oder einen vergleichbaren Internet-Dienst zurück. Da **Rechnungsdaten nicht an Dritte** übermittelt werden, trägt **XFakturist** zum Schutz der **Vertraulichkeit dieser Daten** bei.

Derzeit ist **XFakturist** ein einfaches, jedoch funktionsfähiges Werkzeug, das überwiegend in Python implementiert ist und über die **Kommandozeile** bedient wird. Eine grafische Benutzeroberfläche ist nicht Bestandteil der Anwendung. Die Software stellt mehrere Befehle zur Verfügung, die beispielsweise im [Terminal von macOS](https://support.apple.com/de-de/guide/terminal/trmld4c92d55/mac) ausgeführt werden können.

**XFakturist** wird **ohne jegliche Gewährleistung** bereitgestellt; die Nutzung erfolgt **ausdrücklich auf eigenes Risiko**. Insbesondere obliegt es vollständig dem Anwender, die in den erzeugten XML-Dateien enthaltenen Rechnungsdaten, Geldbeträge und andere Angaben auf Richtigkeit zu prüfen. Die Nutzung von **XFakturist** zur Erzeugung einer XML-Datei garantiert **nicht deren Konformität mit dem Standard [XRechnung](https://xeinkauf.de/xrechnung/)**. Diese Konformität hängt maßgeblich auch von den bereitgestellten Eingabedaten ab.

Zur **Visualisierung der Rechnungsdaten** und zur **Prüfung der Konformität** kann externe Drittsoftware herangezogen werden, etwa die **eigenständige und quelloffene [Validierungs- und Visualisierungssoftware](https://github.com/itplr-kosit)**, die von der [Koordinierungsstelle für IT-Standards (KoSIT)](https://www.xoev.de/) der deutschen öffentlichen Verwaltung bereitgestellt wird. **XFakturist** bietet hierfür ein vereinfachtes Installationsverfahren sowie eine grundlegende Kommandozeilenschnittstelle zur Nutzung der KoSIT-Software.

## Hintergrund

Bis einschließlich 2024 war es für Freiberufler und kleine Unternehmen üblich, elektronische Rechnungen in Form von für Menschen lesbaren **PDF-Dokumenten** zu übermitteln. Soweit diese Dokumente [fälschungssicher und ordnungsgemäß archiviert](https://ao.bundesfinanzministerium.de/ao/2023/Anhaenge/BMF-Schreiben-und-gleichlautende-Laendererlasse/Anhang-64/inhalt.html) wurden und sämtliche gesetzlichen Pflichtangaben enthielten, waren sie für Zwecke des Vorsteuerabzugs ausreichend. Solche PDF-Rechnungen ließen sich mit kostenfrei verfügbaren Werkzeugen erstellen und anschließend per E‑Mail versenden.

Zwischen 2025 und 2027 wird der **deutsche umsatzsteuerliche Rechtsrahmen** schrittweise angepasst, um die **verpflichtende Nutzung von [elektronischen Rechnungen](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/What+is+eInvoicing)** einzuführen. Nach Abschluss dieser Übergangsphase müssen inländische Rechnungen von Unternehmen an andere Unternehmen grundsätzlich mittels eines elektronischen Datenaustauschs gestellt werden, bevorzugt durch den Transfer von XML-Daten. Ausnahmen hiervon sind nur in engen Grenzen vorgesehen.

Während **herkömmliche PDF-Rechnungen** mit gängiger Standardsoftware vergleichsweise einfach erzeugt werden können, ist die Erstellung von **XML-Daten, die alle rechtlichen Anforderungen an elektronische Rechnungen** erfüllen, deutlich komplexer.

Ende 2024 stand eine Vielzahl kommerzieller Softwareprodukte zur Verfügung, mit denen XML-basierte elektronische Rechnungen generiert werden konnten. Viele dieser Lösungen erwiesen sich jedoch in Anschaffung oder Bedienung als zu aufwendig für die eher einfachen Anforderungen kleiner Unternehmen. Daneben existierten einige **kostenfreie Webanwendungen**, teilweise verbunden mit einer Registrierungspflicht. **Quelloffene und eigenständig lauffähige Anwendungen** für die elektronische Rechnungsstellung waren dagegen kaum verfügbar. Diese Ausgangslage war die wesentliche Motivation für die Neuentwicklung von **XFakturist**.

## Einfache Nutzung

Nach erfolgreicher Installation stehen drei eigenständige **XFakturist**-Befehle für die Nutzung im Terminal zur Verfügung:

-   ```
    xr-compile invoice.xlsx
    ```

    Dieser Befehl liest Rechnungsdaten aus einer XLSX-Arbeitsmappe `invoice.xlsx` ein, welche eine definierte Struktur haben muss. Eine Vorlage dafür ist als Datei [`template.xlsx`](template.xlsx) im Wurzelverzeichnis von **XFakturist** enthalten. Diese kann kopiert, umbenannt und anschließend mit eigenen Rechnungsdaten befüllt werden. Die Anwendung des Python-Skripts `xr-compile` auf eine Datei `invoice.xlsx` korrekten Formats erzeugt die XML-Datei `invoice.xml` sowie eine Protokolldatei mit dem Namen `invoice.log`.

-   ```
    xr-validate invoice.xml
    ```

    Dieser Befehl ruft die [KoSIT-Validierungssoftware](https://github.com/itplr-kosit/validator) für XML-basierte elektronische Rechnungen auf und erstellt zwei Validierungsberichte: `invoice_validation_report.xml` und `invoice_validation_report.html`.

-   ```
    xr-convert invoice.xml
    ```

    Mithilfe dieses Befehls wird die [KoSIT-Visualisierungssoftware](https://github.com/itplr-kosit/xrechnung-visualization) ausgeführt, um die Rechnungsdaten in eine für Menschen lesbare Darstellung zu überführen. Im hier dargestellten Beispiel werden die Dateien `invoice_converted_de.html` und `invoice_converted_de.pdf` erzeugt. Die Feldbezeichnungen in diesen Dokumenten sind standardmäßig in deutscher Sprache gehalten. Um Feldbezeichnungen in englischer Sprache zu erhalten, kann der Sprachcode `en` als zweiter Kommandozeilenparameter übergeben werden:

    ```
    xr-convert invoice.xml en
    ```


## Automatisierte Nutzung

**XFakturist** unterstützt alternativ zur Tabellenkalkulation auch die Bereitstellung von Rechnungsdaten in Form einer JSON-Datei, was sich insbesondere für eine automatisierte Erzeugung elektronischer Rechnungen eignen könnte.

```
xr-compile invoice.json
```

Mit diesem Befehl werden Rechnungsdaten aus der Datei `invoice.json` eingelesen und im Anschluss die Dateien `invoice.xml` und `invoice.log` erzeugt.

Eine entsprechende Vorlage für JSON-basierte Rechnungsdaten ist als Datei [`template.json`](template.json) im Wurzelverzeichnis von **XFakturist** enthalten. Die Feldbezeichnungen in [`template.json`](template.json) und [`template.xlsx`](template.xlsx) sind identisch gehalten, um Konsistenz herzustellen.

Es ist zu beachten, dass die Erstellung einer XML-Datei mittels `xr-compile` für sich genommen keine Gewähr für die Konformität mit dem Standard XRechnung bietet. Eine wesentliche Voraussetzung für die Konformität besteht darin, dass sämtliche Pflichtangaben (Muss-Felder) bereitgestellt werden. Welche Felder als verpflichtend einzustufen sind, ist in der Arbeitsmappe [`template.xlsx`](template.xlsx) für jede Datenposition gesondert ausgewiesen.

## Installation

_Derzeit werden ausschließlich Systeme auf Basis von macOS und Linux offiziell unterstützt. Unter Microsoft Windows könnte eine Ausführung möglich sein, sofern das [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install) oder die [Git Bash](https://git-scm.com/) zur Verfügung stehen. Dies wurde aber bisher nicht getestet._

### Python-Skript `xr-compile`

Für die Nutzung von **XFakturist** ist eine Python-Installation (Version 3.10 oder höher) erforderlich, etwa in Form einer aktuellen [Anaconda-Distribution](https://www.anaconda.com/download). Zu den benötigten Python-Paketen zählen insbesondere:

```
json5
openpyxl
xmltodict
```

Für die Erstellung von XML-basierten elektronischen Rechnungen mit dem Befehl `xr-compile` ist somit eine funktionsfähige Python-Installation einschließlich der oben genannten Pakete erforderlich. Der **XFakturist**-Quelltext kann entweder über eine veröffentlichte ZIP-Datei heruntergeladen oder aus dem entsprechenden GitHub-Repository geklont werden. Anschließend ist sicherzustellen, dass sich das Python-Skript `xr-compile` im Suchpfad befindet.

### Installation der KoSIT-Software

Für den Betrieb der [KoSIT-Validierungs- und Visualisierungssoftware](https://github.com/itplr-kosit) wird eine aktuelle Java-Laufzeitumgebung benötigt, beispielsweise [Eclipse Temurin JRE](https://adoptium.net/de/temurin/releases/).

**XFakturist** stellt die Shell-Skripte `xr-validate` und `xr-convert` zum Starten der KoSIT-Software bereit; diese Skripte müssen sich im Suchpfad befinden, um vom Terminalfenster aus aufgerufen werden zu können.

Die KoSIT-Software selbst ist nicht Bestandteil des **XFakturist**-Pakets und muss gesondert heruntergeladen und installiert werden. Zur Vereinfachung dieses Vorgangs stellt **XFakturist** das Shell-Skript `get-kosit-xr` bereit, das aus dem Hauptverzeichnis des Projekts heraus auszuführen ist. Dieses Skript lädt und entpackt drei unterschiedliche [KoSIT-Softwarepakete](https://github.com/itplr-kosit) sowie zwei zusätzliche Abhängigkeiten, nämlich [Saxonica Saxon Home Edition](https://github.com/Saxonica/Saxon-HE/) und [Apache Formatting Objects Processor](https://xmlgraphics.apache.org/fop/).

Vier dieser fünf Komponenten wurden von den jeweiligen Anbietern unter der [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.html) lizenziert. Das Unternehmen [Saxonica](https://www.saxonica.com/) stellte die _Saxon Home Edition_ darüber hinaus auch als [Open-Source-Software](https://saxonica.plan.io/projects/saxonmirrorhe) zur Verfügung.

Nach erfolgreicher Ausführung des Installationsskripts `get-kosit-xr` sollten die Shell-Skripte `xr-validate` und `xr-convert` ohne weitere manuelle Eingriffe einsatzbereit sein.

## XRechnung-Standard

**Dieser Abschnitt gibt lediglich unsere eigene Interpretation öffentlich zugänglicher Informationen wieder und stellt ausdrücklich weder eine Rechts- noch eine Steuerberatung dar.**

Seit dem 1. Januar 2025 enthält das deutsche Umsatzsteuergesetz ([Umsatzsteuergesetz – UStG](https://www.gesetze-im-internet.de/ustg_1980/index.html)) eine [Definition der „elektronischen Rechnung“](https://www.gesetze-im-internet.de/ustg_1980/__14.html). Demnach handelt es sich um eine Rechnung, "_die in einem strukturierten elektronischen Format ausgestellt, übermittelt und empfangen wird und eine elektronische Verarbeitung ermöglicht_." Zur Erfüllung der Anforderungen des deutschen Umsatzsteuerrechts wird in der Praxis vermutlich vorwiegend eine Umsetzung der Vorgaben der [Richtlinie 2014/55/EU](https://eur-lex.europa.eu/eli/dir/2014/55/oj) der Europäischen Union angewendet werden, welche sich auf den europäischen Standard [EN 16931](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/Obtaining+a+copy+of+the+European+standard+on+eInvoicing) beruft. Der Standard [XRechnung](https://xeinkauf.de/xrechnung/) baut auf EN 16931 auf und erweitert diesen um zusätzliche Spezifikationen für den deutschen Rechtsraum.

In einer [Verlautbarung des Bundesministeriums der Finanzen](https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Umsatzsteuer/Umsatzsteuer-Anwendungserlass/2025-10-15-einfuehrung-obligatorische-e-rechnung.html) vom 15. Oktober 2025, wie bereits zuvor im Umsatzsteuer-Anwendungserlass vom 15. Oktober 2024, wurde u. a. ausgeführt, dass XML-Daten, die dem [XRechnung](https://xeinkauf.de/xrechnung/)-Standard entsprechen, für Zwecke der Umsatzsteuer als „elektronische Rechnung“ im Sinne des Gesetzes anzusehen sind.

Vor diesem Hintergrund konzipierten wir **XFakturist** Ende 2024, um elektronische Rechnungen im Einklang mit dem [XRechnung](https://xeinkauf.de/xrechnung/)-Standard erstellen zu können.

## Lizenz

**XFakturist** wird standardmäßig unter der Open-Source-Lizenz [AGPL-3.0-only](https://opensource.org/license/agpl-v3) bereitgestellt, sofern das Programm nicht unmittelbar vom Autor, Dr. Tim Brunne (München), auf Grundlage einer gesonderten kommerziellen Lizenzvereinbarung bezogen wurde.
