# SunEnergyXT 500 Series Lokale API

## Language / Sprache

- [English](API.en.md)
- [Deutsch](API.de.md) (Standard)

Dieses Dokument richtet sich an Integrationen im lokalen Netzwerk und beschreibt die aktuell unterstuetzte lokale HTTP-API, die Feldbedeutungen und die Ausfuellregeln fuer Geraete der SunEnergyXT 500 Series.

## 1. Wichtige Klarstellungen

- Die stabile Antwortstruktur von `/read` ist `{"state":{"reported":{...}}}`. Nutzdaten muessen aus `state.reported` gelesen werden.
- Die stabile Anfragestruktur von `/write` ist `{"state":{"FIELD": value}}`. Partielle Feldupdates werden empfohlen.
- `MS` bedeutet Zaehlerstatus, nicht Hersteller.
- `ES / AS / DS / BS0..BS5` sind Firmware-Versionsfelder und keine generischen Statusmeldungen.
- `PB` ist das dokumentierte Feld fuer die Batterieleistung.
- `GD1 / GD2 / LD` sind rohe Tagesenergiezaehler in `Wh`, nicht in `kWh`.
- `MM` ist der Schalter fuer den lokalen Eigenverbrauchsmodus, und `MD` ist die Zaehlerverbindungs-Zeichenkette, die dieser Modus verwendet.
- `TZ` ist ein POSIX-Zeitzonenfeld und kein Landes- oder Regionsname. Fuer Deutschland sollte eine POSIX-Zeitzone mit Sommerzeitregel verwendet werden, zum Beispiel `CET-1CEST,M3.5.0,M10.5.0/3`.
- `MD` und `TZ` wirken direkt nach dem Schreiben, aber das Geraet gibt den exakt geschriebenen Wert moeglicherweise nicht zurueck.

## 2. Geltungsbereich und allgemeine Regeln

- Dieses Dokument beschreibt die lokale HTTP-API, die das AIO-Geraet im LAN bereitstellt.
- Die aktuell stabilen oeffentlichen Endpunkte sind:
  - `GET /read`
  - `POST /write`
- `/write` arbeitet als asynchrones Desired-State-Modell. `HTTP 2xx` bedeutet nur, dass das Geraet die Anfrage angenommen hat.
- Das tatsaechliche Ergebnis muss immer durch erneutes Lesen von `/read` bestaetigt werden.
- Die vorhandenen Felder koennen je nach Firmware-Zweig, Modell und Topologie leicht variieren. Integrationen sollten unbekannte Schluessel ignorieren und fehlende optionale Felder tolerieren.
- Falls nicht anders angegeben:
  - Leistung in `W`
  - Strom in `A`
  - Spannung in `V`
  - SOC in `%`
  - Tagesenergiezaehler in `Wh`

## 3. Endpunkte

| Endpunkt | Methode | Beschreibung |
| --- | --- | --- |
| `/read` | `GET` | Liest den aktuellen Geraetesnapshot aus `state.reported` |
| `/write` | `POST` | Schreibt ein oder mehrere Zielfelder partiell unter `state` |

### 3.1 `GET /read`

Anfrage:

```http
GET http://{device_ip}:{port}/read
```

Beispiel fuer die stabile Antwortstruktur:

```json
{
  "state": {
    "reported": {
      "SN": "TBe072a1edb090",
      "PK": 2,
      "ST": 1,
      "PV": 1820,
      "PV1": 460,
      "PV2": 455,
      "PV3": 450,
      "PV4": 455,
      "II1": 2.1,
      "II2": 2.1,
      "II3": 2.0,
      "II4": 2.1,
      "VP1": 219.0,
      "VP2": 218.6,
      "VP3": 218.8,
      "VP4": 218.9,
      "IW": 1820,
      "OP": 1510,
      "GP": -1530,
      "LP": 0,
      "PB": 1450,
      "SC": 54,
      "SC0": 54,
      "GD1": 5683,
      "GD2": 4789,
      "LD": 0,
      "GS": -1550,
      "IS": 2400,
      "LM": 0,
      "MM": 1,
      "MS": 1,
      "IP": "192.168.1.102",
      "COM": 80,
      "ES": "1.1.3",
      "AS": "1.0.6",
      "DS": "1.0.5",
      "BS0": "4.0.5",
      "timestamp": 1712476800000
    }
  }
}
```

