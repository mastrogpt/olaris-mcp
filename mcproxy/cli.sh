export PATH=$HOME/.ops/*-*/bin:$PATH
set -a
ops -config -d | grep OPSDEV_ >_src
export OPS_PWD=$PWD
source _src
source $HOME/.wskprops
uv run ipython

