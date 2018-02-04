# Use Shared Computers #
* Authors: Noelia Ruiz Martínez, Robert Hänggi
* download [development version][2]

## Introduction
This add-on is targeted at sighted and screen reader users that share a computer, for instance in computer labs.

NVDA offers a lot of commands in conjunction with the NumPad but only if NumLock is turned off.
On the other hand, sighted users often prefer "NumLock On" in order to enter numbers rapidly.
This add-on let's you decide what state NumLock should have on launching NVDA or on changing a profile.

Sighted users do also frequently mute or turn the Windows master volume down to cut off 
system sounds or the still running screen reader.
You can now make sure that the screen reader restarts with a minimal or absolute system volume level. 
The units are the same as in the task bar for the speakers icon.

## Use Shared Computers settings Dialog##

Note: You can assign a gesture to open this dialog from NVDA's menu, Preferences submenu, Input gestures dialog, Configuration category.

On first time installation, it will be opened automatically.

This dialog, found in NVDA's menu, under the Preferences submenu, provides the following options:

### NumLock Settings
#### "Activate Num Lock:"

- Off:  
  The NumLock key will be  deactivated automatically. This is the NVDA-friendly setting.  
  It's the default for desktop computers. 
- On:  
  The NumLock key will be activated automatically.
  The recommended setting if you type a lot of numbers or your keyboard layout is generally "Laptop".
- Never  change:  
  It will remain in the current state.
  This is the default for laptop layouts.

The setting will be applied each time that you start NVDA or switch to another profile.

### System Volume Settings

Note: System volume refers to the overall master volume of Windows, 
same as the speakers icon in the task bar or the leftmost setting in the volume mixer.
#### "System Volume at Start:"

- Ensure a minimum of:  
  Muted speakers will always be unmuted and the system volume will  never be less than the set value.
  However, if the volume level was higher before restart, it will be untouched.
  This is the default
- Set exactly to:  
  Muted speakers will always be unmuted.  
  The system volume will exactly be at the percentage that has been  set under "Volume Level.  
  As a precaution, levels can't be set to less than 20 percent with this option enabled.
- Never change:  
  All volume corrections, including unmuting, will be off.
  In other words, this feature will be disabled.

#### "Volume Level:"
This spin control shows the volume level in percent that is applied at the start of NVDA. 
You can either enter a value or scroll through the values with arrow up/down.
The lower limit is raised from zero to twenty percent for the option "Set exactly to".
It won't be shown if the option "Never change" has been selected in the previous combo box.

Note that these settings are saved on termination of NVDA.
This means that for instance the command "Reload add-ons" (NVDA+Control+F3) 
takes the saved settings rather than the recently set ones.
---

## Changes for 1.1 ##
Added the possibility to set Windows master volume automatically at start of NVDA

## Changes for 1.0 ##
* Initial version.

[2]: https://github.com/nvdaes/numLockManager/releases/download/1.1-dev/numLockManager-1.1-dev.nvda-addon
