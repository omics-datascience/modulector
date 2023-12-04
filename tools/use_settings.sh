#!/bin/bash

case $1 in
	"dev")
		cp -vf $BASEDIR/ModulectorBackend/settings_dev.py $BASEDIR/ModulectorBackend/settings.py
		;;
	"prod")
		cp -vf $BASEDIR/ModulectorBackend/settings_prod.py $BASEDIR/ModulectorBackend/settings.py
		;;
	"ci")
		cp -vf $BASEDIR/ModulectorBackend/settings_ci.py $BASEDIR/ModulectorBackend/settings.py
		;;
esac
