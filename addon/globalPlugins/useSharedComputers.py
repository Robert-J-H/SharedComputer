# -*- coding: UTF-8 -*-
# useSharedComputers: Plugin to using shared computers
# https://github.com/nvaccess/nvda/issues/4093
# https://github.com/nvaccess/nvda/pull/7506/files
# Copyright (C) 2018 Noelia Ruiz Martínez, Robert Hänggi 
# Released under GPL 2

import globalPluginHandler
import addonHandler
import gui, wx, time, tones, winUser, config
from gui import guiHelper
from gui import nvdaControls
from gui.settingsDialogs import SettingsDialog
from keyboardHandler import KeyboardInputGesture
from globalCommands import SCRCAT_CONFIG
from comtypes import HRESULT,GUID,IUnknown, COMMETHOD, POINTER, CoCreateInstance, cast, c_float
from ctypes.wintypes import BOOL, DWORD, UINT 
from logHandler import log
from api import processPendingEvents
addonHandler.initTranslation()

confspec = {
	"activation": "integer(default=0)",
	"changeVolumeLevel": "boolean(default=False)",
	"volumeLevel": "integer(default=50)"
}
config.conf.spec["useSharedComputers"] = confspec

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def handleConfigProfileSwitch(self):
		activation = config.conf["useSharedComputers"]["activation"]
		if activation < 2 and winUser.getKeyState(winUser.VK_NUMLOCK) != activation:
			KeyboardInputGesture.fromName("numLock").send()

	def changeVolumeLevel(self, volumeLevel):
		speakers=getVolumeObject()
		if speakers is not None:
			# should actually work on first attempt
			# but level 0 is a pain
			# to do: level 0 and mute at the same time is for some reason not recognizable
			for attempt in range(2):
				processPendingEvents()
				level=int(speakers.GetMasterVolumeLevelScalar()*100)
				log.info("Level Speakers at Startup: {} Percent".format(level))
				if level<volumeLevel:
					speakers.SetMasterVolumeLevelScalar(volumeLevel/100.0,None)
				muteState= speakers.GetMute()
				log.info("Speakers at Startup: {}".format(("Unmuted","Muted")[muteState]))
				if muteState:
					speakers.SetMute(0, None)
				time.sleep(0.05)
				log.info("Speakers after correction: {} Percent, {}".format(
					int(speakers.GetMasterVolumeLevelScalar()*100),
					("Unmuted","Muted")[speakers.GetMute()]))
		else:
			# As a fall-back, change the volume "manually"
			volDown=KeyboardInputGesture.fromName("VolumeDown")
			volUp=KeyboardInputGesture.fromName("VolumeUp")
			# one keystroke = 2 % here, is that universal?
			repeats=volumeLevel//2
			# We are only interested in the side effect, hence the dummy underscore variable
			_ = {key.send() for key in iter((volDown,)*repeats + (volUp,)*repeats)}
			time.sleep(float(volumeLevel)/62)

	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		volLevel = config.conf["useSharedComputers"]["volumeLevel"]
		if config.conf["useSharedComputers"]["changeVolumeLevel"]:
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

# Audio Stuff
def getVolumeObject():
	CLSID_MMDeviceEnumerator = GUID('{BCDE0395-E52F-467C-8E3D-C4579291692E}')
	deviceEnumerator = CoCreateInstance(CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, 1)
	volObj = cast(
		deviceEnumerator.GetDefaultAudioEndpoint(0, 1).Activate(IAudioEndpointVolume._iid_, 7, None),
		POINTER(IAudioEndpointVolume))
	return volObj

