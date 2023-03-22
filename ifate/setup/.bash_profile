#!/bin/bash
echo
echo "################################################"
echo "################################################"
echo "###   Hello Laurie. Welcome to your terminal ###"
echo "################################################"
echo "################################################"
echo
echo "------------------------------------------------"
echo "-------    *************************    --------"
echo "-------    => Fired up, ready to go!    --------"
echo "------------------------------------------------"
echo

## Add IfA to Path
export PATH=$PATH:Users/lmcclymont/Programming/ids/S129-Institute-Data-System
export PATH=$PATH:'/c/ProgramData/Microsoft/Windows/Start Menu/Programs/Python 3.10'
export PATH=$PATH:'~/Programming/bin/Downloads'

export PYTHONPATH='C:\\Users\\lmcclymont\\Programming\\ids\\S129-Institute-Data-System'

######## Main Code Short Cuts ###############

alias pip='python -m pip --trusted-host pypi.org --trusted-host files.pythonhosted.org --default-timeout=600'
alias grep_r='grep -Irn -e'
alias sumatra='~/Downloads/SumatraPDF-3.2-64.exe'
alias suma='sumatra'
alias jl='jupyter-lab'
alias jn='jupyter notebook &'
alias get_git_url='echo "Copying Git URL..."; git remote get-url origin | clip'
alias edit_bash_profile='emacs ~/.bash_profile &'
alias reload_bash_profile='source ~/.bash_profile'

## Quick Start Aliases
source ~/Programming/git_laurie/ifa-analyses/quick_starter/scripts/quick_start_aliases.sh

### Useful locations
export ONEDRIVE='~/OneDrive - Department for Education/'
export DL='~/OneDrive - Department for Education/Downloads/'
export DSDST_DOCS='/c/Users/lmcclymont/OneDrive - Department for Education/Documents - DSDST/'
export ALPHA_DOCS='/c/Users/lmcclymont/Department for Education/EXTERNAL - Occupational Maps Prototype Alpha - 04 Data'


######## Setup Proxy ########
alias set_proxy="export HTTP_PROXY='http://127.0.0.1:3128';export HTTPS_PROXY='https://127.0.0.1:3128';"
alias unset_proxy='unset HTTP_PROXY; unset HTTPS_PROXY;'
######## Navigation Tools ##########################
### Quick Links
alias go_dl='cd  ~/OneDrive\ -\ Department\ for\ Education/Downloads/'
alias go_docs='cd  ~/OneDrive\ -\ Department\ for\ Education/Documents/'
alias go_pres='cd ~/OneDrive\ -\ Department\ for\ Education/Presentations/'
alias go_my_dl='cd  ~/Downloads/'
alias go_ids='cd ~/Programming/ids/IfA/'
alias go_dsdst_docs='cd "${DSDST_DOCS}"'
alias go_alpha_docs='cd "${ALPHA_DOCS}"'

### Andy's hack
### Bind the up/down arrows in the linux bash terminal to search the bash command history
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

######### Setups ##############
## Load Setups
source /c/Users/lmcclymont/Programming/make_setup/load_setup_aliases.sh
## Make Setup Auto
alias make_setup='source /c/Users/lmcclymont/Programming/make_setup/make_setup.sh'
## List my Aliases
alias list_setups='source /c/Users/lmcclymont/Programming/make_setup/list_setup_aliases.sh'

### Set up a current for easy moving about
alias current_setup='export CURRENT=$(pwd); echo $CURRENT'
alias current='cd $CURRENT; echo $CURRENT'
alias cur='current'
alias cur_setup='current_setup'

######## Useful commands #######
alias new='ls -ltrd * | tail -10'

##### Set up Venvs ####
alias create_venv='source /c/Users/lmcclymont/Programming/Environments/create_env.sh'
alias venv_ids='source /c/Users/lmcclymont/Programming/Environments/venv_ids/Scripts/activate'
alias venv_ana='source /c/Users/lmcclymont/Programming/Environments/venv_ana/Scripts/activate'
alias venv_triage_tool_testing='source /c/Users/lmcclymont/Programming/Environments/venv_triage_tool_testing/Scripts/activate'
alias venv_ids_w_sc_packages='source /c/Users/lmcclymont/Programming/Environments/venv_ids_w_sc_packages/Scripts/activate'
alias venv_nlp_sentiment_analysis='source /c/Users/lmcclymont/Programming/Environments/venv_nlp_sentiment_analysis/Scripts/activate'
