# SunEnergyXT 500 Series Local API

## Language / Sprache

- [English](API.en.md) (default)
- [Deutsch](API.de.md)

This document is for LAN-side integrations and describes the currently supported local HTTP API, field meanings, and fill rules for SunEnergyXT 500 Series devices.

## 1. Key Corrections

- The stable `/read` response shape is `{"state":{"reported":{...}}}`. Business data must be read from `state.reported`.
- The stable `/write` request shape is `{"state":{"FIELD": value}}`. Partial field updates are recommended.
- `MS` means meter status, not manufacturer.
- `ES / AS / DS / BS0..BS5` are firmware version fields, not generic status strings.
- `BP` is the documented battery power field.
- `GD1 / GD2 / LD` are raw daily energy counters in `Wh`, not `kWh`.
- `MM` is the Local Self-Consumption Mode switch, and `MD` is the meter connection string used by that mode.
- `TZ` is a POSIX timezone field, not a country or region name. Germany should use a DST-aware POSIX timezone string such as `CET-1CEST,M3.5.0,M10.5.0/3`.
- `MD` and `TZ` take effect immediately after a write, but the device may not echo the exact written value back.

## 2. Scope and General Contract

- This document covers the local HTTP API exposed by the AIO device on the LAN.
- The current stable public endpoints are:
  - `GET /read`
  - `POST /write`
- `/write` follows an asynchronous desired-state model. `HTTP 2xx` only means the device accepted the request.
- The real result must always be confirmed by reading `/read` again.
- Field presence may vary slightly across firmware branches, models, and topology. Integrations should ignore unknown keys and tolerate missing optional keys.
- Unless otherwise stated:
  - Power is in `W`
  - Current is in `A`
  - Voltage is in `V`
  - SOC is in `%`
  - Daily energy counters are in `Wh`

## 3. Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/read` | `GET` | Read the current device snapshot from `state.reported` |
| `/write` | `POST` | Partially write one or more target fields under `state` |

### 3.1 `GET /read`

Request:

```http
GET http://{device_ip}:{port}/read
```

Stable response shape example:

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
      "BP": 1450,
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

Parsing rules:

- Stable business data must be parsed from `state.reported`.
- Some keys may be absent depending on firmware version, topology, or current mode.

### 3.2 `POST /write`

Request:

```http
POST http://{device_ip}:{port}/write
Content-Type: application/json

{
  "state": {
    "GS": -1500
  }
}
```

Write contract notes:

- Only send the fields you want to change. Partial writes are recommended.
- Do not rely on a fixed response body format. Use `HTTP 2xx + /read echo` as the success rule.
- If a field is unsupported by the current firmware, the device may silently ignore it and keep the previous value.
- `MD` and `TZ` take effect immediately after a successful write, but the device may not echo the same value back. Confirm them by the resulting effect, not by direct field echo.
- For high-risk actions such as `RT`, use a fire-and-confirm flow rather than fire-and-forget.

## 4. Stable Writable Fields and Fill Rules