# for a ffull-fletched Audio wrapper
# visit https://github.com/AndreMiras/pycaw
class IAudioEndpointVolume(IUnknown):
	_iid_ = GUID('{5CDF2C82-841E-4546-9722-0CF74078229A}')
	_methods_ = (
		COMMETHOD([], HRESULT, 'NotImpl1'),
		COMMETHOD([], HRESULT, 'NotImpl2'),
		COMMETHOD([], HRESULT, 'GetChannelCount', (['out'], POINTER(UINT), 'pnChannelCount')),
		COMMETHOD([], HRESULT, 'SetMasterVolumeLevel',
			(['in'], c_float, 'fLevelDB'), (['in'], POINTER(GUID), 'pguidEventContext')),
		COMMETHOD([], HRESULT, 'SetMasterVolumeLevelScalar',
			(['in'], c_float, 'fLevel'), (['in'], POINTER(GUID), 'pguidEventContext')),
		COMMETHOD([], HRESULT, 'GetMasterVolumeLevel', (['out'], POINTER(c_float), 'pfLevelDB')),
		COMMETHOD([], HRESULT, 'GetMasterVolumeLevelScalar', (['out'], POINTER(c_float), 'pfLevelDB')),
		COMMETHOD([], HRESULT, 'SetChannelVolumeLevel',
			(['in'], UINT, 'nChannel'), (['in'], c_float, 'fLevelDB'), (['in'], POINTER(GUID), 'pguidEventContext')),
		COMMETHOD([], HRESULT, 'SetChannelVolumeLevelScalar',
			(['in'], DWORD, 'nChannel'), (['in'], c_float, 'fLevelDB'), (['in'], POINTER(GUID), 'pguidEventContext')),
		COMMETHOD([], HRESULT, 'GetChannelVolumeLevel',
			(['in'], UINT, 'nChannel'),
			(['out'], POINTER(c_float), 'pfLevelDB')),
		COMMETHOD([], HRESULT, 'GetChannelVolumeLevelScalar',
			(['in'], DWORD, 'nChannel'),
			(['out'], POINTER(c_float), 'pfLevelDB')),
		COMMETHOD([], HRESULT, 'SetMute', (['in'], BOOL, 'bMute'), (['in'], POINTER(GUID), 'pguidEventContext')),
		COMMETHOD([], HRESULT, 'GetMute', (['out'], POINTER(BOOL), 'pbMute')),
		COMMETHOD([], HRESULT, 'GetVolumeStepInfo',
			(['out'], POINTER(DWORD), 'pnStep'),
			(['out'], POINTER(DWORD), 'pnStepCount')),
		COMMETHOD([], HRESULT, 'VolumeStepUp', (['in'], POINTER(GUID), 'pguidEventContext')),
		COMMETHOD([], HRESULT, 'VolumeStepDown', (['in'], POINTER(GUID), 'pguidEventContext')),
		COMMETHOD([], HRESULT, 'QueryHardwareSupport', (['out'], POINTER(DWORD), 'pdwHardwareSupportMask')),
		COMMETHOD([], HRESULT, 'GetVolumeRange',
			(['out'], POINTER(c_float), 'pfMin'),
			(['out'], POINTER(c_float), 'pfMax'),
			(['out'], POINTER(c_float), 'pfIncr')))

class IMMDevice(IUnknown):
	_iid_ = GUID('{D666063F-1587-4E43-81F1-B948E807363F}')
	_methods_ = (
		COMMETHOD([], HRESULT, 'Activate',
			(['in'], POINTER(GUID), 'iid'),
			(['in'], DWORD, 'dwClsCtx'),
			(['in'], POINTER(DWORD), 'pActivationParams'),
			(['out'], POINTER(POINTER(IUnknown)), 'ppInterface')),)

class IMMDeviceCollection(IUnknown):
	_iid_ = GUID('{0BD7A1BE-7A1A-44DB-8397-CC5392387B5E}')
	_methods_ = (
		COMMETHOD([], HRESULT, 'GetCount',
			(['out'], POINTER(UINT), 'pcDevices')),
		COMMETHOD([], HRESULT, 'Item',
			(['in'], UINT, 'nDevice'),
			(['out'], POINTER(POINTER(IMMDevice)), 'ppDevice')))

class IMMDeviceEnumerator(IUnknown):
	_iid_ = GUID('{A95664D2-9614-4F35-A746-DE8DB63617E6}')
	_methods_ = (
		COMMETHOD([], HRESULT, 'EnumAudioEndpoints',
			(['in'], DWORD, 'dataFlow'),
			(['in'], DWORD, 'dwStateMask'),
			(['out'], POINTER(POINTER(IMMDeviceCollection)), 'ppDevices')),
		COMMETHOD([], HRESULT, 'GetDefaultAudioEndpoint',
			(['in'], DWORD, 'dataFlow'),
			(['in'], DWORD, 'role'),
			(['out'], POINTER(POINTER(IMMDevice)), 'ppDevices')),)