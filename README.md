# HomeWorthAI
nosu ai hackathon



# Backend

## Making a virtual environment
Make a virtual environment using python3: 
> make sure to be in backend folder
`python3 -m venv venv`, to activate using Windows `venv\Scripts\activate`, then install dependencies `pip install -r requirements.txt`

## Installing detectron2
> **Note:** We are installing for the CPU, install CUDA if you want GPU support. Also make sure to change `cfg.MODEL.DEVICE = "cpu"` in backend > controllers > decetron2.py
### Step 1
First install py torch
`pip install torch`
verify installation by running
`python -c "import torch; print(torch.__version__)"`
This will output the PyTorch version, confirming that it's installed correctly. (you might need to install numpy)

### Step 2
install [Detectron2](https://detectron2.readthedocs.io/en/latest/tutorials/install.html)
install required dependencies (make sure to install [git](git-scm.com) to install detectron2)
```
pip install -U pip setuptools wheel
pip install cython
pip install 'git+https://github.com/facebookresearch/detectron2.git'
```
> For Windows make sure to install MS build tools

