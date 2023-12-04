#!/bin/bash
VERSION=$(grep -i VERSION: $BASEDIR/ModulectorBackend/settings.py | cut -d '=' -f2 | tr -d "' ")
echo "VERSION=$VERSION"
