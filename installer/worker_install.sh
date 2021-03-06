#!/usr/bin/env bash
# This is the installer of the worker. 

[ -z $_AAMKS_PATH ] &&  { _AAMKS_PATH="/usr/local/aamks"; }
[ -z $_AAMKS_SERVER] && { _AAMKS_SERVER="127.0.0.1"; }

update() { #{{{
	[ -d $_AAMKS_PATH ] || { install; }
	echo
	git -C $_AAMKS_PATH pull -q
	sudo rm -rf /etc/aamksconf.json
	hostname
	echo "{ \"AAMKS_SERVER\": \"$_AAMKS_SERVER\" }"  | sudo tee /etc/aamksconf.json
	echo 
}
#}}}
install() { #{{{
	cd
	rm -rf $_AAMKS_PATH 
	sudo locale-gen en_US.UTF-8
	sudo apt-get update
	sudo apt-get --yes install git python3-pip xdg-utils unzip cmake gearman ipython3 python3-urllib3 golang libboost-python-dev libgfortran3
	sudo -H pip3 install --upgrade pip
	sudo -H pip3 install shapely scipy numpy Cython
	sudo rm -rf /etc/aamksconf.json
	echo "{ \"AAMKS_SERVER\": \"$_AAMKS_SERVER\" }"  | sudo tee /etc/aamksconf.json
	[ -d aamks ] || { git clone https://github.com/aamks/aamks; }
	sudo mv aamks $_AAMKS_PATH
	sudo chown -R $USER:$USER $_AAMKS_PATH

	# RVO2
	echo; echo; echo "Installing RVO2 (agents collisions library) ..."; echo; echo;
	cd
	[ -d Python-RVO2 ] && { git -C Python-RVO2 pull; } || { git clone https://github.com/sybrenstuvel/Python-RVO2; }
	cd Python-RVO2
	python3 setup.py build
	sudo python3 setup.py install
	cd

	# recast
	echo; echo; echo "Installing recast (path finding library, navmesh producer)..."; echo; echo;
	cd
	go get -u github.com/arl/go-detour/cmd/recast
	[ -f ~/go/bin/recast ] || { 
		echo " ~/go/bin/recast is missing. It is likely that your golang version is obsolete."; 
		echo "Perhaps the below commands can fix golang. Once you have fixed golang, you can rerun the installer.

sudo add-apt-repository ppa:longsleep/golang-backports
sudo apt update
sudo apt install golang-go
";
exit; }

	sudo mv ~/go/bin/recast /usr/local/bin
	echo "Recast should be now installed"

	# detour
	echo; echo; echo "Installing detour (path finding library, navmesh navigator) ..."; echo; echo;
	cd
	[ -d recastlib ] && { git -C recastlib pull; } || { git clone https://github.com/layzerar/recastlib.git; }
	cd recastlib
	cp -rf ./Recast\(Patched\)/Detour/ ./Recast/
	sudo python3 setup.py install
}
#}}}
print_help() { #{{{
	cat << EOF

Worker installer options:
    -i   fresh worker install from github
    -p   AAMKS_PATH (Aamks will be installed there on the worker)
    -s   AAMKS_SERVER (the worker will expect the Aamks server there)
    -u   update/inspect worker
    -h   this help;

EOF
info
	exit
} #}}}
info() { #{{{
	echo
	echo "AAMKS_PATH: $_AAMKS_PATH"
	echo "AAMKS_SERVER: $_AAMKS_SERVER"
	echo
}
#}}}
while getopts "p:s:iuh" opt #{{{
do
case $opt in
	p) _AAMKS_PATH=$OPTARG;;
	s) _AAMKS_SERVER=$OPTARG;;
	i) info; echo "Clear and install fresh Aamks worker from github. OK? Ctrl+c to cancel."; read; install; exit;;
	u) info; update; exit;;
esac
done
#}}}
print_help

