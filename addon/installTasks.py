# -*- coding: UTF-8 -*-
# Install Tasks for useSharedComputers
# https://github.com/nvaccess/nvda/issues/4093
# https://github.com/nvaccess/nvda/pull/7506/files
# Copyright (C) 2018 Noelia Ruiz Martínez, Robert Hänggi 
# Released under GPL 2

from  config import conf

def onInstall():
	confspec = {
		"activation": "integer(default=0)",
		"changeVolumeLevel": "integer(default=0)",
		"volumeLevel": "integer(default=50)"
	}
	conf.spec["useSharedComputers"] = confspec
	# Check for previous version where 
	# changeVolumeLevel was a boolean
	if conf["useSharedComputers"].isSet("changeVolumeLevel"):
		volMode=conf["useSharedComputers"].__getitem__("changeVolumeLevel",checkValidity=False)
		if not  isinstance(volMode, int):
			# makes False 0 and True 1
			conf.profiles[0]["useSharedComputers"]["changeVolumeLevel"] = int(eval(volMode))
			# conf._writeProfileToFile(conf.profiles[0].filename, conf.profiles[0])
			# log.info("Base configuration saved after use shared computers install tasks")
