
# work in progress:
exit 1

# check xcode command line tools install:
xcode-select --print-path

# install homebrew:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/96362c02f64bc1270645f6cd1698dda5a4790619/install.sh)"

brew install -y python3.10 vscode sevenzip msitools

python3 -m pip install --upgrade pip 

python3 -m pip install --upgrade setuptools build wheel
