# -*- coding: UTF-8 -*-
# Install Tasks for useSharedComputers
# https://github.com/nvaccess/nvda/issues/4093
# https://github.com/nvaccess/nvda/pull/7506/files
# Copyright (C) 2018 Noelia Ruiz Martínez, Robert Hänggi 
# Released under GPL 2
import ui
from  config import conf
numLockByLayoutDefault="0" if conf["keyboard"]["keyboardLayout"]=="desktop" else "2"
confspec = {
	"numLockActivationChoice": "integer(default="+numLockByLayoutDefault+")",
	"volumeCorrectionChoice": "integer(default=0)",
	"volumeLevel": "integer(0, 100, default = 50)"
}

def onInstall():
	try:
		conf.spec.pop("useSharedComputers")
	except:
		pass
	for profile in conf.profiles:
		try:
			profile.pop("useSharedComputers")
		except Exception as e:
			ui.message(str(e))
	conf.spec["sharedComputer"] = confspec