Auswertungsregeln:

- Stabile Nutzdaten muessen aus `state.reported` gelesen werden.
- Einige Schluessel koennen je nach Firmware-Version, Topologie oder aktuellem Modus fehlen.

### 3.2 `POST /write`

Anfrage:

```http
POST http://{device_ip}:{port}/write
Content-Type: application/json

{
  "state": {
    "GS": -1500
  }
}
```

Schreibregeln:

- Senden Sie nur die Felder, die Sie aendern moechten. Partielle Schreibvorgaenge werden empfohlen.
- Verlassen Sie sich nicht auf ein festes Antwortformat im Body. Verwenden Sie `HTTP 2xx + /read`-Ruecklesen als Erfolgskriterium.
- Wenn ein Feld von der aktuellen Firmware nicht unterstuetzt wird, kann das Geraet es stillschweigend ignorieren und den bisherigen Wert beibehalten.
- `MD` und `TZ` wirken direkt nach einem erfolgreichen Schreibvorgang, aber das Geraet gibt moeglicherweise nicht denselben Wert zurueck. Bestaetigen Sie diese Felder ueber die Wirkung, nicht ueber ein direktes Echo.
- Fuer risikoreiche Aktionen wie `RT` sollte ein Senden-und-Bestaetigen-Ablauf verwendet werden, nicht Fire-and-forget.

## 4. Stabil schreibbare Felder und Ausfuellregeln

