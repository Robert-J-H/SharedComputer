# -*- coding: UTF-8 -*-
# numLockManager: Plugin to manage the numLock key
# https://github.com/nvaccess/nvda/issues/4093
# Copyright (C) 2018 Noelia Ruiz Martínez
# Released under GPL 2

import globalPluginHandler
import addonHandler
import wx
import gui
from gui import guiHelper
from gui.settingsDialogs import SettingsDialog
import config
import winUser
from keyboardHandler import KeyboardInputGesture
from globalCommands import SCRCAT_CONFIG

confspec = {
	"activation": "integer(default=0)"
}
config.conf.spec["numLockManager"] = confspec

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def handleConfigProfileSwitch(self):
		activation = config.conf["numLockManager"]["activation"]
		if activation < 2 and winUser.getKeyState(winUser.VK_NUMLOCK) != activation:
			KeyboardInputGesture.fromName("numLock").send()

	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
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
			_("&NumLock Manager settings..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, self.settingsItem)

	def terminate(self):
		if winUser.getKeyState(winUser.VK_NUMLOCK) != self.numLockState:
			KeyboardInputGesture.fromName("numLock").send()
		try:
			config.configProfileSwitched.unregister(self.handleConfigProfileSwitch)
		except AttributeError:
			pass
		try:
			self.prefsMenu.RemoveItem(self.settingsItem)
		except:
			pass

	def onSettings(self, evt):
		gui.mainFrame._popupSettingsDialog(AddonSettingsDialog)

	def script_settings(self, gesture):
		wx.CallAfter(self.onSettings, None)
	script_settings.category = SCRCAT_CONFIG
	# Translators: message presented in input mode.
	script_settings.__doc__ = _("Shows the NumLock Manager settings dialog.")

class AddonSettingsDialog(SettingsDialog):

# Translators: Title of the NumLockManagerDialog.
	title = _("NumLockManager settings")

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: The label for a setting in NumLockManagerDialog.
		activateLabel = _("&Activate NumLock:")
		self.activateChoices = (_("off"), _("on"), _("not changed"))
		self.activateList = sHelper.addLabeledControl(activateLabel, wx.Choice, choices=self.activateChoices)
		self.activateList.Selection = config.conf["numLockManager"]["activation"]

	def postInit(self):
		self.activateList.SetFocus()

	def onOk(self,evt):
		super(AddonSettingsDialog, self).onOk(evt)
		config.conf["numLockManager"]["activation"] = self.activateList.GetSelection()