| Field | Type | Readback | Description | Fill Rule |
| --- | --- | --- | --- | --- |
| `GS` | `integer` | Yes | On-grid power setpoint. `>0` means export/feed-in, `<0` means grid import / grid charging, `0` means neutral. | Recommended export range: `0..800` for 500 Standard, `0..2400` for 500 Pro. Recommended import range: `-2400..0` for both models. Recommended step: `10W`. |
| `IS` | `integer` | Yes | Max inverter output power setpoint. | Recommended range: `1..2400`. When the EMS/Wi-Fi firmware version is not above `1.1.1`, the device may ignore this write. |
| `MG` | `integer` | Yes | Maximum grid-connected output power. | Recommended range: `1..800` for 500 Standard, `1..2400` for 500 Pro. Recommended step: `1W`. |
| `SI` | `integer` | Yes | On-grid minimum discharge SOC. | Recommended values: `1`, `10`, or `20`. |
| `SA` | `integer` | Yes | On-grid maximum charge SOC. | Recommended values: `70`, `80`, `90`, or `100`. |
| `SO` | `integer` | Yes | Off-grid minimum discharge SOC. | Recommended values: `1`, `10`, or `20`. |
| `LM` | `integer` | Yes | Local mode switch. `0 = off`, `1 = on`. | Once local mode is enabled, most cloud-side remote control is expected to be restricted until local mode is turned off. |
| `MM` | `integer` | Yes | Local Self-Consumption Mode switch. `0 = off`, `1 = on`. | The safest pattern is to prepare a valid `MD` first, or submit `MM = 1` together with `MD` in the same request. The Home Assistant integration clears `MD` when turning `MM` off. Confirm final meter status via `MS`. |
| `LFB` | `integer` | Yes | Load priority switch. `0 = off`, `1 = on`. | Use only when the device firmware supports load priority. |
| `LPS` | `integer` | Yes | Off-grid output switch. `0 = off`, `1 = on`. | Use only when the device firmware supports off-grid output control. |
| `MD` | `string` | Effect only | Meter local connection JSON string. | Fill `MD` with the final device-side JSON string content shown in Section 5. The setting takes effect immediately, but the device may not echo the written `MD` value back. Confirm the result via `MS` and actual meter data. |
| `RT` | `integer` | Trigger | Device restart trigger. | Write `1` only. Read `/read` again after the device comes back online. |
| `TZ` | `string` | Effect only | POSIX timezone field. | It must be a POSIX timezone string, not a country or region name. Germany should use `CET-1CEST,M3.5.0,M10.5.0/3`; China can use `CST-8`. Do not write `Europe/Berlin`, `Europe/Paris`, `PRC`, `UTC+1`, `UTC+2`, `CET`, or `CEST`. The setting takes effect immediately, but the device may not echo the written `TZ` value back. |
| `NT` | `integer` | Not guaranteed | Nation / safety profile identifier. | Example: Germany commonly uses `60`. Only write this field when the country-to-profile mapping is clear. |
| `UO` | `integer` | Yes | UPS mode switch. `0 = off`, `1 = on`. | When `UO = 1`, many non-UPS settings may no longer take effect until UPS mode is disabled. |
| `UG` | `integer` | Yes | UPS grid charging power. | `0` means no grid charging in UPS mode. Recommended non-zero range: `20..2400`. |
| `FP` | `integer` | Yes | Max PV bypass output power after the battery is full. | Recommended range: `20..current allowed max output power`. The upper limit usually follows the device's currently allowed max grid output capability. |

### 4.1 Reserved Fields

The following fields may appear on some devices or firmware versions, but they are not recommended for normal integrations. Use them only when the device protocol has been explicitly confirmed.

| Field | Type | Meaning | Notes |
| --- | --- | --- | --- |
| `SI1` | `integer` | Discharge SOC hysteresis | Not recommended as a default integration field |
| `SA1` | `integer` | Charge SOC hysteresis | Not recommended as a default integration field |
| `PO` | `integer` | Power enable/stop control | Not recommended as a default integration field |
| `PT` | `integer` | Auto power-off time | A common range is `30..1440` minutes, but this should not be treated as a fixed public guarantee |
| `SD` | `integer` | Power on/off field | Use only after firmware behavior is confirmed |
| `CF` | `integer` | Clear-fault trigger | Use only after firmware behavior is confirmed |

## 5. `MD` Fill Rules and Meter Classification

`MD` is the JSON string written into `state.MD`. It tells the device how to discover and read the local meter.

Fill rules:

- In the examples below, `MD` is shown as the final device-side JSON string content, without extra escape slashes.
- When your HTTP client serializes a JSON request body, the outer string escaping is usually handled automatically.
- For `mdns` meters, the host part inside `dat_url` must remain `0.0.0.0`. Do not replace it with the real LAN IP manually.
- In some clients, `=` may appear as `\u003d` during serialization. This is equivalent and can be sent as-is.

### 5.1 Final `MD` Field Shape

Fill `MD` with a value in the following final device-side format:

```text
{"mode":"mdns","mdns":{"sn":"8c4f00c31844","dat_url":"http://0.0.0.0/rpc/EM.GetStatus?id\u003d0"},"dat_str":{"pwr":"total_act_power"}}
```

Field meanings:

| Path | Meaning |
| --- | --- |
| `mode` | Meter discovery mode. The device currently uses `mdns` or `direct` |
| `mdns.sn` | Meter SN or SN prefix used for local mDNS matching |
| `mdns.dat_url` | Final URL stored by the device for mDNS mode |
| `direct.dat_url` | Final full URL stored by the device for direct mode |
| `dat_str.pwr` | Power field name or expression in the meter payload |

### 5.2 Supported Meter Categories

The device currently supports the following four meter categories for Local Self-Consumption Mode:

