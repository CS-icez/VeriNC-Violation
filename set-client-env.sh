echo 'root hard nofile 1024000' >> /etc/security/limits.conf
echo 'root soft nofile 1024000' >> /etc/security/limits.conf
echo source /opt/farreach/scripts/global.sh >> /root/.bashrc
echo 'export PROJ_DIR=/opt/farreach' >> /root/.bashrc
echo 'export LOG_DIR=/root/farreach/log' >> /root/.bashrc
