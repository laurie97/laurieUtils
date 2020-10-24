#!/bin/bash
 
SCRIPTPATH=`pwd`/04_schedule_plot_experiment_data.sh
echo "04_schedule_plot_experiment_data.sh: $SCRIPTPATH"
echo
BASEDIR=$(dirname $SCRIPTPATH)
cd "$BASEDIR"
 
#### RUN SCRIPT ####
##
##  put your commands her
if [ `klist 2>&1 | grep -i 'No credentials' | wc -l` -gt 0 ]; then
    echo "04_schedule_plot_experiment_data.sh: No Credentials Found - Cannot Run PyScript right now"
else
    case 
echo "04_schedule_plot_experiment_data.sh: Found credential"
    echo "04_schedule_plot_experiment_data.sh: Running ./03_plot_experiment_data.py"
    echo
    ./03_plot_experiment_data.py
    echo
    echo "04_schedule_plot_experiment_data.sh: Sucessful"
fi
##
#### END RUN SCRIPT ####
 
## reschedule the run for tomorrow ##
echo "04_schedule_plot_experiment_data.sh: Will try to run 03_plot_experiment_data.py @ 11:00 tomorrow"
at -f "$SCRIPTPATH" 11:00
