sudo apt update
sudo apt install python3.13-venv
sudo apt install binutils
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
sh build_exe.sh
