# -*- coding: UTF-8 -*-
# numLockManager: Plugin to manage the numLock key
# https://github.com/nvaccess/nvda/issues/4093
# Copyright (C) 2018 Noelia Ruiz Martínez
# Released under GPL 2

import globalPluginHandler
import winUser
from keyboardHandler import KeyboardInputGesture

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		if winUser.getKeyState(winUser.VK_NUMLOCK) == 1:
			KeyboardInputGesture.fromName("numLock").send()