| Meter Type | Final `mode` | Final Connection Fields | Final `dat_str.pwr` | Fill Notes |
| --- | --- | --- | --- | --- |
| `ECOTRACKER` | `direct` | `direct.dat_url = http://{meter_ip}/v1/json` | `power` | The current LAN IP of the meter is required. Do not use a placeholder |
| `SHELLY_3EM_METER` | `mdns` | `mdns.sn = meter SN`; `mdns.dat_url = http://0.0.0.0/status` | `total_power` | Use the meter SN directly |
| `SHELLY_PRO3EM_METER` | `mdns` | `mdns.sn = meter SN`; `mdns.dat_url = http://0.0.0.0/rpc/EM.GetStatus?id\u003d0` | `total_act_power` | Use the meter SN directly |
| `TASMOTA` | `mdns` | `mdns.sn = SN prefix without the last 4 characters`; `mdns.dat_url = http://0.0.0.0/cm?cmnd=Status%208` | Depends on subtype | `dat_str.pwr` must match the exact current subtype. See the full list in Section 5.4 |

### 5.3 `MD` Examples by Meter Category

#### 5.3.1 EcoTracker

Fill this `MD` value:

```text
{"mode":"direct","direct":{"dat_url":"http://192.168.1.50/v1/json"},"dat_str":{"pwr":"power"}}
```

#### 5.3.2 Shelly 3EM

Fill this `MD` value:

```text
{"mode":"mdns","mdns":{"sn":"B929CC","dat_url":"http://0.0.0.0/status"},"dat_str":{"pwr":"total_power"}}
```

#### 5.3.3 Shelly Pro 3EM

Fill this `MD` value:

```text
{"mode":"mdns","mdns":{"sn":"8c4f00c31844","dat_url":"http://0.0.0.0/rpc/EM.GetStatus?id\u003d0"},"dat_str":{"pwr":"total_act_power"}}
```

#### 5.3.4 Tasmota

Notes:

- `mode` is always `mdns`
- `mdns.dat_url` is always `http://0.0.0.0/cm?cmnd=Status%208`
- `mdns.sn` is not the full device SN. It uses the prefix with the last 4 characters removed. Example: `tasmota-c28338-0824` becomes `tasmota-c28338`
- `dat_str.pwr` must match the exact meter subtype

Fill this `MD` value:

```text
{"mode":"mdns","mdns":{"sn":"tasmota-c28338","dat_url":"http://0.0.0.0/cm?cmnd=Status%208"},"dat_str":{"pwr":"Power"}}
```

### 5.4 Full BitShake / Tasmota `dat_str.pwr` Mapping List

The following table contains the complete currently available BitShake / Tasmota `dat_str.pwr` values:

| Subtype | `dat_str.pwr` |
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

If the current meter subtype is not listed above, do not fill `MD` for that Tasmota meter. Otherwise the device will not be able to read the meter correctly in Local Self-Consumption Mode.

## 6. Stable Reported Fields

