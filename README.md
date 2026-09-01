# Edge Debloat (and Bing Remover)

This is a collection of tweaks and settings I've been using for sometime now, to make using Edge less annoying, especially by:
- Removing Bing search engine and forcing Google;
- Preventing Edge from becoming the default browser and asking for it all the time.

## AI Usage?
Yes, Gemini 3.1 Pro helped me organize and bring parity between the Windows and macOS tweaks I've gathered over time.
How:
- Consolidation, correction, automation and organization of the tweaks for both operating systems.
- Creation of the python scripts for Bing Search Removal (both Windows and macOS).
- The features and instructions in this README.md file below the following 3 horizontal lines were AI-generated following my instructions and edited as needed.

# Disclaimer

I am **not** responsible for any damage caused by the use of these scripts.

Use them at your own risk.

**Review carefully!**

---
---
---

# 1. Bing Search Removal

Python scripts for both Windows and macOS. No additional packages needed (uses only standard libraries). Python 3.7 or newer is required.

## Features

Removes the Bing engine from the "search bar" by directly editing Edge's `Web Data` SQLite database file, across **all Edge profiles** (`Default`, `Profile 1`, `Profile 2`, ...).

First, it creates a consistent backup of each profile database (`Web Data.backup_<timestamp>` next to the original, via SQLite's online backup API), and then executes a SQL command to delete any search engine entries from the `keywords` table where the URL contains `bing.com` or the keyword contains `bing`.

The scripts exit with code `0` on success and `1` on failure, so they can also be used from automation.

## Bing Search Removal HOWTO

Run `nuke_bing_win.py` on Windows, or `nuke_bing_mac.py` on macOS (double-click, or from a terminal). Close Edge first if you can.

Notes:
- The scripts import the shared `nuke_bing_lib.py` from the repository root, so keep the folder layout as-is.
- Every run leaves a `Web Data.backup_<timestamp>` file inside each profile folder; delete old backups manually once you are happy with the result.

# 2. Edge Debloat

Windows (registry) and macOS (property list).

## Edge Debloat Features

**1. Disables AI, Copilot, & Bing Features**
* Disables Copilot and its ability to read page context.
* Removes Bing Chat from the New Tab Page.
* Disables AI features in history and text fields.
* Hides the Microsoft 365 Copilot chat icon.
* Prevents the downloading of local AI foundation models.

**2. Cleans Up the New Tab Page & Interface**
* Removes the news feed and articles from the New Tab Page.
* Hides the default quick links/top sites on the New Tab Page.
* Disables the Edge Sidebar completely.
* Disables the Edge desktop widget.
* Disables the "Collections" feature.

**3. Stops Telemetry, Background Services & Limits Cache**
* Stops sending optional diagnostic data and browsing history for personalization.
* Enables the "Do Not Track" web request header.
* Stops sending failed URL navigation data to Microsoft.
* Disables network prediction (prefetching pages) to save bandwidth and improve privacy.
* Stops Edge from running in the background when closed (Startup Boost).
* Limits the maximum disk cache size to 256MB to prevent storage bloat.
* **Allows User DNS Configuration**: Explicitly clears DNS policies (such as DNS-over-HTTPS and built-in DNS client locks) to ensure that the secure DNS settings remain configurable in Edge's privacy settings UI.

**4. Removes Shopping, Rewards, & Ads/Promotions**
* Disables the built-in shopping and coupon assistant.
* Hides Microsoft Rewards integration.
* Disables browser recommendations.
* Disables the pop-ups asking to set Edge as the default browser.
* Hides the Adobe Acrobat subscription button in the PDF viewer.
* Stops promotions for the Edge Insider program.

**5. Sets Google as Default Search**
* Forces the address bar search engine to be Google instead of Bing.

## Edge Debloat HOWTO
### Windows: edge_debloat.reg

This is a Windows Registry script that applies group policies to `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Edge`.

* Simply double-click the `edge_debloat.reg` file and click "Yes" when prompted to merge it into your registry.
* Restart Edge for the changes to take effect.

### macOS: com.microsoft.Edge.plist

The `plist` file contains the same enterprise policies as the Windows `.reg` file above. Applying it replaces any previous custom Edge policy settings.

* Recommended (Terminal): `defaults import com.microsoft.Edge /path/to/com.microsoft.Edge.plist` — this writes the policies and refreshes the macOS preferences cache in one step.
* Alternative: copy the file to `~/Library/Preferences/` (overwriting the existing one), then run `killall cfprefsd` in Terminal so macOS re-reads the file.
* If secure DNS settings were previously locked by policy, also clear the cached DNS policies explicitly:
  ```bash
  defaults delete com.microsoft.Edge DnsOverHttpsMode
  defaults delete com.microsoft.Edge DnsOverHttpsTemplates
  defaults delete com.microsoft.Edge BuiltInDnsClientEnabled
  ```
* Restart Edge for the changes to take effect.
