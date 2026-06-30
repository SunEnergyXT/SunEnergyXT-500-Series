# SunEnergyXT 500 Series

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

## Sprache / Language

- [Deutsch](README.md) (Standard)
- [English](README.en.md)

## Einfuehrung

SunEnergyXT 500 Series ist eine benutzerdefinierte Integration fuer Home Assistant. Sie ermoeglicht das Auffinden, Ueberwachen und Steuern von AIO-Geraeten der SunEnergyXT 500-Serie im lokalen Netzwerk.

Die vollstaendige Referenz der lokalen API, Beispiele fuer `MD`-Zaehlerverbindungsstrings und Beispiele fuer `TZ`-Zeitzonenwerte finden Sie in [API.md](API.md).

## Funktionen

- Automatische Geraeteerkennung ueber Zeroconf oder manuelles Hinzufuegen per IP-Adresse
- Ueberwachung von PV-Eingang, Netzanschlussleistung, Lastanschlussleistung, Batteriestand, Firmware-Versionen und weiteren Echtzeitdaten
- Anpassung haeufig genutzter Einstellungen wie `GS`, `IS`, `MG`, `SI`, `SA`, `SO` und `PT`
- Konfiguration von lokalem Modus, `MM` Lokaler Eigenverbrauch, `MD` lokale Smart-Meter-Verbindung, `LFB` Lastprioritaet, `LPS` Inselausgang und dem Zeitzonenfeld `TZ`
- Neustart des Geraets direkt aus Home Assistant

## Installation

### Installation ueber HACS (empfohlen)

1. Oeffnen Sie HACS in Home Assistant
2. Klicken Sie oben rechts auf die drei Punkte und waehlen Sie "Custom repositories"
3. Geben Sie die Repository-Adresse ein: https://github.com/SunEnergyXT/SunEnergyXT-500-Series
4. Waehlen Sie als Kategorie "Integration"
5. Klicken Sie auf "Add"
6. Suchen Sie nach "SunEnergyXT 500 Series"
7. Klicken Sie auf "Download"
8. Starten Sie Home Assistant neu

### Manuelle Installation