| Field | Type | Description | Notes |
| --- | --- | --- | --- |
| `SN` | `string` | Device serial number | Stable identifier |
| `PK` | `integer` | Device power type. `1 = 500 Standard (800W)`, `2 = 500 Pro (2400W)` | Prefer this over model display text for logic branching |
| `ST` | `integer` | System status code | Only `0 = off` is currently confirmed; other values are firmware-defined |
| `WT` | `integer` | Wi-Fi / network state code | Firmware-defined integer enum |
| `PV` | `number` | Total PV input power | Unit `W` |
| `PV1..PV4` | `number` | MPPT 1..4 PV power | Unit `W` |
| `II1..II4` | `number` | MPPT 1..4 current | Unit `A` |
| `VP1..VP4` | `number` | MPPT 1..4 voltage | Unit `V` |
| `GP` | `number` | Grid power. Positive means export/feed-in, negative means import/grid charging | Unit `W` |
| `LP` | `number` | Load power | Unit `W` |
| `BP` | `number` | Battery power. Positive means charging, negative means discharging | Unit `W` |
| `IW` | `number` | Total input power | Unit `W` |
| `OP` | `number` | Total output power | Unit `W` |
| `SC` | `number` | Total system SOC | Unit `%` |
| `SC0..SC5` | `number` | Master and slave battery SOC values | `SC0` is the master battery, `SC1..SC5` are slaves |
| `BN` | `integer` | Total battery pack count | Useful for topology awareness |
| `ON` | `integer` | Online battery pack count | Useful for multi-pack awareness |
| `GD1` | `number` | Daily grid charging energy | Raw unit `Wh` |
| `GD2` | `number` | Daily grid export energy | Raw unit `Wh` |
| `LD` | `number` | Daily off-grid load output energy | Raw unit `Wh` |
| `GS` | `integer` | Echo of the current on-grid power setpoint | Sign semantics match the write contract |
| `IS` | `integer` | Echo of the current max grid output setting | Upper bound depends on model |
| `SI / SA / SO` | `integer` | SOC limits | `SI1 / SA1` are reserved fields and should not be assumed by default |
| `LM` | `integer` | Local mode state | `0 = off`, `1 = on` |
| `MM` | `integer` | Local Self-Consumption Mode state | `0 = off`, `1 = on` |
| `MD` | `string` | Meter connection runtime value when present | Do not use it as guaranteed echo of the last written `MD` |
| `MS` | `integer` | Meter state | Current known values: `0 = no meter bound`, `1 = online`, `2 = offline`, `3 = requesting IP` |
| `IP` | `string` | Local mode IP address | Reported by the device |
| `COM` | `integer` | Local mode port | Reported by the device |
| `TZ` | `string` | Timezone runtime value when present | Do not use it as guaranteed echo of the last written `TZ` |
| `ES` | `string` | Wi-Fi / module firmware version | Stable version field |
| `AS` | `string` | AC firmware version | Stable version field |
| `DS` | `string` | DC firmware version | Stable version field |
| `BS0..BS5` | `string` | BMS firmware versions | `BS0` is the master pack, `BS1..BS5` are slave packs |
| `TF / EF / DF1 / DF2 / AF1 / AF2 / BF` | `integer` | Fault bitmasks for prompt, EMS, DC, AC, and BMS domains | Treat these as bitmasks, not as single status codes |
| `FP` | `integer` | Full-charge PV bypass max output power | Unit `W` |
| `UO` | `integer` | UPS mode state | `0 = off`, `1 = on` |
| `UG` | `integer` | UPS grid charging power | Unit `W` |
| `timestamp` | `integer` | Collection timestamp | Usually milliseconds |

## 7. Request Examples

### 7.1 Read Current Snapshot

```http
GET http://192.168.1.102/read
```

### 7.2 Enable Local Mode

```http
POST http://192.168.1.102/write
Content-Type: application/json

{
  "state": {
    "LM": 1
  }
}
```

### 7.3 Set Grid Charging Power to 1500W

```http
POST http://192.168.1.102/write
Content-Type: application/json

{
  "state": {
    "GS": -1500
  }
}
```

### 7.4 Set Germany POSIX Timezone

```http
POST http://192.168.1.102/write
Content-Type: application/json

{
  "state": {
    "TZ": "CET-1CEST,M3.5.0,M10.5.0/3"
  }
}
```

The setting takes effect immediately, but the device may not echo the same `TZ` value back.

### 7.5 Enable Local Self-Consumption Mode with Shelly Pro 3EM

```http
POST http://192.168.1.102/write
Content-Type: application/json
```

Write the following values under `state`:

| Field | Value |
| --- | --- |
| `MM` | `1` |
| `MD` | `{"mode":"mdns","mdns":{"sn":"8c4f00c31844","dat_url":"http://0.0.0.0/rpc/EM.GetStatus?id\u003d0"},"dat_str":{"pwr":"total_act_power"}}` |

`MD` takes effect immediately, but the device may not echo the same value back. Confirm success through `MS` and live meter data.

### 7.6 Restart the Device

```http
POST http://192.168.1.102/write
Content-Type: application/json

{
  "state": {
    "RT": 1
  }
}
```

## 8. Integration Notes

- Always use `/read` as the source of truth after every write.
- For `MD` and `TZ`, confirm the result by the resulting effect. Do not rely on those fields as guaranteed direct echo values.
- For normal monitoring, `2s ~ 5s` polling is usually reasonable. For short-term write confirmation, `1s ~ 2s` can be used temporarily.
- Avoid mixing unrelated actions in the same `/write` request, especially `RT` together with configuration updates.
- If a Home Assistant zero feed-in automation blueprint controls the device, keep the device's local zero feed-in / Local Self-Consumption Mode (`MM`) disabled. The blueprint follows Home Assistant meter entities and Home Assistant automation logic, while `MM` + `MD` lets the device read the configured local meter directly.
- If you need to support multiple firmware branches, implement only against the stable core fields defined in this document. Do not assume undocumented fields are always present.
