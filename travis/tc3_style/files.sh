#!/bin/bash

source ../settings.sh

find $TWINCAT_PROJECT_ROOT -regextype posix-extended -regex '.*\.(TcPOU|TcDUT|TcGVL)$'
