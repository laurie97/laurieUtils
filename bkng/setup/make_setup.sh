### A script to build a default setup script and add alias
## Inputs

location=`pwd`
fullName=$1
shortName="s_"$2

setup_name="setup_"$2".sh"

echo
echo "make_setup.sh:  I want to make project '$fullName' in '$location' with a alias name '$shortName'"
while true; do
    read -p "make_setup.sh:  Is this ok? (yes/no/maybe)  " yn
    case $yn in
	[Yy]* ) echo; echo "  **** Ok let's go! ***"; echo; break;;
	[Nn]* ) echo "make_setup.sh: I'll take that as a no"; echo; exit;;
	[Mm]* ) echo "make_setup.sh: You can't actually answer 'maybe' to a machine, I can't make decisions for you!"; echo; continue;;
	* ) echo "make_setup.sh: Please answer yes/no/maybe!"; echo; continue;;
    esac
    done
echo

echo "make_setup.sh: Creating alias...." 
echo "alias "${shortName}"='source "${location}"/${setup_name}'" >> ~/.bash_profile
echo 'echo "'${shortName}' = Go to '$fullName'"' >> ~/.list_aliases.sh
echo
echo "make_setup.sh: Creating setup script...."

#### This is the default setup scriot
echo 'echo "*****************************************"' > ${location}/${setup_name}
echo 'echo "**** Welcome to '${fullName}' ('$shortName') ****"' >> ${location}/${setup_name}
echo 'echo "*****************************************"'>> ${location}/${setup_name}
echo 'echo'>> ${location}/${setup_name}
echo 'echo "Where am I?"'>> ${location}/${setup_name}
echo 'local='${location} >> ${location}/${setup_name}
echo 'cd $local;'>> ${location}/${setup_name}
echo '## cur_setup'>> ${location}/${setup_name}
echo 'export CURRENT='$location'; echo $CURRENT'>> ${location}/${setup_name}
echo 'echo'>> ${location}/${setup_name}
echo 'echo "Loading aliases..."'>> ${location}/${setup_name}
echo '#### Here are the aliases'>> ${location}/${setup_name}
echo '#'>> ${location}/${setup_name}
echo 'alias test="echo THIS IS HOW TO WRITE A ALIAS"'>> ${location}/${setup_name}
echo 'echo " - test (Template to write lovely aliases)"'>> ${location}/${setup_name}
echo ''>> ${location}/${setup_name}
echo 'echo'>> ${location}/${setup_name}
echo 'Done!'
echo 
echo
echo 'Loading setup script....'
source ~/.bash_profile
source ${location}/${setup_name}
echo "make_setup.sh: Done!!"
echo
