#!/bin/bash
grep -i VERSION: $BASEDIR/ModulectorBackend/settings.py | cut -d '=' -f2 | tr -d "' "
