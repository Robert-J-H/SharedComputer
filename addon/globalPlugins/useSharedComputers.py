# -*- coding: UTF-8 -*-
# useSharedComputers: Plugin to using shared computers
# https://github.com/nvaccess/nvda/issues/4093
# https://github.com/nvaccess/nvda/pull/7506/files
# Copyright (C) 2018 Noelia Ruiz Martínez
# Released under GPL 2

import globalPluginHandler
import addonHandler
import wx
import gui
from gui import guiHelper
from gui import nvdaControls
from gui.settingsDialogs import SettingsDialog
import config
import winUser
from keyboardHandler import KeyboardInputGesture
from globalCommands import SCRCAT_CONFIG

addonHandler.initTranslation()

confspec = {
	"activation": "integer(default=0)",
	"changeVolumeLevel": "boolean(default=False)",
	"volumeLevel": "integer(default=50)"
}
config.conf.spec["useSharedComputers"] = confspec

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def handleConfigProfileSwitch(self):
		activation = config.conf["numLockManager"]["activation"]
		if activation < 2 and winUser.getKeyState(winUser.VK_NUMLOCK) != activation:
			KeyboardInputGesture.fromName("numLock").send()

	def changeVolumeLevel(self, volumeLevel):
		from comtypes.client import CreateObject
		wSObj = CreateObject("wScript.Shell")
		# (174=volume down, 175=volume up, 173= mute)
		wSObj.SendKeys('{'+chr(174) + ' ' + '100' + '}')
		wSObj.SendKeys('{'+chr(175) + ' ' + str(volumeLevel) + '}')

	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		volLevel = config.conf["useSharedComputers"]["volumeLevel"]
		if config.conf["useSharedComputers"]["changeVolumeLevel"]:
			# We use wx.CallAfter() so that NVDA can speak messages
			wx.CallAfter(self.changeVolumeLevel, volLevel)
		self.numLockState = winUser.getKeyState(winUser.VK_NUMLOCK)
		self.handleConfigProfileSwitch()
		try:
			config.configProfileSwitched.register(self.handleConfigProfileSwitch)
		except AttributeError:
			pass

		# Gui
		self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
		self.settingsItem = self.prefsMenu.Append(wx.ID_ANY,
			# Translators: name of the option in the menu.
			_("&Use Shared Computers settings..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, self.settingsItem)

	def terminate(self):
		if winUser.getKeyState(winUser.VK_NUMLOCK) != self.numLockState:
			KeyboardInputGesture.fromName("numLock").send()
		try:
			config.configProfileSwitched.unregister(self.handleConfigProfileSwitch)
		except AttributeError: # This is for backward compatibility
			pass
		try:
			self.prefsMenu.RemoveItem(self.settingsItem)
		except: # Compatible with Python 2 and 3
			pass

	def onSettings(self, evt):
		gui.mainFrame._popupSettingsDialog(AddonSettingsDialog)

	def script_settings(self, gesture):
		wx.CallAfter(self.onSettings, None)
	script_settings.category = SCRCAT_CONFIG
	# Translators: message presented in input mode.
	script_settings.__doc__ = _("Shows the Use Shared Computers settings dialog.")

class AddonSettingsDialog(SettingsDialog):

# Translators: Title of a dialog.
	title = _("Use Shared Computers settings")

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Label of a dialog.
		activateLabel = _("&Activate NumLock:")
		self.activateChoices = (_("off"), _("on"), _("not changed"))
		self.activateList = sHelper.addLabeledControl(activateLabel, wx.Choice, choices=self.activateChoices)

		self.activateList.Selection = config.conf["useSharedComputers"]["activation"]

		# Translators: label of a dialog.
		self.changeVolumeLevelCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("&Change volume level")))
		self.changeVolumeLevelCheckBox.Value = config.conf["useSharedComputers"]["changeVolumeLevel"]
		self.changeVolumeLevelCheckBox.Enabled = (config.conf.profiles[-1].name is None)
		# Translators: Label of a dialog.
		self.volumeLevel = sHelper.addLabeledControl(_("Volume level:"), nvdaControls.SelectOnFocusSpinCtrl,
			min=0, max=100, initial=config.conf["useSharedComputers"]["volumeLevel"])
		self.volumeLevel.Enabled = (config.conf.profiles[-1].name is None)

	def postInit(self):
		self.activateList.SetFocus()

	def onOk(self,evt):
		super(AddonSettingsDialog, self).onOk(evt)
		config.conf["useSharedComputers"]["activation"] = self.activateList.Selection
		config.conf["useSharedComputers"]["changeVolumeLevel"] = self.changeVolumeLevelCheckBox.Value
		config.conf["useSharedComputers"]["volumeLevel"] = self.volumeLevel.Value
