# !/bin/bash
cd ./common
sudo mv sysnettool/sysnettool sysnettool_bak
sudo rm -rf sysnettool
sudo mv sysnettool_bak sysnettool
sudo chown -R sysadmin:sysadmin sysnettool