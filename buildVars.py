# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x : x

# Add-on information variables
addon_info = {
	# for previously unpublished addons, please follow the community guidelines at:
	# https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
	# add-on Name, internal for nvda
	"addon_name" : "useSharedComputers",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown on installation and add-on information.
	"addon_summary" : _("Use Shared Computers"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-ons manager
	"addon_description" : _("""Adds the possibility of choosing the state of the numLock key at start or when changing configuration profiles.
	Additionally, the Windows  master volume can be set, either as a minimum or as an absolute percentage.
	This ensures that the user hears the screen reader even if the volume has previously been muted or turned to a low level.
	It will be applied  on the next start of NVDA."""),
	# version
	"addon_version" : "1.2-dev",
	# Author(s)
	"addon_author" : u"Noelia Ruiz Martínez <nrm1977@gmail.com>, Robert Hänggi <aarjay.robert@gmail.com>",
	# URL for the add-on documentation support
	"addon_url" : "https://github.com/Robert-J-H/UseSharedComputers.git",
	# Documentation file name
	"addon_docFileName" : "readme.html",
}


import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = [os.path.join("addon", "globalPlugins", "*.py")]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []
