# SunEnergyXT 500 Series

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

## Language / Sprache

- [Deutsch](README.md) (default)
- [English](README.en.md)

## Introduction

SunEnergyXT 500 Series is a custom integration for Home Assistant. It lets you discover, monitor, and control SunEnergyXT 500 Series AIO devices over the local network.

For the complete local API field reference, `MD` meter connection string examples, and `TZ` timezone examples, see [API.md](API.md).

## Features

- Discover devices automatically via Zeroconf, or add a device manually by IP address
- Monitor PV input, grid port power, load port power, battery level, firmware versions, and other real-time data
- Adjust common settings such as `GS`, `IS`, `MG`, `SI`, `SA`, `SO`, and `PT`
- Configure Local Mode, `MM` Local Zero Feed-in mode, `MD` Local Meter Data Format, `LFB` load priority, `LPS` off-grid output, and the `TZ` timezone field
- Restart the device from Home Assistant

## Installation

### Install via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner and select "Custom repositories"
3. Enter the repository address: https://github.com/SunEnergyXT/SunEnergyXT-500-Series
4. Select "Integration" as the category
5. Click "Add"
6. Search for "SunEnergyXT 500 Series"
7. Click "Download"
8. Restart Home Assistant

### Manual Installation

1. Download the latest [release package](https://github.com/SunEnergyXT/SunEnergyXT-500-Series/releases)
2. Extract it to the `config/custom_components/` directory
3. Make sure the final directory is `config/custom_components/sunenergyxt/`
4. Restart Home Assistant

#### Final Directory Structure Example

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

## Configuration

1. In Home Assistant, go to "Settings" > "Devices & services"
2. Click "Add Integration"
3. Search for `SunEnergyXT 500 Series`
4. Follow the setup prompts
   - If the device is discovered automatically, confirm the discovered device
   - If the device is not discovered automatically, enter the device IP address manually
5. The integration reads the device SN and model automatically. You do not need to enter the SN manually

Usage notes:

- Home Assistant and the device must be on the same local network
- If you rely on automatic discovery, make sure the network allows mDNS / Zeroconf traffic
- The `Today's PV Generation Energy` (`PD`) sensor requires control module firmware `ES 1.1.4` or later. Older firmware can continue using the integration, but may not report this sensor.
- After changing a control item, wait for the next polling cycle or read the status again to confirm the final value

## Zero Feed-in Mode Selection

Use only one zero feed-in control path at a time. Mixing the device's local meter control and the Home Assistant blueprint can make the resulting behavior difficult to predict.

| Mode | Where control runs | Meter source | When to use it |
|------|--------------------|--------------|----------------|
| Device-local zero feed-in mode (`MM` + `MD`) | On the SunEnergyXT device firmware | A meter configured directly in the device through `MD` | Use this when your meter is one of the documented device-local meter types and you want the device to read the meter directly |
| Home Assistant zero feed-in blueprint | In Home Assistant automation | Home Assistant meter entities | Use this when the meter is already available in Home Assistant, or when you need custom meter formulas, custom logic, or easier inspection of the control behavior |

Device-local zero feed-in mode currently supports only the meter categories documented in [API.md](API.md), such as Shelly 3EM, Shelly Pro 3EM, EcoTracker, and Tasmota / BitShake. Other meters are not automatically supported by the device-local mode unless they are exposed to the device in one of those documented formats.

In the SunEnergyXT app, **Smart Strategy - Local Network (WLAN)** is the app-side setup path for the same device-local function shown in the Home Assistant integration as `Local Zero Feed-in mode` (`MM`).

The official Home Assistant blueprint is maintained separately: [SunEnergyXT zero feed-in blueprint](https://github.com/SunEnergyXT/sunenergyxt-500-zero-feed-in-blueprint). When using the blueprint, keep `MM` disabled because the blueprint controls the device from Home Assistant entities instead of using the device's direct local meter-reading path.

To use the device-local path from Home Assistant, open the SunEnergyXT device in Home Assistant and save the final meter JSON from [API.md](API.md) in the `Local Meter Data Format` text entity (`MD`). In the current integration, saving a non-empty `MD` value writes `MD` and enables `Local Zero Feed-in mode` (`MM`) together. Clearing `MD` disables `MM`, while turning `MM` off also clears `MD`. `Local Meter Data Format` is the visible Home Assistant name of the `MD` meter connection field. It is a write field, not a guaranteed readback field; confirm the result through `Meter Status` (`MS`) and live meter behavior.

## Entity Description

Notes:

- The actual visible entities may vary by model, firmware version, and the number of expansion storages
- Energy counters are usually reported by the device as raw `Wh`; this integration displays them as `kWh`
- `TZ` must be a POSIX timezone string, not a country, city, or short label such as `CEST`

### Sensor

| Entity ID | Name | Unit | Description |
|-----------|------|------|-------------|
| `WS` | Wi-Fi SSID | - | Wi-Fi connection diagnostic information |
| `WR` | Wi-Fi Signal Strength | dB | Current Wi-Fi signal strength |
| `ST` | System Status | - | Device running status. Common values: `0 = Shutdown`, `1 = Standby`, `2 = Running`, `3 = Upgrading` |
| `IW` | System Total Input Power | W | Current total system input power |
| `OP` | System Total Output Power | W | Current total system output power |
| `PV` | PV Total Input Power | W | Total PV input power across all MPPT channels |
| `PV1` | PV 1 Input Power | W | MPPT channel 1 PV input power |
| `PV2` | PV 2 Input Power | W | MPPT channel 2 PV input power |
| `PV3` | PV 3 Input Power | W | MPPT channel 3 PV input power |
| `PV4` | PV 4 Input Power | W | MPPT channel 4 PV input power |
| `II1` | PV 1 Input Current | A | MPPT channel 1 input current |
| `II2` | PV 2 Input Current | A | MPPT channel 2 input current |
| `II3` | PV 3 Input Current | A | MPPT channel 3 input current |
| `II4` | PV 4 Input Current | A | MPPT channel 4 input current |
| `VP1` | PV 1 Input Voltage | V | MPPT channel 1 input voltage |
| `VP2` | PV 2 Input Voltage | V | MPPT channel 2 input voltage |
| `VP3` | PV 3 Input Voltage | V | MPPT channel 3 input voltage |
| `VP4` | PV 4 Input Voltage | V | MPPT channel 4 input voltage |
| `GP` | System Grid Port Power | W | Grid port power. A positive value usually means export/feed-in; a negative value usually means grid import or grid charging |
| `LP` | System Load Port Power | W | Current load port power |
| `BP` | System Battery Power | W | Current battery power. A positive value means charging; a negative value means discharging |
| `PD` | Today's PV Generation Energy | kWh | Today's accumulated PV generation energy. Requires control module firmware `ES 1.1.4` or later |
| `GD1` | Today's Grid Charge Energy | kWh | Today's energy charged into the system from the grid |
| `GD2` | Today's Grid Feed-in Energy | kWh | Today's energy exported to the grid through the grid port |
| `LD` | Today's Off-grid Output Energy | kWh | Today's off-grid inverter output energy |
| `SC` | System Battery Level | % | Overall system SOC |
| `SC0` | Head storage | % | SOC of the head storage |
| `SC1` | Expansion storage 1 | % | SOC of expansion storage 1 |
| `SC2` | Expansion storage 2 | % | SOC of expansion storage 2 |
| `SC3` | Expansion storage 3 | % | SOC of expansion storage 3 |
| `SC4` | Expansion storage 4 | % | SOC of expansion storage 4 |
| `SC5` | Expansion storage 5 | % | SOC of expansion storage 5 |
| `ON` | System Battery Pack Online Count | - | Number of online battery packs |
| `ES` | Firmware Version (Wi-Fi) | - | System Wi-Fi / EMS firmware version |
| `AS` | Firmware Version (AC Unit) | - | AC unit firmware version |
| `DS` | Firmware Version (DC Unit) | - | DC unit firmware version |
| `BS0` | Firmware Version (BMS 0) | - | Head storage BMS firmware version |
| `BS1` | Firmware Version (BMS 1) | - | Expansion storage 1 BMS firmware version |
| `BS2` | Firmware Version (BMS 2) | - | Expansion storage 2 BMS firmware version |
| `BS3` | Firmware Version (BMS 3) | - | Expansion storage 3 BMS firmware version |
| `BS4` | Firmware Version (BMS 4) | - | Expansion storage 4 BMS firmware version |
| `BS5` | Firmware Version (BMS 5) | - | Expansion storage 5 BMS firmware version |
| `SN` | System Host SN | - | Device serial number |
| `MS` | Meter Status | - | Local meter connection status. Common values: `0 = Unbound`, `1 = Online`, `2 = Offline`; some firmware versions may also report `3 = Requesting IP` |

### Number

| Entity ID | Name | Unit | Range | Step | Description |
|-----------|------|------|-------|------|-------------|
| `GS` | System Grid Port Power Setpoint | W | `-2400` to `2400` | `10` | Grid port power setpoint. A positive value usually means export/feed-in; a negative value usually means grid import or grid charging. The common positive upper limit is `800W` for 500 Standard and `2400W` for 500 Pro |
| `IS` | System Max Inverter Power Setpoint | W | `1` to `2400` | `10` | Maximum inverter output power setpoint |
| `MG` | Maximum Grid-Connected Output Power | W | `1` to `2400` | `1` | Maximum grid-connected output power. The upper limit is `800W` for 500 Standard and `2400W` for 500 Pro |
| `SI` | System Min Discharge SOC | % | `1` to `30` | `1` | Minimum SOC allowed for discharge in on-grid scenarios |
| `SA` | System Max Charge SOC | % | `70` to `100` | `1` | Maximum SOC allowed for charge in on-grid scenarios |
| `SO` | System Load Port Discharge Limit SOC | % | `1` to `30` | `1` | Minimum SOC allowed for discharge in off-grid / load port scenarios |
| `PT` | System Auto-Shutdown Time Setting | min | `30` to `1440` | `1` | Auto-shutdown time |

### Switch

| Entity ID | Name | Description |
|-----------|------|-------------|
| `LM` | Local mode | Local mode switch. When enabled, the device prioritizes local-side configuration |
| `MM` | Local Zero Feed-in mode | Local zero feed-in mode switch. It cannot be enabled while `MD` is empty. Turning it off also clears `MD` |
| `PM` | System Parallel Mode | Parallel mode switch. Use only when the device topology and firmware support it |
| `LFB` | Load Priority Switch | Load priority switch |
| `LPS` | Off-Grid Output Switch | Off-grid output switch |

### Text

| Entity ID | Name | Description |
|-----------|------|-------------|
| `MD` | Local Meter Data Format | Local meter connection JSON string for Local Zero Feed-in mode. Saving a non-empty value also enables `MM`; clearing it disables `MM`. Fill in the exact final device-side value shown in [API.md](API.md). It takes effect directly, but should not be used as a guaranteed readback field |
| `TZ` | System Time Zone | POSIX timezone string. For example, China can use `CST-8`; Germany with DST can use `CET-1CEST,M3.5.0,M10.5.0/3`. It takes effect directly, but should not be used as a guaranteed readback field |

### Button

| Entity ID | Name | Description |
|-----------|------|-------------|
| `RT` | System Restart | Sends a restart command to the device |

## Troubleshooting

### Device Not Found

- Make sure the device is powered on and connected to the local network
- Make sure Home Assistant and the device are on the same network segment
- If automatic discovery fails, enter the device IP address manually
- If the network blocks mDNS / Zeroconf traffic, automatic discovery may not work

### Data Update Issues

- Check whether the device network connection is stable
- Check whether `http://device-ip/read` is reachable directly
- After changing a control item, confirm the final result by reading the device state again

### Local Zero Feed-in Mode Does Not Work

- Make sure `MD` follows the exact meter-type example shown in [API.md](API.md)
- Make sure `MM` is enabled
- Check whether `MS` reports an online meter status and whether live meter data is updating
- Make sure the meter is one of the device-local meter categories documented in [API.md](API.md)
- Do not rely on `MD` itself as a guaranteed echo after writing

### Using the Home Assistant Zero Feed-in Blueprint

- If you use the Home Assistant zero feed-in automation blueprint, disable the device's `Local Zero Feed-in mode` (`MM`)
- The blueprint uses Home Assistant meter entities and Home Assistant automation logic; it does not use the device's direct local meter-reading path
- If you prefer the device's built-in local zero feed-in function, configure the meter connection on the device side instead. In that mode, the meter does not need to be connected through Home Assistant
- If your meter is not supported by the device-local `MM` + `MD` mode but is available as a Home Assistant power entity, use the blueprint path instead

### Timezone Setting Is Incorrect

- `TZ` must be a POSIX timezone string
- Do not enter `Europe/Berlin`, `UTC+1`, `CET`, or `CEST` as the final `TZ` value
- For Germany, use a DST-aware POSIX string such as `CET-1CEST,M3.5.0,M10.5.0/3`
- After changing `TZ`, confirm the resulting timezone behavior instead of expecting the exact written value to be echoed back

## Contribution

Contributions are welcome. Please submit issues or pull requests on [GitHub](https://github.com/SunEnergyXT/SunEnergyXT-500-Series).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

[releases-shield]: https://img.shields.io/github/release/SunEnergyXT/SunEnergyXT-500-Series.svg
[releases]: https://github.com/SunEnergyXT/SunEnergyXT-500-Series/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/SunEnergyXT/SunEnergyXT-500-Series.svg
[commits]: https://github.com/SunEnergyXT/SunEnergyXT-500-Series/commits/main
[license-shield]: https://img.shields.io/github/license/SunEnergyXT/SunEnergyXT-500-Series.svg
