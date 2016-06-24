#!/bin/bash

logged_in_user=$(/usr/bin/stat -f%Su /dev/console)
command_to_run="/usr/bin/defaults write com.poleposition-sw.lanrev_admin AllowURLSDPackageImport -bool true"

echo "Enabling AllowURLSDPackageImport as $logged_in_user"

sudo -u $logged_in_user $command_to_run