| Feld | Typ | Ruecklesbar | Beschreibung | Ausfuellregel |
| --- | --- | --- | --- | --- |
| `GS` | `integer` | Ja | Sollwert fuer die Netzleistung. `>0` bedeutet Einspeisung, `<0` bedeutet Netzbezug bzw. Netzladung, `0` bedeutet neutral. | Empfohlener Einspeisebereich: `0..800` fuer 500 Standard, `0..2400` fuer 500 Pro. Empfohlener Bezugsbereich: `-2400..0` fuer beide Modelle. Empfohlene Schrittweite: `10W`. |
| `IS` | `integer` | Ja | Sollwert fuer die maximale Wechselrichter-Ausgangsleistung. | Empfohlener Bereich: `1..2400`. Wenn die EMS/Wi-Fi-Firmware-Version nicht ueber `1.1.1` liegt, kann das Geraet diesen Schreibvorgang ignorieren. |
| `MG` | `integer` | Ja | Maximale netzgekoppelte Ausgangsleistung. | Empfohlener Bereich: `1..800` fuer 500 Standard, `1..2400` fuer 500 Pro. Empfohlene Schrittweite: `1W`. |
| `SI` | `integer` | Ja | Minimaler Entlade-SOC im Netzbetrieb. | Empfohlene Werte: `1`, `10` oder `20`. |
| `SA` | `integer` | Ja | Maximaler Lade-SOC im Netzbetrieb. | Empfohlene Werte: `70`, `80`, `90` oder `100`. |
| `SO` | `integer` | Ja | Minimaler Entlade-SOC im Inselbetrieb. | Empfohlene Werte: `1`, `10` oder `20`. |
| `LM` | `integer` | Ja | Schalter fuer den lokalen Modus. `0 = aus`, `1 = ein`. | Sobald der lokale Modus aktiviert ist, ist zu erwarten, dass die meisten Cloud-Fernsteuerungen blockiert bleiben, bis der lokale Modus wieder deaktiviert wird. |
| `MM` | `integer` | Ja | Schalter fuer den lokalen Eigenverbrauchsmodus. `0 = aus`, `1 = ein`. | Am sichersten ist es, zuerst ein gueltiges `MD` vorzubereiten oder `MM = 1` zusammen mit `MD` in derselben Anfrage zu senden. Die Home-Assistant-Integration leert `MD`, wenn `MM` ausgeschaltet wird. Den finalen Zaehlerstatus ueber `MS` bestaetigen. |
| `LFB` | `integer` | Ja | Schalter fuer Lastprioritaet. `0 = aus`, `1 = ein`. | Nur verwenden, wenn die Geraetefirmware Lastprioritaet unterstuetzt. |
| `LPS` | `integer` | Ja | Schalter fuer den Inselausgang. `0 = aus`, `1 = ein`. | Nur verwenden, wenn die Geraetefirmware die Steuerung des Inselausgangs unterstuetzt. |
| `MD` | `string` | Wirkt direkt | JSON-Zeichenkette fuer die lokale Zaehlerverbindung. | Fuellen Sie `MD` mit dem finalen geraeteseitigen JSON-Zeichenketteninhalt aus Abschnitt 5. Die Einstellung wirkt direkt, aber das Geraet gibt den geschriebenen `MD`-Wert moeglicherweise nicht zurueck. Bestaetigen Sie das Ergebnis ueber `MS` und die echten Zaehlerdaten. |
| `RT` | `integer` | Trigger | Neustart-Trigger fuer das Geraet. | Nur `1` schreiben. Nach dem Neustart erneut `/read` lesen, sobald das Geraet wieder erreichbar ist. |
| `TZ` | `string` | Wirkt direkt | POSIX-Zeitzonenfeld. | Es muss eine POSIX-Zeitzonen-Zeichenkette sein, kein Landes- oder Regionsname. Deutschland sollte `CET-1CEST,M3.5.0,M10.5.0/3` verwenden, China kann `CST-8` verwenden. Schreiben Sie nicht `Europe/Berlin`, `Europe/Paris`, `PRC`, `UTC+1`, `UTC+2`, `CET` oder `CEST`. Die Einstellung wirkt direkt, aber das Geraet gibt den geschriebenen `TZ`-Wert moeglicherweise nicht zurueck. |
| `NT` | `integer` | Nicht garantiert | Landes-/Sicherheitsprofil-ID. | Beispiel: Deutschland verwendet haeufig `60`. Dieses Feld nur schreiben, wenn die Zuordnung Land-zu-Profil eindeutig bekannt ist. |
| `UO` | `integer` | Ja | Schalter fuer den UPS-Modus. `0 = aus`, `1 = ein`. | Wenn `UO = 1`, koennen viele nicht UPS-bezogene Einstellungen wirkungslos bleiben, bis der UPS-Modus wieder deaktiviert wird. |
| `UG` | `integer` | Ja | Netzladeleistung im UPS-Modus. | `0` bedeutet keine Netzladung im UPS-Modus. Empfohlener nicht-null Bereich: `20..2400`. |
| `FP` | `integer` | Ja | Maximale PV-Bypass-Ausgangsleistung nach vollstaendiger Batterieladung. | Empfohlener Bereich: `20..aktuell zulaessige maximale Ausgangsleistung`. Die Obergrenze folgt in der Regel der aktuell zulaessigen maximalen Netzeinspeiseleistung des Geraets. |

### 4.1 Reservierte Felder

Die folgenden Felder koennen auf einigen Geraeten oder Firmware-Versionen auftreten, werden jedoch nicht fuer normale Integrationen empfohlen. Verwenden Sie sie nur, wenn das Geraeteprotokoll explizit bestaetigt wurde.

| Feld | Typ | Bedeutung | Hinweise |
| --- | --- | --- | --- |
| `SI1` | `integer` | Entlade-SOC-Hysterese | Nicht als Standardfeld fuer Integrationen empfohlen |
| `SA1` | `integer` | Lade-SOC-Hysterese | Nicht als Standardfeld fuer Integrationen empfohlen |
| `PO` | `integer` | Leistungs-Ein/Aus-Steuerung | Nicht als Standardfeld fuer Integrationen empfohlen |
| `PT` | `integer` | Automatische Abschaltzeit | Ein haeufiger Bereich ist `30..1440` Minuten, sollte aber nicht als feste oeffentliche Zusage behandelt werden |
| `SD` | `integer` | Feld fuer Ein/Aus des Geraets | Nur verwenden, wenn das Firmware-Verhalten bestaetigt ist |
| `CF` | `integer` | Trigger zum Fehlerloeschen | Nur verwenden, wenn das Firmware-Verhalten bestaetigt ist |

