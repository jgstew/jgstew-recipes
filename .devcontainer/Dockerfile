# See here for image contents: https://github.com/microsoft/vscode-dev-containers/blob/v0.202.3/containers/python-3/.devcontainer/base.Dockerfile
# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT=3.10-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# https://stackoverflow.com/a/72378273/861745
# [Optional] Allow the vscode user to pip install globally w/o sudo
#ENV PIP_TARGET=/usr/local/pip-global
ENV PYTHONPATH=/usr/local/pip-global:${PYTHONPATH}
ENV PATH=/usr/local/pip-global/bin:${PATH}
RUN if ! cat /etc/group | grep -e "^pip-global:" > /dev/null 2>&1; then groupadd -r pip-global; fi \
    && usermod -a -G pip-global vscode \
    && umask 0002 && mkdir -p /usr/local/pip-global \
    && chown :pip-global /usr/local/pip-global \
    && ( [ ! -f "/etc/profile.d/00-restore-env.sh" ] || sed -i -e "s/export PATH=/export PATH=\/usr\/local\/pip-global:/" /etc/profile.d/00-restore-env.sh )

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends python-dev-is-python3 speech-dispatcher libcairo2-dev libmagic-dev jq p7zip-full msitools curl git wget python3 python3-pip build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev

# update python basics
RUN sudo pip3 install --upgrade pip
RUN sudo pip3 install --upgrade setuptools wheel build

RUN mkdir /workspaces
RUN mkdir -p /home/vscode/Library/AutoPkg
RUN mkdir -p /home/vscode/.config/Autopkg

RUN echo {} > /home/vscode/.config/Autopkg/config.json

# setup autopkg:
RUN cd /workspaces && git clone https://github.com/autopkg/autopkg.git
RUN cd /workspaces/autopkg && git checkout dev
# install requirements for autopkg dev branch:
RUN cd /workspaces/autopkg && sudo pip3 --disable-pip-version-check --no-cache-dir install --requirement gh_actions_requirements.txt

# install requirements for jgstew-recipes:
RUN sudo pip3 --disable-pip-version-check --no-cache-dir install besapi bigfix_prefetch cairosvg certifi chevron generate_bes_from_template hachoir icoextract jsonpath_ng looseversion olefile pefile Pillow pre-commit python-magic signify validate_bes_xml

RUN python3 /workspaces/autopkg/Code/autopkg repo-add hansen-m-recipes homebysix-recipes https://github.com/jgstew/jgstew-recipes.git

# add alias for autopkg for vscode user:
RUN echo 'alias autopkg="python3 /workspaces/autopkg/Code/autopkg"' >> /home/vscode/.bashrc

# in case you run this as root / a regular docker container:
RUN echo 'alias autopkg="python3 /workspaces/autopkg/Code/autopkg"' >> /root/.bashrc

RUN chown -R vscode /workspaces
RUN chown -R vscode /home/vscode

# # [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#     && rm -rf /tmp/pip-tmp

# RUN for line in $(cat /tmp/.autopkg_repos.txt); do python3 /tmp/autopkg/Code/autopkg repo-add $line; done
