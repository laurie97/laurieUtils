## Files
qs_dir="/c/Users/lmcclymont/Programming/git_laurie/ifa-analyses/quick_starter"
jt_dir="${qs_dir}/jupyter_templates"
jt_pandas_and_plot="${jt_dir}/jupyter_template__pandas_and_plot.ipynb"
jt_django="${jt_dir}/jupyter_template__django_pandas_and_plot.ipynb"


f_dir="${qs_dir}/functions"
f_pandas="${f_dir}/laurie_pandas_functions.py"
f_plotting="${f_dir}/laurie_plotting_functions.py"
f_django="${f_dir}/laurie_django_functions.py"

## Aliases
echo '## Quick starts aliases'
echo '- cp_jt_pandas_and_plot: Jupyter template'
alias cp_jt_pandas_and_plot='cp ${jt_pandas_and_plot}'
echo '- cp_jt_django: Jupyter template w Django'
alias cp_jt_django='cp ${jt_django}'
echo '- cp_f_pandas: Functions for Pandas'
alias cp_f_pandas='cp ${f_pandas}'
echo '- cp_f_plotting: Functions for plotting'
alias cp_f_plotting='cp ${f_plotting}'
echo '- cp_f_django: Functions for IfATE Django'
alias cp_f_django='cp ${f_django}'
