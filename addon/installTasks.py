# -*- coding: UTF-8 -*-
# Install Tasks for useSharedComputers
# https://github.com/nvaccess/nvda/issues/4093
# https://github.com/nvaccess/nvda/pull/7506/files
# Copyright (C) 2018 Noelia Ruiz Martínez, Robert Hänggi 
# Released under GPL 2

import config

def onInstall():
	confspec = {
		"activation": "integer(default=0)",
		"changeVolumeLevel": "integer(default=0)",
		"volumeLevel": "integer(default=50)"
	}
	config.conf.spec["useSharedComputers"] = confspec
	# Check for previous version where 
	# changeVolumeLevel was a boolean
	if config.conf["useSharedComputers"].isSet("changeVolumeLevel"):
		volMode=config.conf["useSharedComputers"].__getitem__("changeVolumeLevel",checkValidity=False)
		if not  isinstance(volMode, int):
			# makes False 0 and True 1
			config.conf.profiles[0]["useSharedComputers"]["changeVolumeLevel"] = int(eval(volMode))