## 5. Regeln fuer `MD` und Zaehlerklassifizierung

`MD` ist die JSON-Zeichenkette, die in `state.MD` geschrieben wird. Sie teilt dem Geraet mit, wie der lokale Zaehler gefunden und ausgelesen werden soll.

Ausfuellregeln:

- In den Beispielen unten wird `MD` als finaler geraeteseitiger JSON-Zeichenketteninhalt ohne zusaetzliche Escape-Slashes gezeigt.
- Wenn Ihr HTTP-Client einen JSON-Request-Body serialisiert, wird das aeussere Escaping der Zeichenkette meist automatisch uebernommen.
- Bei `mdns`-Zaehlern muss der Host-Teil in `dat_url` auf `0.0.0.0` bleiben. Er darf nicht manuell durch die echte LAN-IP ersetzt werden.
- In einigen Clients kann `=` waehrend der Serialisierung als `\u003d` erscheinen. Das ist gleichwertig und kann unveraendert gesendet werden.

### 5.1 Endgueltiges Format des `MD`-Felds

Fuellen Sie `MD` im folgenden finalen geraeteseitigen Format aus:

```text
{"mode":"mdns","mdns":{"sn":"8c4f00c31844","dat_url":"http://0.0.0.0/rpc/EM.GetStatus?id\u003d0"},"dat_str":{"pwr":"total_act_power"}}
```

Bedeutung der Felder:

| Pfad | Bedeutung |
| --- | --- |
| `mode` | Modus zur Zaehlererkennung. Das Geraet verwendet aktuell `mdns` oder `direct` |
| `mdns.sn` | Zaehler-SN oder SN-Praefix fuer das lokale mDNS-Matching |
| `mdns.dat_url` | Endgueltige URL, die das Geraet fuer den mDNS-Modus speichert |
| `direct.dat_url` | Endgueltige vollstaendige URL, die das Geraet fuer den Direktmodus speichert |
| `dat_str.pwr` | Name oder Ausdruck des Leistungsfelds in den Zaehlerdaten |

### 5.2 Unterstuetzte Zaehlerkategorien

Das Geraet unterstuetzt aktuell die folgenden vier Zaehlerkategorien fuer den lokalen Eigenverbrauchsmodus:

| Zaehlertyp | Finales `mode` | Finale Verbindungsfelder | Finales `dat_str.pwr` | Ausfuellhinweise |
| --- | --- | --- | --- | --- |
| `ECOTRACKER` | `direct` | `direct.dat_url = http://{meter_ip}/v1/json` | `power` | Die aktuelle LAN-IP des Zaehlergeraets ist erforderlich. Es darf kein Platzhalter verwendet werden |
| `SHELLY_3EM_METER` | `mdns` | `mdns.sn = Zaehler-SN`; `mdns.dat_url = http://0.0.0.0/status` | `total_power` | Die Zaehler-SN direkt verwenden |
| `SHELLY_PRO3EM_METER` | `mdns` | `mdns.sn = Zaehler-SN`; `mdns.dat_url = http://0.0.0.0/rpc/EM.GetStatus?id\u003d0` | `total_act_power` | Die Zaehler-SN direkt verwenden |
| `TASMOTA` | `mdns` | `mdns.sn = SN-Praefix ohne die letzten 4 Zeichen`; `mdns.dat_url = http://0.0.0.0/cm?cmnd=Status%208` | Abhaengig vom Subtyp | `dat_str.pwr` muss exakt zum aktuellen Subtyp passen. Die vollstaendige Liste steht in Abschnitt 5.4 |

### 5.3 `MD`-Beispiele nach Zaehlerkategorie

#### 5.3.1 EcoTracker

Fuellen Sie diesen `MD`-Wert aus:

```text
{"mode":"direct","direct":{"dat_url":"http://192.168.1.50/v1/json"},"dat_str":{"pwr":"power"}}
```

#### 5.3.2 Shelly 3EM

