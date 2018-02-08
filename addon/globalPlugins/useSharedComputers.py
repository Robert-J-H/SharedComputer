# -*- coding: UTF-8 -*-
# useSharedComputers: Plugin to using shared computers
# https://github.com/nvaccess/nvda/issues/4093
# https://github.com/nvaccess/nvda/pull/7506/files
# Copyright (C) 2018 Noelia Ruiz Martínez, Robert Hänggi 
# Released under GPL 2

import globalPluginHandler
import addonHandler
import gui, ui, wx, winUser, config
from gui import guiHelper, nvdaControls
from gui.settingsDialogs import SettingsDialog
from keyboardHandler import KeyboardInputGesture
from globalCommands import SCRCAT_CONFIG
from comtypes import HRESULT,GUID,IUnknown, COMMETHOD, POINTER, CoCreateInstance, cast, c_float
from ctypes.wintypes import BOOL, DWORD, UINT 
from logHandler import log
from api import processPendingEvents

addonHandler.initTranslation()
activationDefault="0" if config.conf['keyboard']['keyboardLayout']=="desktop" else "2"
confspec = {
	"activation": "integer(default="+activationDefault+")",
	"changeVolumeLevel": "integer(default=0)",
	"volumeLevel": "integer(0, 100, default = 50)"
}
config.conf.spec["useSharedComputers"] = confspec
speakers=None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def handleConfigProfileSwitch(self):
		activation = config.conf["useSharedComputers"]["activation"]
		if activation < 2 and winUser.getKeyState(winUser.VK_NUMLOCK) != activation:
			KeyboardInputGesture.fromName("numLock").send()

	def changeVolumeLevel(self, targetLevel, mode):
		if speakers is not None:
			for attempt in range(2):
				processPendingEvents()
				level = int(speakers.GetMasterVolumeLevelScalar()*100)
				log.info("Level speakers at Startup: {} Percent".format(level))
				if level < targetLevel or (mode==1 and level > targetLevel):
					speakers.SetMasterVolumeLevelScalar(targetLevel/100.0,None)
				muteState = speakers.GetMute()
				log.info("speakers at Startup: {}".format(("Unmuted","Muted")[muteState]))
				if muteState:
					speakers.SetMute(0, None)
				log.info("speakers after correction: {} Percent, {}".format(
					int(speakers.GetMasterVolumeLevelScalar()*100),
					("Unmuted","Muted")[speakers.GetMute()]))

	def __init__(self):
		global speakers
		speakers=getVolumeObject()
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		volLevel = config.conf["useSharedComputers"]["volumeLevel"]
		volMode = config.conf["useSharedComputers"]["changeVolumeLevel"]
		if volMode < 2:
			wx.CallAfter(self.changeVolumeLevel, volLevel, volMode)
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
			_("&Use Shared Computers Settings..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, self.settingsItem)
		# first installation: open dialog automatically
		if not config.conf["useSharedComputers"].isSet("changeVolumeLevel"):
			wx.CallAfter(self.onSettings, None)

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
		# Translators: label of a dialog.
		activateLabel = _("&Activate NumLock:")
		self.activateChoices = (_("Off"), _("On"), _("Never change"))
		self.activateList = sHelper.addLabeledControl(activateLabel, wx.Choice, choices=self.activateChoices)
		self.activateList.Selection = config.conf["useSharedComputers"]["activation"]
		# Translators: label of a dialog.
		volumeLabel = _("System &Volume at Start:")
		self.volumeChoices = ( _("Ensure a minimum of"), _("Set exactly to"), _("Never change"))
		self.volumeList = sHelper.addLabeledControl(volumeLabel, wx.Choice, choices=self.volumeChoices)
		self.volumeList.Selection = config.conf["useSharedComputers"]["changeVolumeLevel"]
		self.volumeList.Bind(wx.EVT_CHOICE, self.onChoice) 
		# Translators: Label of a dialog.
		self.volumeLevel = sHelper.addLabeledControl(_("Volume &Level:"), 
			nvdaControls.SelectOnFocusSpinCtrl,
			min = 20 if self.volumeList.Selection==1 else 0, 
			initial=config.conf["useSharedComputers"]["volumeLevel"])

		self.volumeLevel.Bind(wx.EVT_CHAR_HOOK, self.onKey)

	def onKey(self, evt):
		global speakers
		key=evt.GetUnicodeKey()
		if  key== 32:
			val = int(speakers.GetMasterVolumeLevelScalar()*100)
			self.volumeLevel.SetValue(val)
			wx.CallLater(50, ui.message, str(self.volumeLevel.Value))
		else:
			evt.Skip()

	def onChoice(self, evt):
		val=evt.GetSelection()
		if val==0:
			self.volumeLevel.SetRange(0, 100)
			self.volumeLevel.Enabled=True
		if val==1:
			self.volumeLevel.SetRange(20, 100)
			self.volumeLevel.Enabled=True
		if val==2:
			self.volumeLevel.Enabled=False

	def postInit(self):
		self.activateList.SetFocus()

	def onOk(self,evt):
		super(AddonSettingsDialog, self).onOk(evt)
		config.conf["useSharedComputers"]["activation"] = self.activateList.Selection
		# write only to the normal configuration
		config.conf.profiles[0]["useSharedComputers"]["changeVolumeLevel"] = self.volumeList.Selection
		config.conf.profiles[0]["useSharedComputers"]["volumeLevel"] = self.volumeLevel.Value

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