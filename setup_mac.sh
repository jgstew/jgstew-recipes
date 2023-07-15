
# work in progress:
exit 1

# check xcode command line tools install:
xcode-select --print-path

# install homebrew:
NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/96362c02f64bc1270645f6cd1698dda5a4790619/install.sh)"

NONINTERACTIVE=1 brew install python@3.10 sevenzip msitools visual-studio-code

python3 -m pip install --upgrade pip 

python3 -m pip install --upgrade setuptools build wheel