Fuellen Sie diesen `MD`-Wert aus:

```text
{"mode":"mdns","mdns":{"sn":"B929CC","dat_url":"http://0.0.0.0/status"},"dat_str":{"pwr":"total_power"}}
```

#### 5.3.3 Shelly Pro 3EM

Fuellen Sie diesen `MD`-Wert aus:

```text
{"mode":"mdns","mdns":{"sn":"8c4f00c31844","dat_url":"http://0.0.0.0/rpc/EM.GetStatus?id\u003d0"},"dat_str":{"pwr":"total_act_power"}}
```

#### 5.3.4 Tasmota

Hinweise:

- `mode` ist immer `mdns`
- `mdns.dat_url` ist immer `http://0.0.0.0/cm?cmnd=Status%208`
- `mdns.sn` ist nicht die vollstaendige Geraete-SN. Verwendet wird das Praefix ohne die letzten 4 Zeichen. Beispiel: `tasmota-c28338-0824` wird zu `tasmota-c28338`
- `dat_str.pwr` muss exakt zum aktuellen Zaehler-Subtyp passen

Fuellen Sie diesen `MD`-Wert aus:

```text
{"mode":"mdns","mdns":{"sn":"tasmota-c28338","dat_url":"http://0.0.0.0/cm?cmnd=Status%208"},"dat_str":{"pwr":"Power"}}
```

### 5.4 Vollstaendige BitShake-/Tasmota-Zuordnung fuer `dat_str.pwr`

Die folgende Tabelle enthaelt alle aktuell verfuegbaren BitShake-/Tasmota-Werte fuer `dat_str.pwr`:

| Subtyp | `dat_str.pwr` |
| --- | --- |
| `APOX` | `Power` |
| `LEPUS` | `power` |
| `Norax` | `Power` |
| `PICUS` | `power` |
| `GS303` | `Power` |
| `DWZE12` | `Power` |
| `DWS7410` | `Power` |
| `DWS7412` | `Power` |
| `DWS7420` | `Power` |
| `DWS7612` | `Power` |
| `DWSB12` | `Power` |
| `DWSB20` | `Power` |
| `DWSE20` | `Power` |
| `M60` | `Power` |
| `Q3A` | `Power` |
| `Q3B` | `Power` |
| `Q3C` | `Power` |
| `Q3D` | `Power` |
| `Q1A` | `Power` |
| `Q3M` | `Power` |
| `eBZ` | `Power` |
| `SGM` | `Power` |
| `AS1440` | `power_in - power_out` |
| `AS2020` | `Power` |
| `AS3500` | `Power` |
| `T510` | `Power_total` |
| `eBZD` | `Power` |
| `ED300L` | `Power` |
| `ED300S` | `Power` |
| `eHZ` | `Power - Power2` |
| `EMH` | `Power` |
| `EHZ161` | `watt_l1 + watt_l2 + watt_l3` |
| `EHZ361` | `watt_l1 + watt_l2 + watt_l3` |
| `EHZ363` | `Power - Power2` |
| `HBZ` | `Power` |
| `DTZ` | `Power` |
| `EHZ` | `Power` |
| `MT175` | `Power` |
| `MT176` | `Power` |
| `MT382` | `Power` |
| `MT631` | `Power` |
| `MT681` | `Power` |
| `MT691` | `Power` |
| `Itron` | `Power` |
| `KAIFA` | `Power` |
| `E220` | `Power` |
| `E230` | `Power_in * 1000` |
| `E320` | `Power` |
| `E350` | `Power_in * 1000` |
| `E650` | `((1-5-0) - (2-5-0)) * 1000` |
| `ZMB120` | `(kW_L1+L2+L3) * 1000` |
| `L20` | `Power` |
| `LK13BE` | `Power \|\| current` |
| `Metcom` | `power_in - power_out` |
| `Siemens` | `(Pp - Pm) * 1000` |
| `Smarty` | `power` |
| `SML` | `Power` |

