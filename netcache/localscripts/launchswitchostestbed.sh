DIRNAME="netcache"

set -e

# NOTE: you need to launch spine/leaf switch data plane before running this script under su account

echo "clear tmp files"
rm -f tmp_switchos.out
rm -f tmp_popserver.out
rm -f tmp_cleaner.out

echo "configure data plane"
cd tofino; bash configure.sh; cd ..
sleep 1s

echo "launch switchos"
nohup ./switchos >tmp_switchos.out 2>&1 &

echo "launch ptfserver"
cd tofino; nohup bash ptf_popserver.sh >../tmp_popserver.out 2>&1 &
sleep 1s
cd ..
# cd tofino; nohup bash ptf_cleaner.sh >../tmp_cleaner.out 2>&1 &
# sleep 1s
# cd ..
