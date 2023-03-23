person="Laurie"    ## Assign variable
adjective=$1       ## Get argument from command line
sentence="${person} is really ${adjective}"  ## Basically like f-strings

echo
if [ -z ${adjective} ]
then
    echo 'You forgot to compliment yourself'
else
    echo ${sentence}
fi
echo
