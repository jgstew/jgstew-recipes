#!/usr/bin/env bash

# this script is intended to setup a mac from scratch to be able to develop or build autopkg recipes

# check xcode command line tools install:
# xcode-select --print-path

# install homebrew:
if [ ! -f  /usr/local/bin/brew ] ; then
NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/96362c02f64bc1270645f6cd1698dda5a4790619/install.sh)"
fi

NONINTERACTIVE=1 brew tap microsoft/git

NONINTERACTIVE=1 brew install --adopt python@3.10 sevenzip msitools visual-studio-code libmagic jq git-credential-manager-core

python3 -m pip install --upgrade pip

python3 -m pip install --upgrade setuptools build wheel

# if autopkg does not exist
if [ ! -f  ../autopkg ] ; then
git clone https://github.com/autopkg/autopkg.git ../autopkg
fi

# install autopkg requirements
python3 -m pip install --requirement ../autopkg/gh_actions_requirements.txt

# add required recipe repos for jgstew-recipes
for line in $(cat .autopkg_repos.txt); do python3 ../autopkg/Code/autopkg repo-add $line; done

# install jgstew-recipes requirements:
python3 -m pip install --requirement requirements.txt
