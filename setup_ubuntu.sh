#!/usr/bin/env bash

sudo apt update && sudo apt upgrade -y

sudo apt install -y p7zip-full msitools curl git wget python3 python3-pip build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev

# update python pip
python3 -m pip install --upgrade pip

# update python basics
python3 -m pip install --upgrade setuptools wheel build

# This may solve a weird issue:
python3 -m pip install -U pyasn1-modules --ignore-installed pyasn1-modules

# if autopkg does not exist
if [ ! -f  ../autopkg ] ; then
git clone https://github.com/autopkg/autopkg.git ../autopkg
fi

# install autopkg requirements
python3 -m pip install --requirement ../autopkg/new_requirements.txt

mkdir -p ~/.config/Autopkg

# if config file does not exist, create it:
if [ ! -f  ~/.config/Autopkg/config.json ] ; then
echo {} > ~/.config/Autopkg/config.json
fi

for line in $(cat .autopkg_repos.txt); do python3 ../autopkg/Code/autopkg repo-add $line; done

# install jgstew-recipes requirements:
python3 -m pip install --requirement requirements.txt

# test:
python3 autopkg/Code/autopkg run -vv Test-Recipes/AutopkgCore.test.recipe.yaml