Wenn der aktuelle Zaehler-Subtyp nicht in der obigen Liste aufgefuehrt ist, sollte fuer diesen Tasmota-Zaehler kein `MD` gesetzt werden. Andernfalls kann das Geraet den Zaehler im lokalen Eigenverbrauchsmodus nicht korrekt auslesen.

## 6. Stabil gemeldete Felder

| Feld | Typ | Beschreibung | Hinweise |
| --- | --- | --- | --- |
| `SN` | `string` | Seriennummer des Geraets | Stabiles Identifikationsmerkmal |
| `PK` | `integer` | Leistungstyp des Geraets. `1 = 500 Standard (800W)`, `2 = 500 Pro (2400W)` | Fuer Logikzweige bevorzugt dieses Feld statt des angezeigten Modellnamens verwenden |
| `ST` | `integer` | Systemstatuscode | Aktuell ist nur `0 = aus` bestaetigt; andere Werte sind firmwaredefiniert |
| `WT` | `integer` | Wi-Fi-/Netzwerkstatuscode | Firmwaredefinierte Integer-Enumeration |
| `PV` | `number` | Gesamte PV-Eingangsleistung | Einheit `W` |
| `PV1..PV4` | `number` | PV-Leistung MPPT 1..4 | Einheit `W` |
| `II1..II4` | `number` | Strom MPPT 1..4 | Einheit `A` |
| `VP1..VP4` | `number` | Spannung MPPT 1..4 | Einheit `V` |
| `GP` | `number` | Netzleistung. Positiv bedeutet Einspeisung, negativ bedeutet Netzbezug bzw. Netzladung | Einheit `W` |
| `LP` | `number` | Lastleistung | Einheit `W` |
| `PB` | `number` | Batterieleistung. Positiv bedeutet Laden, negativ bedeutet Entladen | Einheit `W` |
| `IW` | `number` | Gesamte Eingangsleistung | Einheit `W` |
| `OP` | `number` | Gesamte Ausgangsleistung | Einheit `W` |
| `SC` | `number` | Gesamt-SOC des Systems | Einheit `%` |
| `SC0..SC5` | `number` | SOC-Werte von Master- und Slave-Batterien | `SC0` ist die Master-Batterie, `SC1..SC5` sind Slaves |
| `BN` | `integer` | Gesamtanzahl der Batteriepacks | Nützlich fuer die Erkennung der Topologie |
| `ON` | `integer` | Anzahl der online befindlichen Batteriepacks | Nützlich fuer die Erkennung von Mehrpack-Systemen |
| `GD1` | `number` | Taegliche Netzladeenergie | Rohwert in `Wh` |
| `GD2` | `number` | Taegliche Netzeinspeiseenergie | Rohwert in `Wh` |
| `LD` | `number` | Taegliche Inselbetriebs-Lastenergie | Rohwert in `Wh` |
| `GS` | `integer` | Ruecklesewert des aktuellen Netzleistungs-Sollwerts | Die Vorzeichenbedeutung entspricht dem Schreibvertrag |
| `IS` | `integer` | Ruecklesewert der aktuellen maximalen Netzeinspeisegrenze | Die Obergrenze haengt vom Modell ab |
| `SI / SA / SO` | `integer` | SOC-Grenzwerte | `SI1 / SA1` sind reservierte Felder und sollten nicht standardmaessig angenommen werden |
| `LM` | `integer` | Status des lokalen Modus | `0 = aus`, `1 = ein` |
| `MM` | `integer` | Status des lokalen Eigenverbrauchsmodus | `0 = aus`, `1 = ein` |
| `MD` | `string` | Laufzeitwert der Zaehlerverbindung, wenn vorhanden | Nicht als garantiertes Echo des zuletzt geschriebenen `MD` verwenden |
| `MS` | `integer` | Zaehlerstatus | Aktuell bekannte Werte: `0 = kein Zaehler gebunden`, `1 = online`, `2 = offline`, `3 = IP-Anfrage laeuft` |
| `IP` | `string` | IP-Adresse des lokalen Modus | Vom Geraet gemeldet |
| `COM` | `integer` | Port des lokalen Modus | Vom Geraet gemeldet |
| `TZ` | `string` | Laufzeitwert der Zeitzone, wenn vorhanden | Nicht als garantiertes Echo des zuletzt geschriebenen `TZ` verwenden |
| `ES` | `string` | Wi-Fi-/Modul-Firmware-Version | Stabiles Versionsfeld |
| `AS` | `string` | AC-Firmware-Version | Stabiles Versionsfeld |
| `DS` | `string` | DC-Firmware-Version | Stabiles Versionsfeld |
| `BS0..BS5` | `string` | BMS-Firmware-Versionen | `BS0` ist das Master-Pack, `BS1..BS5` sind Slave-Packs |
| `TF / EF / DF1 / DF2 / AF1 / AF2 / BF` | `integer` | Fehler-Bitmasks fuer Prompt-, EMS-, DC-, AC- und BMS-Domaenen | Diese Felder als Bitmasks behandeln, nicht als einzelne Statuscodes |
| `FP` | `integer` | Maximale PV-Bypass-Ausgangsleistung nach voller Ladung | Einheit `W` |
| `UO` | `integer` | Status des UPS-Modus | `0 = aus`, `1 = ein` |
| `UG` | `integer` | Netzladeleistung im UPS-Modus | Einheit `W` |
| `timestamp` | `integer` | Erfassungszeitstempel | In der Regel Millisekunden |

