# HomeWorthAI
nosu ai hackathon

# Intalling virtual environment

### Commands

python3 -m venv venv
source venv/bin/activate
export MACOSX_DEPLOYMENT_TARGET=10.13
source /Users/avnoorludhar/Desktop/computer\ sceince/HackathonForInsurance/HomeWorthAI/backend/venv/bin/activate
/Applications/Python\ 3.11/Install\ Certificates.command


# Installing detectron2
> **Note:** We are installing for the CPU, install CUDA if you want GPU support.
### Step 1
First install py torch
`pip install torch`
verify installation by running
`python -c "import torch; print(torch.__version__)"`
This will output the PyTorch version, confirming that it's installed correctly. (you might need to install numpy)

### Step 2
install [Detectron2](https://detectron2.readthedocs.io/en/latest/tutorials/install.html)
install required dependencies (make sure to install [git](git-scm.com))
```
pip install -U pip setuptools wheel
pip install cython
pip install 'git+https://github.com/facebookresearch/detectron2.git'
```

