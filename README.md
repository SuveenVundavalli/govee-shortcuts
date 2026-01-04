# Govee Shortcuts for Home Assistant

This custom component allows you to trigger Govee Tap-to-Run shortcuts and Dreamview snapshots as buttons in Home Assistant.

## Features
- **Automatic Discovery**: Automatically finds Govee "BaseGroup" devices (Groups/Shortcuts).
- **Scene Support**: Discovers "Snapshots" (Scenes/Dreamview) as buttons.
- **Easy Setup**: No YAML configuration required; uses the Home Assistant integration UI.
- **OpenAPI Integration**: Uses the latest Govee OpenAPI for reliability.

## Prerequisites
- A Govee API Key. You can obtain one by emailing `support@govee.com` or through the Govee Home app (Profile > Settings > Apply for API Key).
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
5. Your Govee groups and snapshots will appear as Button entities!

## Troubleshooting
If your shortcuts don't appear:
- Ensure they are created as "Tap-to-Run" or "BaseGroups" in the Govee app.
- Check the Home Assistant logs for any authentication errors.
- Ensure your API key has the necessary permissions.

## License
MIT License. See [LICENSE](LICENSE) for more details.
