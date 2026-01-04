# Govee Shortcuts for Home Assistant

This custom component exposes Govee **Tap-to-Run shortcuts**, **DIY Scenes**, and **Snapshots** (such as Dreamview/Sync settings) as simple **Button** entities in Home Assistant.

### Why this integration?
While the official Govee integration focuses on device state (on/off, brightness, color), it often lacks direct support for the complex scenes and groups created in the Govee Home app. This integration bridges that gap by allowing you to trigger your custom "Tap-to-Run" shortcuts and device-specific scenes directly via the Govee OpenAPI.

## Features
- **Automatic Discovery**: Automatically finds Govee "BaseGroup" devices (Groups/Shortcuts).
- **Comprehensive Scene Support**: Discovers "Snapshots" (Dreamview), "DIY Scenes", and "Light Scenes" as buttons.
- **Easy Setup**: No YAML configuration required; uses the Home Assistant integration UI.
- **Configurable Whitelist**: Govee returns hundreds of default hardware scenes for every device. This integration allows you to filter those out by providing specific keywords, keeping your Home Assistant dashboard clean.
- **OpenAPI Integration**: Uses the latest Govee OpenAPI for reliability.

## Prerequisites
- A Govee API Key. You can obtain one through the Govee Home app (Profile > Settings > Apply for API Key).
- Home Assistant with HACS installed.

## Installation via HACS (Recommended)
1. Open **Home Assistant**.
2. Go to **HACS** > **Integrations**.
3. Click the **three dots** in the top right corner and select **Custom repositories**.
4. Paste the repository URL: `https://github.com/SuveenVundavalli/govee-shortcuts`
5. Select **Integration** as the category and click **Add**.
6. Find the **Govee Shortcuts** integration in HACS and click **Download**.
7. **Restart Home Assistant**.

## Configuration
1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration** in the bottom right.
3. Search for **Govee Shortcuts**.
4. Enter your Govee API Key when prompted.
5. (Optional) Provide a comma-separated list of **whitelisted keywords** (e.g., `Ambient, Rainbow, Candle`). 
   - **If left blank**: All discovered scenes and shortcuts will be added.
   - **If provided**: Only scenes containing these keywords (case-insensitive) will be added.
6. Your Govee groups and snapshots will appear as Button entities!

## Troubleshooting
If your shortcuts don't appear:
- Ensure they are created as "Tap-to-Run", "DIY", or "Snapshots" in the Govee Home app.
- If you used a whitelist, ensure the keywords match the names of your scenes exactly.
- Check the Home Assistant logs for any authentication or API errors.
- Ensure your API key is active.

## License
MIT License. See [LICENSE](LICENSE) for more details.

