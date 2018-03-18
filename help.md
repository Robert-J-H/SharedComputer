# Shared Computer #
* Authors: Robert Hänggi, Noelia Ruiz Martínez
* Download: <a id = "devel-version" href = "https://github.com/Robert-J-H/SharedComputer/releases/latest">Development version</a>

## Introduction
This add-on is targeted at sighted and screen reader users that share a computer, for instance in computer labs. 
NVDA offers a lot of commands in conjunction with the NumPad but only if NumLock is turned off.
On the other hand, sighted users often prefer "NumLock On" in order to enter numbers.

This add-on let's you decide what state NumLock should have on launching NVDA or on changing a profile.

Sighted users do also frequently mute or turn the Windows master volume down to cut off 
system sounds or the still running screen reader.
You can now make sure that the screen reader restarts with a minimal or absolute system volume level. 
The units are the same as in the task bar for the speakers icon.

## Shared Computers settings Dialog ##

Note: You can assign a gesture to open this dialog from NVDA's menu, Preferences submenu, Input gestures dialog, Configuration category.

It has three controls and you can press F1 in any of them to display the help associated with it.  

This dialog can be found in the NVDA menu under preferences, "Shared Computer".

The following options are available:

### NumLock Settings

<div markdown="1" >

#### "Activate NumLock:"

- Off:  
  The NumLock key will be  deactivated automatically.
  This is the NVDA-friendly setting and the default for desktop computers. 
- On:  
  The NumLock key will be activated automatically.
  The recommended setting if you type a lot of numbers or your keyboard layout is generally "Laptop".
- Never  change:  
  It will remain in the current state.
  This is the default for laptop layouts.

The setting will be applied each time that you start NVDA or switch to another profile.

</div>

### System Volume Settings

Note: System volume refers to the overall master volume of Windows, 
same as the speakers icon in the task bar or the leftmost setting in the volume mixer.

<div markdown="1" >

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

</div>

<div markdown="1" >

#### "Volume Level:"
This spin control shows the volume level in percent that is applied at the start of NVDA. 
You can perform the following actions:

* Increase/decrease a value by one with Arrow Up/Down
* Increase/decrease a value by ten  with Page Up/Down
* Fetch the current Windows system volume with Space Bar (replaces old value) 
* Select a value (e.g. with Control+A)
* Overwrite a selected value

The lower limit is raised from zero to twenty percent for the option "Set exactly to".
It won't be shown if the option "Never change" has been selected in the previous combo box.

</div>

Tip: You can reload add-ons (NVDA+Control+F3) to apply e.g. the volume changes without restart.

---

## Changes for 18.057 ##

* Changed version numbering system to year.dday
* The download link of the add-on help redirects  now to the newest version rather than the installed one
* For convenience, the version number is added to the link 
* Volume levels are now correctly rounded
* Dialog popup for first installation removed
* Freshly set options are now applied on reloading add-ons 

## Changes for 1.3 ##

* Changed add-on name
* Added contextual help for all controls
* Fixed  a bug in NVDA dialogs where focus in a control wasn't restored after Window switching
* Fixed a problem with writing volume settings to normal configuration
* Fixed translation related issues
* updated readme

## Changes for 1.2 ##

* Added absolute volume level choice with 20 % lower limit
* NumLock off default only for desktop computers
* Added install tasks
* New readme and labels for GUI
* Page up/down in spin control to increase/decrease volume level by tens.
* Space bar in spin control to fetch current volume level.

## Changes for 1.1 ##

* Added the possibility to set a minimum Windows master volume automatically at start of NVDA

## Changes for 1.0 ##

* Initial version.

  <script>
   var xhr = new XMLHttpRequest();
   var placeholder = document.getElementById('devel-version');
   xhr.open("GET", "https://api.github.com/repos/Robert-J-H/SharedComputer/releases", true);
   xhr.setRequestHeader("Accept", "application/vnd.github.v3+json");
   xhr.send();
   xhr.onreadystatechange = processRequest;
   function processRequest(e) {
    if (xhr.readyState == 4) {
     if (xhr.status == 200) {
      var response = JSON.parse(xhr.responseText);
      var releases = response.sort(function(a, b) {
        a = new Date(a.assets[0].updated_at);
        b = new Date(b.assets[0].updated_at);
        return b<a ? -1 : a<b ? 1 : 0;
      });
      placeholder.textContent = "Development version " + releases[0].tag_name;
      placeholder.href = releases[0].assets[0].browser_download_url;
     }
    }
  }
  </script>