## 7. Anfragebeispiele

### 7.1 Aktuellen Geraetestatus lesen

```http
GET http://192.168.1.102/read
```

### 7.2 Lokalen Modus aktivieren

```http
POST http://192.168.1.102/write
Content-Type: application/json

{
  "state": {
    "LM": 1
  }
}
```

### 7.3 Netzladeleistung auf 1500 W setzen

```http
POST http://192.168.1.102/write
Content-Type: application/json

{
  "state": {
    "GS": -1500
  }
}
```

### 7.4 POSIX-Zeitzone fuer Deutschland setzen

```http
POST http://192.168.1.102/write
Content-Type: application/json

{
  "state": {
    "TZ": "CET-1CEST,M3.5.0,M10.5.0/3"
  }
}
```

Die Einstellung wirkt direkt, aber das Geraet gibt moeglicherweise nicht denselben `TZ`-Wert zurueck.

### 7.5 Lokalen Eigenverbrauchsmodus mit Shelly Pro 3EM aktivieren

```http
POST http://192.168.1.102/write
Content-Type: application/json
```

Schreiben Sie die folgenden Werte unter `state`:

| Feld | Wert |
| --- | --- |
| `MM` | `1` |
| `MD` | `{"mode":"mdns","mdns":{"sn":"8c4f00c31844","dat_url":"http://0.0.0.0/rpc/EM.GetStatus?id\u003d0"},"dat_str":{"pwr":"total_act_power"}}` |

`MD` wirkt direkt, aber das Geraet gibt moeglicherweise nicht denselben Wert zurueck. Bestaetigen Sie den Erfolg ueber `MS` und die echten Zaehlerdaten.

### 7.6 Geraet neu starten

```http
POST http://192.168.1.102/write
Content-Type: application/json

{
  "state": {
    "RT": 1
  }
}
```

## 8. Integrationshinweise

- Verwenden Sie nach jedem Schreibvorgang immer `/read` als massgebliche Quelle.
- Bestaetigen Sie `MD` und `TZ` ueber ihre Wirkung. Verlassen Sie sich bei diesen Feldern nicht auf ein garantiertes direktes Echo.
- Fuer normales Monitoring ist ein Polling-Intervall von `2s ~ 5s` in der Regel angemessen. Fuer die kurzzeitige Schreibbestaetigung koennen temporaer `1s ~ 2s` verwendet werden.
- Vermeiden Sie es, nicht zusammengehoerige Aktionen in derselben `/write`-Anfrage zu mischen, insbesondere `RT` zusammen mit Konfigurationsaenderungen.
- Wenn mehrere Firmware-Zweige unterstuetzt werden muessen, sollte die Integration nur auf den in diesem Dokument definierten stabilen Kernfeldern aufbauen. Gehen Sie nicht davon aus, dass undokumentierte Felder immer vorhanden sind.
