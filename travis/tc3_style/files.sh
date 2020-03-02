#!/bin/bash

source $CI_HELPER_PATH/travis/settings.sh

find $TWINCAT_PROJECT_ROOT -regextype posix-extended -regex '.*\.(TcPOU|TcDUT|TcGVL)$'
