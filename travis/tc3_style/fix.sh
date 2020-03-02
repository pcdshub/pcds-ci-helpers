#!/bin/bash

./files.sh | xargs sed -i -e 's/\t/    /g'
./files.sh | xargs sed -i -e 's/\s\+$//g'
./files.sh | xargs sed -i '/LineId/d'
