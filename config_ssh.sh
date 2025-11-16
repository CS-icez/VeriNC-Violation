#!/bin/bash
mkdir -p /run /root/.ssh
service ssh start
cp $PROJ_DIR/ssh_config /root/.ssh/config
sleep 5
ssh-keygen -t ed25519 -N '' -f /root/.ssh/id_ed25519
sshpass -p root ssh-copy-id -i /root/.ssh/id_ed25519.pub dl11
sshpass -p root ssh-copy-id -i /root/.ssh/id_ed25519.pub dl20
sshpass -p root ssh-copy-id -i /root/.ssh/id_ed25519.pub dl21
sshpass -p root ssh-copy-id -i /root/.ssh/id_ed25519.pub dl30
sshpass -p onl ssh-copy-id -i /root/.ssh/id_ed25519.pub bf3
