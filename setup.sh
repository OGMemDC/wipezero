#!/bin/env bash
# vim:ff=unix ts=4 ss=4 
# vim60:fdm=marker

# Install dependencies for the application
if grep -q "Ubuntu" /etc/os-release; then 
    echo "Great, you are running Ubuntu..."
    sudo apt update -y
    sudo apt upgrade -y
    sudo apt install python3 python3-{cryptography,reportlab,tk,logging-tree,argparse-addons,json5,dateutil,hashids,enum-tools,pathtools,command-runner,pip,installer,platformdirs} -y 
else
    echo "Checking for python3..."
    if not command -v python3 &>/dev/null; then 
        echo "Missing Python3..."
    fi

    echo "Checking for pip3..."
fi
