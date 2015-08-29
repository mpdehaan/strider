#!/bin/bash
SUDOERS_FILE=/etc/sudoers.d/strider-init-requiretty
echo "Defaults:ec2-user !requiretty" > $SUDOERS_FILE
echo "Defaults:root !requiretty" >> $SUDOERS_FILE
chmod 440 $SUDOERS_FILE

