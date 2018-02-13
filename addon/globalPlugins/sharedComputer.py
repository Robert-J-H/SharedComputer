# -*- coding: UTF-8 -*-
# sharedComputer: Plugin to using shared computers
# https://github.com/nvaccess/nvda/issues/4093
# https://github.com/nvaccess/nvda/pull/7506/files
# Copyright (C) 2018 Noelia Ruiz Martínez, Robert Hänggi 
# Released under GPL 2

import globalPluginHandler
import addonHandler
import gui, ui, wx, winUser, config, re
from gui import guiHelper, nvdaControls
from gui.settingsDialogs import SettingsDialog
from keyboardHandler import KeyboardInputGesture
from globalCommands import SCRCAT_CONFIG
from comtypes import HRESULT,GUID,IUnknown, COMMETHOD, POINTER, CoCreateInstance, cast, c_float
from ctypes.wintypes import BOOL, DWORD, UINT 
from logHandler import log
from api import processPendingEvents

addonHandler.initTranslation()

helpPath=addonHandler.getCodeAddon().getDocFilePath()

numLockByLayoutDefault="0" if config.conf['keyboard']['keyboardLayout']=="desktop" else "2"
confspec = {
	"numLockActivationChoice": "integer(default="+numLockByLayoutDefault+")",
	"volumeCorrectionChoice": "integer(default=0)",
	"volumeLevel": "integer(0, 100, default = 50)"
}
config.conf.spec["sharedComputer"] = confspec
speakers=None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def handleConfigProfileSwitch(self):
		activation = config.conf["sharedComputer"]["numLockActivationChoice"]
		if activation < 2 and winUser.getKeyState(winUser.VK_NUMLOCK) != activation:
			KeyboardInputGesture.fromName("numLock").send()

	def changeVolumeLevel(self, targetLevel, mode):
		if speakers is not None:
			for attempt in range(2):
				processPendingEvents()
				level = int(speakers.GetMasterVolumeLevelScalar()*100+0.5)
				log.info("Level speakers at Startup: {} Percent".format(level))
				if level < targetLevel or (mode==1 and level > targetLevel):
					speakers.SetMasterVolumeLevelScalar(targetLevel/100.0,None)
				muteState = speakers.GetMute()
				log.info("speakers at Startup: {}".format(("Unmuted","Muted")[muteState]))
				if muteState:
					speakers.SetMute(0, None)
				log.info("speakers after correction: {} Percent, {}".format(
					int(speakers.GetMasterVolumeLevelScalar()*100+0.5),
					("Unmuted","Muted")[speakers.GetMute()]))

	def __init__(self):
		global speakers
		speakers=getVolumeObject()
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		volLevel = config.conf["sharedComputer"]["volumeLevel"]
		volMode = config.conf["sharedComputer"]["volumeCorrectionChoice"]
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
			# Translators: name of the entry in the preferences menu.
			_("Shared Comp&uter..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, self.settingsItem)
		# first installation: open dialog automatically
		if not config.conf["sharedComputer"].isSet("volumeCorrectionChoice"):
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
	script_settings.__doc__ = _("Shows the Shared Computer settings dialog.")

class AddonSettingsDialog(SettingsDialog):

# Translators: Title of a dialog.
	title = _("Shared Computer Settings (F1 for Context Help)")
	# Translators: title of the browsable help message
	helpTitle=_(u"Help")
	# Translators: advice on how to close the browsable help message
	hint=_(u"<p>Press escape to close this message</p>")
	lastFocus = None
	helpDict={}
	with open(helpPath,'r') as helpFile:
		help_html=helpFile.read().decode("utf8")
	sections = re.match('(.*<body>).+(<span>.+</span>).+(<span>.+</span>).*(<span>.+</span>).*(</body>.*)',
		help_html,
		flags=re.DOTALL).groups()
	del help_html

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: label of a combo box
		activateLabel = _("&Activate NumLock:")
		self.activateChoices = (
			# Translators: Choice in Activate NumLock combo box
			_("Off"), 
			# Translators: Choice in Activate NumLock combo box
			_("On"), 
			# Translators: Choice in Activate NumLock combo box
			_("Never change"))
		self.activateList = sHelper.addLabeledControl(activateLabel, wx.Choice, choices=self.activateChoices)
		self.activateList.Selection = config.conf["sharedComputer"]["numLockActivationChoice"]
		# Translators: label of a combo box
		volumeLabel = _("System &Volume at Start:")
		self.volumeChoices = ( 
			# Translators: Choice in Volume at Start combo box
			_("Ensure a minimum of"), 
			# Translators: Choice in Volume at Start combo box
			_("Set exactly to"), 
			# Translators: Choice in Volume at Start combo box
			_("Never change"))
		self.volumeList = sHelper.addLabeledControl(volumeLabel, wx.Choice, choices=self.volumeChoices)
		self.volumeList.Selection = config.conf["sharedComputer"]["volumeCorrectionChoice"]
		# Translators: Label of a spin control
		self.volumeLevel = sHelper.addLabeledControl(_("Volume &Level:"), 
			nvdaControls.SelectOnFocusSpinCtrl,
			min = 20 if self.volumeList.Selection==1 else 0, 
			initial=config.conf["sharedComputer"]["volumeLevel"])

		# several event bindings
		self.Bind(wx.EVT_ACTIVATE, self.onDialogActivate)
		self.volumeList.Bind(wx.EVT_CHOICE, self.onChoice) 
		self.volumeLevel.Bind(wx.EVT_CHAR_HOOK, self.onKey)
		for number, child in enumerate([self.activateList, self.volumeList, self.volumeLevel], 1):
			self.helpDict[child.GetId()] = u'\n'.join((self.sections[0], self.sections[number], self.hint, self.sections[4]))
			child.Bind(wx.EVT_HELP, self.onHelp)

	def onDialogActivate(self, evt):
		"Ensures that the current control will be the same after switching to another window and back"
		# store focus when the user switches to another window
		if not evt.GetActive():
			self.lastFocus=self.FindFocus()
		elif self.lastFocus:
			self.lastFocus.SetFocus()

	def onHelp(self, evt):
		helpText = self.helpDict.get(evt.GetEventObject().GetId(), None)
		if helpText:
			ui.browseableMessage(helpText, self.helpTitle, True)

	def onKey(self, evt):
		global speakers
		key = max(evt.GetUnicodeKey(), evt.GetKeyCode())
		if key== 32:
			val = int(speakers.GetMasterVolumeLevelScalar()*100+0.5)
			self.volumeLevel.SetValue(val)
			wx.CallLater(50, ui.message, str(self.volumeLevel.Value))
		elif key==366:
			self.volumeLevel.SetValue(self.volumeLevel.Value+10)
		elif key==367:
			self.volumeLevel.SetValue(self.volumeLevel.Value-10)
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
		config.conf["sharedComputer"]["numLockActivationChoice"] = self.activateList.Selection
		# write only to the normal configuration
		config.conf.profiles[0].update({"sharedComputer": {
			"volumeCorrectionChoice": self.volumeList.Selection,
			"volumeLevel": self.volumeLevel.Value}})

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