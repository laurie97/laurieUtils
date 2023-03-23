echo "I'm going print Hello World!"
while true; do
    read -p "Is this ok? (yes/no)  " yn
    case $yn in
	[Yy]* ) echo "Ok!"; echo; break;;
	[Nn]* ) echo "make_setup.sh: I'll take that as a no"; echo; exit 0;;
	* ) echo "make_setup.sh: Please answer yes/no/maybe!"; echo; continue;;
    esac
    done
echo "Hello World"
echo
