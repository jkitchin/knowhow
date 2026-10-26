# Notify Done Hook

Send desktop notifications when Claude Code stops and is waiting for user input.

## Overview

| Field | Value |
|-------|-------|
| Name | `notify-done` |
| Event | `Stop` |
| Type | `command` |
| Timeout | 10 seconds |

## Purpose

Get notified when Claude Code finishes a task and needs your attention. This is especially useful when:

- Running long operations while working in another window
- Waiting for Claude to complete a complex task
- Working in a multi-monitor setup where Claude might not be visible

The notification appears when:
- Claude completes a task and is waiting for input
- Claude encounters an error and needs guidance
- A long-running operation finishes

## Platform Support

The hook automatically detects your platform and uses the appropriate notification system.

### Linux

Uses `notify-send` (libnotify).

#### Installation

```bash
# Debian/Ubuntu
sudo apt install libnotify-bin

# Fedora
sudo dnf install libnotify

# Arch Linux
sudo pacman -S libnotify

# openSUSE
sudo zypper install libnotify-tools
```

#### Features
- Supports urgency levels (low, normal, critical)
- Optional sound hints
- Works with most desktop environments (GNOME, KDE, XFCE, etc.)

### macOS

Uses `osascript` (AppleScript) - no additional installation required.

The hook uses the built-in macOS notification system, which:
- Appears in Notification Center
- Respects Do Not Disturb settings
- Works with all macOS versions

### Windows (WSL)

Uses PowerShell notifications. Works out of the box with WSL.

The hook attempts to use:
1. **BurntToast** module (if installed) - provides richer notifications
2. **Native Windows Toast** - fallback using Windows.UI.Notifications

#### Optional: Install BurntToast for Enhanced Notifications

```powershell
# In PowerShell (not WSL)
Install-Module -Name BurntToast
```

## Configuration

Customize notifications with environment variables:

```bash
# Custom notification title (default: "Claude Code")
export NOTIFY_DONE_TITLE="Claude Code"

# Enable notification sound - Linux only (default: false)
export NOTIFY_DONE_SOUND="true"

# Notification urgency - Linux only (default: normal)
# Options: low, normal, critical
export NOTIFY_DONE_URGENCY="normal"
```

### Environment Variables

| Variable | Default | Platforms | Description |
|----------|---------|-----------|-------------|
| `NOTIFY_DONE_TITLE` | `Claude Code` | All | Notification title |
| `NOTIFY_DONE_SOUND` | `false` | Linux | Play notification sound |
| `NOTIFY_DONE_URGENCY` | `normal` | Linux | Urgency level |

## Behavior

1. Triggered when Claude stops (Stop event)
2. Extracts project name from current working directory
3. Detects operating system:
   - Checks for WSL on Linux
   - Uses platform-appropriate notification method
4. Sends notification with project context
5. Exits 0 (never blocks)

### Notification Message

The notification includes context about your project:

```
Title: Claude Code
Message: Ready for input in myproject
```

If the project directory cannot be determined, a generic message is shown:

```
Title: Claude Code
Message: Claude is waiting for your input
```

## Requirements

### Linux
- `libnotify` / `notify-send` command

### macOS
- None (uses built-in osascript)

### Windows/WSL
- PowerShell available (default in WSL)
- Optional: BurntToast PowerShell module

## Installation

```bash
knowhow hooks install notify-done
```

## Notes

- **Non-blocking**: Fire-and-forget notification
- **Graceful fallback**: If notification tools aren't available, fails silently
- **Platform-aware**: Automatically uses the right notification system
- **WSL-aware**: Detects WSL and uses Windows notifications
- **Fast**: Short timeout prevents delays

## Troubleshooting

### Notifications Not Appearing

#### Linux
1. Check if notify-send is installed: `which notify-send`
2. Test manually: `notify-send "Test" "Hello"`
3. Check notification daemon is running
4. Verify Do Not Disturb is off

#### macOS
1. Test manually: `osascript -e 'display notification "Test" with title "Test"'`
2. Check Notification Center settings
3. Verify Claude Code/Terminal app has notification permissions

#### Windows/WSL
1. Test PowerShell access: `powershell.exe -Command "echo hello"`
2. Check Windows notification settings
3. Try installing BurntToast for better compatibility

### Notifications Delayed

The hook has a 10-second timeout. If notifications are slow:
- Check system load
- Verify notification service is responsive
- Consider disabling sound effects

### Wrong Project Name

The hook extracts the project name from the current working directory (`cwd`). If it shows the wrong name:
- Check that Claude Code is running in the correct directory
- The name comes from the last component of the path

## Combining with Other Hooks

The notify-done hook works well with:

- **lab-notebook**: Get notified when session ends, then review the notebook entry
- **bash-logger**: Notification alerts you to check the command log

```bash
knowhow hooks install notify-done
knowhow hooks install lab-notebook
```

## Advanced Usage

### Custom Notification Script

For more control, create a custom hook that wraps notify-done:

```python
#!/usr/bin/env python3
import os
import subprocess
import sys

# Your custom logic here
project = os.path.basename(os.getcwd())
duration = calculate_session_duration()  # Your function

message = f"Completed in {project} after {duration}"

# Call appropriate notifier
if sys.platform == "darwin":
    subprocess.run(["osascript", "-e", f'display notification "{message}" with title "Claude Done"'])
```

### Integration with Other Tools

```bash
# Send to Slack (example)
export NOTIFY_DONE_WEBHOOK="https://hooks.slack.com/..."

# Then in a custom hook, post to webhook when done
```
