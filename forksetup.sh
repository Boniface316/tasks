#!/bin/bash

# Remove all files and directories except 'gtasks' in the current directory

shopt -s extglob
rm -rf !("gtasks") .!(".") .??*
shopt -u extglob
rm __init__.py

mv main.py __init__.py


mv gtasks/* .
rmdir gtasks

