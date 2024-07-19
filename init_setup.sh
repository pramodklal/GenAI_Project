echo [$(date)]: "START"
echo [$(date)]: "Creating conda Env with python 3.9"
conda create --prefix ./env python=3.9-y
echo [$(date)]: "activate env"
source activate ./env
echo [$(date)]: "installaing requiremmets"
pip install -r requirements.txt
echo [$(date)]: "END"


