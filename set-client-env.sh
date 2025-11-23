echo 'root hard nofile 1024000' >> /etc/security/limits.conf
echo 'root soft nofile 1024000' >> /etc/security/limits.conf
echo source /opt/farreach/scripts/global.sh >> /root/.bashrc