1. Laden Sie das aktuelle [Release-Paket](https://github.com/SunEnergyXT/SunEnergyXT-500-Series/releases) herunter
2. Entpacken Sie es in `config/custom_components/`
3. Stellen Sie sicher, dass das Zielverzeichnis `config/custom_components/sunenergyxt/` ist
4. Starten Sie Home Assistant neu

#### Beispiel fuer die endgueltige Verzeichnisstruktur

```text
custom_components
    ├── sunenergyxt
        ├── __init__.py
        ├── button.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── manifest.json
        ├── number.py
        ├── sensor.py
        ├── switch.py
        ├── text.py
        └── translations
            ├── de.json
            ├── en.json
```

## Konfiguration

1. Gehen Sie in Home Assistant zu "Einstellungen" > "Geraete und Dienste"
2. Klicken Sie auf "Integration hinzufuegen"
3. Suchen Sie nach `SunEnergyXT 500 Series`
4. Folgen Sie dem Einrichtungsdialog
   - Wenn das Geraet automatisch gefunden wird, bestaetigen Sie einfach den Fund
   - Wenn das Geraet nicht automatisch gefunden wird, geben Sie die IP-Adresse manuell ein
5. Die Integration liest SN und Modell automatisch aus. Eine manuelle Eingabe der SN ist nicht noetig

Hinweise zur Nutzung:

- Home Assistant und das Geraet muessen sich im selben lokalen Netzwerk befinden
- Wenn Sie die automatische Erkennung nutzen moechten, muss das Netzwerk mDNS / Zeroconf zulassen
- Nach dem Aendern eines Steuerwerts sollte der finale Zustand durch die naechste Aktualisierung oder ein erneutes Auslesen bestaetigt werden

## Auswahl des Nulleinspeisungsmodus

Verwenden Sie immer nur einen Regelpfad fuer Nulleinspeisung gleichzeitig. Wenn geraeteinterner lokaler Modus, Home-Assistant-Blueprint und App-/Cloud-Steuerung gleichzeitig gemischt werden, ist das resultierende Verhalten schwer vorhersehbar.

| Modus | Wo die Regelung laeuft | Zaehlerquelle | Wann verwenden |
|-------|------------------------|---------------|----------------|
| Geraeteinterner lokaler Eigenverbrauch (`MM` + `MD`) | In der Firmware des SunEnergyXT-Geraets | Direkt im Geraet ueber `MD` konfigurierter Zaehler | Verwenden, wenn der Zaehler zu den dokumentierten geraeteinternen Zaehlerarten gehoert und das Geraet den Zaehler direkt auslesen soll |
| Home-Assistant-Nulleinspeisungs-Blueprint | In der Home-Assistant-Automatisierung | Home-Assistant-Zaehlerentitaeten | Verwenden, wenn der Zaehler bereits in Home Assistant verfuegbar ist oder wenn eigene Zaehlerformeln, eigene Logik oder eine besser nachvollziehbare Regelung benoetigt werden |
| App-/Cloud-Nulleinspeisung | SunEnergyXT App-/Cloud-Pfad | In App/Cloud konfigurierter Zaehlerpfad | Nur verwenden, wenn bewusst der App-/Cloud-Regelpfad genutzt werden soll |

Der geraeteinterne lokale Eigenverbrauch unterstuetzt aktuell nur die in [API.md](API.md) dokumentierten Zaehlerkategorien, z. B. Shelly 3EM, Shelly Pro 3EM, EcoTracker und Tasmota / BitShake. Andere Zaehler werden vom geraeteinternen Modus nicht automatisch unterstuetzt, ausser sie werden dem Geraet in einem dieser dokumentierten Formate bereitgestellt.

Die offizielle Home-Assistant-Blueprint wird separat gepflegt: [SunEnergyXT Nulleinspeisungs-Blueprint](https://github.com/SunEnergyXT/sunenergyxt-500-zero-feed-in-blueprint). Wenn diese Blueprint verwendet wird, sollte `MM` deaktiviert bleiben, weil die Blueprint das Geraet ueber Home-Assistant-Entitaeten steuert und nicht den direkten lokalen Zaehlerlesepfad des Geraets nutzt.

Um den geraeteinternen lokalen Pfad aus Home Assistant zu verwenden, oeffnen Sie das SunEnergyXT-Geraet in Home Assistant und bearbeiten Sie die Textentitaet `Lokale Smart-Meter-Verbindung` (`MD`) mit dem finalen Zaehler-JSON aus [API.md](API.md). Aktivieren Sie danach `Lokaler Eigenverbrauch` (`MM`). Die `MD`-Entitaet ist ein Schreibfeld fuer die geraeteinterne lokale Zaehlerverbindung, aber kein garantiertes Ruecklesefeld. Bestaetigen Sie das Ergebnis ueber `Zaehlerstatus` (`MS`) und das reale Zaehlerverhalten.

## Entitaetsbeschreibung

Hinweise:

- Die tatsaechlich sichtbaren Entitaeten koennen je nach Modell, Firmware-Version und Anzahl der Erweiterungsspeicher leicht variieren
- Energiezaehler werden vom Geraet in der Regel als rohe `Wh` geliefert; die Integration zeigt sie als `kWh` an
- `TZ` muss als POSIX-Zeitzonenstring angegeben werden, nicht als Land, Stadt oder Kurzform wie `CEST`

### Sensor

| Entitaets-ID | Name | Einheit | Beschreibung |
|--------------|------|---------|--------------|
| `WS` | WLAN-SSID | - | Diagnoseinformationen zur WLAN-Verbindung |
| `WR` | WLAN-Signalstaerke | dB | Aktuelle WLAN-Signalstaerke |
| `ST` | Systemstatus | - | Betriebsstatus des Geraets. Hauefige Werte: `0 = Abgeschaltet`, `1 = Standby`, `2 = In Betrieb`, `3 = Upgrade` |
| `IW` | Gesamteingangsleistung des Systems | W | Aktuelle gesamte Eingangsleistung des Systems |
| `OP` | Gesamtausgangsleistung des Systems | W | Aktuelle gesamte Ausgangsleistung des Systems |
| `PV` | PV-Gesamteingangsleistung | W | Gesamte PV-Eingangsleistung aller MPPT-Kanaele |
| `PV1` | PV 1 Eingangsleistung | W | PV-Eingangsleistung von MPPT-Kanal 1 |
| `PV2` | PV 2 Eingangsleistung | W | PV-Eingangsleistung von MPPT-Kanal 2 |
| `PV3` | PV 3 Eingangsleistung | W | PV-Eingangsleistung von MPPT-Kanal 3 |
| `PV4` | PV 4 Eingangsleistung | W | PV-Eingangsleistung von MPPT-Kanal 4 |
| `II1` | PV 1 Eingangsstrom | A | Eingangsstrom von MPPT-Kanal 1 |
| `II2` | PV 2 Eingangsstrom | A | Eingangsstrom von MPPT-Kanal 2 |
| `II3` | PV 3 Eingangsstrom | A | Eingangsstrom von MPPT-Kanal 3 |
| `II4` | PV 4 Eingangsstrom | A | Eingangsstrom von MPPT-Kanal 4 |
| `VP1` | PV 1 Eingangsspannung | V | Eingangsspannung von MPPT-Kanal 1 |
| `VP2` | PV 2 Eingangsspannung | V | Eingangsspannung von MPPT-Kanal 2 |
| `VP3` | PV 3 Eingangsspannung | V | Eingangsspannung von MPPT-Kanal 3 |
| `VP4` | PV 4 Eingangsspannung | V | Eingangsspannung von MPPT-Kanal 4 |
| `GP` | Systemleistung am Netzanschluss | W | Leistung am Netzanschluss. Positive Werte bedeuten in der Regel Einspeisung, negative Werte in der Regel Netzbezug oder Netzladen |
| `LP` | Systemleistung am Lastanschluss | W | Aktuelle Leistung am Lastanschluss |
| `BP` | System-Batterieleistung | W | Aktuelle Batterieleistung. Positive Werte bedeuten Laden, negative Werte bedeuten Entladen |
| `GD1` | Heutige Netzladung | kWh | Energie, die heute aus dem Netz in das System geladen wurde |
| `GD2` | Heutige Netzeinspeisung | kWh | Energie, die heute ueber den Netzanschluss ins Netz eingespeist wurde |
| `LD` | Heutige Off-Grid-Ausgabe | kWh | Heute abgegebene Off-Grid-Ausgangsenergie |
| `SC` | System-Speicherlevel | % | Gesamter SOC des Systems |
| `SC0` | Kopfspeicher | % | SOC des Kopfspeichers |
| `SC1` | Erweiterungsspeicher 1 | % | SOC des Erweiterungsspeichers 1 |
| `SC2` | Erweiterungsspeicher 2 | % | SOC des Erweiterungsspeichers 2 |
| `SC3` | Erweiterungsspeicher 3 | % | SOC des Erweiterungsspeichers 3 |
| `SC4` | Erweiterungsspeicher 4 | % | SOC des Erweiterungsspeichers 4 |
| `SC5` | Erweiterungsspeicher 5 | % | SOC des Erweiterungsspeichers 5 |
| `ON` | Anzahl der Online-Batteriepacks | - | Anzahl der aktuell online gemeldeten Batteriepacks |
| `ES` | Firmware-Version (Wi-Fi) | - | System-Wi-Fi- bzw. EMS-Firmware-Version |
| `AS` | Firmware-Version (AC-Einheit) | - | Firmware-Version der AC-Einheit |
| `DS` | Firmware-Version (DC-Einheit) | - | Firmware-Version der DC-Einheit |
| `BS0` | Firmware-Version (BMS 0) | - | BMS-Firmware-Version des Kopfspeichers |
| `BS1` | Firmware-Version (BMS 1) | - | BMS-Firmware-Version des Erweiterungsspeichers 1 |
| `BS2` | Firmware-Version (BMS 2) | - | BMS-Firmware-Version des Erweiterungsspeichers 2 |
| `BS3` | Firmware-Version (BMS 3) | - | BMS-Firmware-Version des Erweiterungsspeichers 3 |
| `BS4` | Firmware-Version (BMS 4) | - | BMS-Firmware-Version des Erweiterungsspeichers 4 |
| `BS5` | Firmware-Version (BMS 5) | - | BMS-Firmware-Version des Erweiterungsspeichers 5 |
| `SN` | SN des Systemhosts | - | Seriennummer des Geraets |
| `MS` | Zaehlerstatus | - | Verbindungsstatus des lokalen Smart Meters. Hauefige Werte: `0 = Nicht gebunden`, `1 = Online`, `2 = Offline`; bei manchen Firmware-Versionen auch `3 = IP wird angefordert` |

### Number

| Entitaets-ID | Name | Einheit | Bereich | Schritt | Beschreibung |
|--------------|------|---------|---------|----------|--------------|
| `GS` | Sollwert Leistung Netzanschluss | W | `-2400` bis `2400` | `10` | Sollwert fuer die Leistung am Netzanschluss. Positive Werte bedeuten in der Regel Einspeisung, negative Werte in der Regel Netzbezug oder Netzladen. Die uebliche obere positive Grenze ist `800W` fuer SunEnergyXT 500 und `2400W` fuer SunEnergyXT 500 Pro |
| `IS` | Sollwert max. Wechselrichterleistung | W | `1` bis `2400` | `10` | Sollwert fuer die maximale Wechselrichter-Ausgangsleistung |
| `MG` | Maximale netzgekoppelte Ausgangsleistung | W | `1` bis `2400` | `1` | Maximale netzgekoppelte Ausgangsleistung. Die Obergrenze liegt bei `800W` fuer SunEnergyXT 500 und `2400W` fuer SunEnergyXT 500 Pro |
| `SI` | System Entladegrenze | % | `1` bis `30` | `1` | Minimaler SOC fuer Entladung im On-Grid-Betrieb |
| `SA` | System Ladegrenze | % | `70` bis `100` | `1` | Maximaler SOC fuer Ladung im On-Grid-Betrieb |
| `SO` | Systemlastanschluss-Entladegrenze | % | `1` bis `30` | `1` | Minimaler SOC fuer Entladung im Off-Grid- bzw. Lastanschluss-Betrieb |
| `PT` | Einstellung der automatischen Abschaltzeit | min | `30` bis `1440` | `1` | Zeit fuer die automatische Abschaltung |

### Switch

| Entitaets-ID | Name | Beschreibung |
|--------------|------|--------------|
| `LM` | Lokaler Modus | Schalter fuer den lokalen Modus. Wenn aktiv, priorisiert das Geraet die lokale Konfiguration |
| `MM` | Lokaler Eigenverbrauch | Schalter fuer den Modus "Lokaler Eigenverbrauch". Vor dem Aktivieren sollte eine gueltige `MD`-Smart-Meter-Verbindung hinterlegt werden. Beim Ausschalten wird `MD` ebenfalls geleert |
| `PM` | Parallelschaltmodus des Systems | Schalter fuer den Parallelbetrieb. Nur verwenden, wenn Geraetetopologie und Firmware dies unterstuetzen |
| `LFB` | Schalter fuer Lastprioritaet | Schalter fuer Lastprioritaet |
| `LPS` | Schalter fuer den Inselausgang | Schalter fuer den Inselausgang |

### Text

| Entitaets-ID | Name | Beschreibung |
|--------------|------|--------------|
| `MD` | Lokale Smart-Meter-Verbindung | JSON-Zeichenkette fuer die lokale Smart-Meter-Verbindung im Modus "Lokaler Eigenverbrauch". Es muss exakt der finale geraeteseitige Wert aus [API.md](API.md) verwendet werden. Die Einstellung wirkt direkt, ist aber kein garantiertes Ruecklesefeld |
| `TZ` | Systemzeitzone | POSIX-Zeitzonenstring. Fuer China kann z. B. `CST-8` verwendet werden; fuer Deutschland mit Sommerzeit z. B. `CET-1CEST,M3.5.0,M10.5.0/3`. Die Einstellung wirkt direkt, ist aber kein garantiertes Ruecklesefeld |

### Button

| Entitaets-ID | Name | Beschreibung |
|--------------|------|--------------|
| `RT` | Systemneustart | Sendet einen Neustartbefehl an das Geraet |

## Fehlerbehebung

### Geraet nicht gefunden

- Stellen Sie sicher, dass das Geraet eingeschaltet und mit dem lokalen Netzwerk verbunden ist
- Stellen Sie sicher, dass Home Assistant und das Geraet sich im selben Netzwerksegment befinden
- Falls die automatische Erkennung fehlschlaegt, geben Sie die IP-Adresse manuell ein
- Wenn das Netzwerk mDNS / Zeroconf blockiert, funktioniert die automatische Erkennung moeglicherweise nicht

### Probleme bei der Datenaktualisierung

- Pruefen Sie, ob die Netzwerkverbindung des Geraets stabil ist
- Pruefen Sie, ob `http://geraete-ip/read` direkt erreichbar ist
- Bestaetigen Sie nach einer Aenderung den finalen Zustand stets durch erneutes Auslesen

### Lokaler Eigenverbrauch funktioniert nicht

- Stellen Sie sicher, dass `MD` exakt dem Zaehlerbeispiel in [API.md](API.md) entspricht
- Stellen Sie sicher, dass `MM` aktiviert ist
- Pruefen Sie, ob `MS` einen online gemeldeten Zaehler zeigt und ob echte Zaehlerdaten aktualisiert werden
- Stellen Sie sicher, dass der Zaehler zu den in [API.md](API.md) dokumentierten geraeteinternen Zaehlerkategorien gehoert
- Verlassen Sie sich nach dem Schreiben nicht auf `MD` als garantiertes Echo

### Nutzung der Home-Assistant-Nulleinspeisungs-Blueprint

- Wenn Sie die Home-Assistant-Automatisierungs-Blueprint fuer Nulleinspeisung verwenden, deaktivieren Sie die lokale Nulleinspeisung bzw. den lokalen Eigenverbrauchsmodus (`MM`) des Geraets
- Die Blueprint arbeitet mit Home-Assistant-Zaehlerentitaeten und Home-Assistant-Automatisierungslogik; sie nutzt nicht den direkten lokalen Zaehlerlesepfad des Geraets
- Wenn Sie die geraeteeigene lokale Nulleinspeisungsfunktion verwenden moechten, konfigurieren Sie stattdessen die Zaehlerverbindung im Geraet. In diesem Modus muss der Zaehler nicht ueber Home Assistant verbunden sein
- Wenn Ihr Zaehler vom geraeteinternen `MM` + `MD`-Modus nicht unterstuetzt wird, aber in Home Assistant als Leistungsentitaet verfuegbar ist, verwenden Sie stattdessen die Blueprint

### Zeitzone ist falsch eingestellt

- `TZ` muss als POSIX-Zeitzonenstring gesetzt werden
- Verwenden Sie nicht `Europe/Berlin`, `UTC+1`, `CET` oder `CEST` als finalen `TZ`-Wert
- Fuer Deutschland sollte ein POSIX-String mit Sommerzeitregel verwendet werden, z. B. `CET-1CEST,M3.5.0,M10.5.0/3`
- Bestaetigen Sie nach dem Schreiben die resultierende Zeitzonenwirkung, statt ein exaktes Echo des geschriebenen `TZ`-Werts zu erwarten

## Beitrag

Beitraege sind willkommen. Bitte reichen Sie Issues oder Pull Requests auf [GitHub](https://github.com/SunEnergyXT/SunEnergyXT-500-Series) ein.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Details finden Sie in der Datei [LICENSE](LICENSE).

[releases-shield]: https://img.shields.io/github/release/SunEnergyXT/SunEnergyXT-500-Series.svg
[releases]: https://github.com/SunEnergyXT/SunEnergyXT-500-Series/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/SunEnergyXT/SunEnergyXT-500-Series.svg
[commits]: https://github.com/SunEnergyXT/SunEnergyXT-500-Series/commits/main
[license-shield]: https://img.shields.io/github/license/SunEnergyXT/SunEnergyXT-500-Series.svg
