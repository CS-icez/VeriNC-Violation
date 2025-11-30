echo 'root hard nofile 1024000' >> /etc/security/limits.conf
echo 'root soft nofile 1024000' >> /etc/security/limits.conf
echo source /opt/netcache/scripts/global.sh >> /root/.bashrc
echo 'export PROJ_DIR=/opt/netcache' >> /root/.bashrc
echo 'export LOG_DIR=/root/netcache/log' >> /root/.bashrc
