cp /home/abc/netlock/experiments/set-env.sh /root/set-env.sh
service ssh start
mkdir -p /root/.ssh
cp /home/abc/netlock/ssh_config /root/.ssh/config
sleep 5
bash -c "ssh-keyscan -p 22 172.20.20.11 >> /root/.ssh/known_hosts"
bash -c "ssh-keyscan -p 22 172.20.20.12 >> /root/.ssh/known_hosts"
bash -c "ssh-keyscan -p 22 172.20.20.13 >> /root/.ssh/known_hosts"
bash -c "ssh-keyscan -p 22 172.20.20.14 >> /root/.ssh/known_hosts"
bash -c "ssh-keyscan -p 22 172.20.20.100 >> /root/.ssh/known_hosts"
ssh-keygen -t ed25519 -N '' -f /root/.ssh/id_ed25519
sshpass -p root ssh-copy-id -i /root/.ssh/id_ed25519.pub worker1
sshpass -p root ssh-copy-id -i /root/.ssh/id_ed25519.pub worker2
sshpass -p root ssh-copy-id -i /root/.ssh/id_ed25519.pub worker3
sshpass -p root ssh-copy-id -i /root/.ssh/id_ed25519.pub worker4
sshpass -p onl ssh-copy-id -i /root/.ssh/id_ed25519.pub tofino
