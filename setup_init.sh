#/bin/bash!

echo "Compile C files"
(cd Direction_Finder/_receiver/C && make)


echo "[ INFO ] Set file executation rights"
chmod a+x Direction_Finder/_receiver/C/rtl_daq
chmod a+x Direction_Finder/_receiver/C/sim
chmod a+x Direction_Finder/_receiver/C/sync
chmod a+x Direction_Finder/_receiver/C/gate


sudo chmod +x run.sh 
sudo chmod +x kill.sh
sudo chmod +x create_linux_desktop_icon.sh

