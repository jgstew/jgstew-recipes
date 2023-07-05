
sudo apt update && sudo apt upgrade -y

sudo apt install -y curl git wget python3 python3-pip build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev

python3 -m pip install --upgrade pip

git clone https://github.com/autopkg/autopkg.git ../autopkg

