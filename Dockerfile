
FROM ubuntu:latest

# MAINTAINER is deprecated, but I don't know how else to set the `AUTHOR` metadata
MAINTAINER james@jgstew.com

# Labels.
LABEL maintainer="james@jgstew.com"

# https://medium.com/@chamilad/lets-make-your-docker-image-better-than-90-of-existing-ones-8b1e5de950d
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.name="jgstewrecipes"
LABEL org.label-schema.description="Run jgstew-recipes using AutoPkg on Ubuntu:latest"
LABEL org.label-schema.url="https://github.com/jgstew/jgstew-recipes"
LABEL org.label-schema.vcs-url="https://github.com/jgstew/jgstew-recipes"
LABEL org.label-schema.docker.cmd="docker run --rm jgstewrecipes run -vv com.github.jgstew.test.DateTimeFromString"

# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --assume-yes libmagic-dev jq p7zip-full msitools curl git wget python3 python3-pip build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
# currently using my fork due to improvements made to URLDownloaderPython
RUN git clone https://github.com/autopkg/autopkg.git
WORKDIR /tmp/autopkg
RUN git checkout dev
RUN pip3 install --requirement gh_actions_requirements.txt --quiet

WORKDIR /
# this assumes that the repo contains a `requirements.txt` file:
COPY requirements.txt /tmp/
RUN pip3 install --requirement /tmp/requirements.txt --quiet
RUN rm -f /tmp/requirements.txt

# create empty autopkg config
RUN mkdir -p ~/.config/Autopkg
# create config if it does not exist
RUN echo {} > ~/.config/Autopkg/config.json

# this assumes that the repo contains an `.autopkg_repos.txt` file:
COPY .autopkg_repos.txt /tmp/.autopkg_repos.txt
WORKDIR /tmp/autopkg
# add AutoPkg recipe repos:
#   https://stackoverflow.com/a/19182518/861745
RUN for line in $(cat /tmp/.autopkg_repos.txt); do python3 ../autopkg/Code/autopkg repo-add $line; done
#RUN python3 ../autopkg/Code/autopkg repo-add hansen-m-recipes

COPY . /tmp/recipes
WORKDIR /tmp/recipes
ENTRYPOINT ["python3", "../autopkg/Code/autopkg"]
CMD ["help"]

# Interactive:
#   docker run --rm -it --entrypoint bash jgstewrecipes
# Run recipe from within Interactive shell
#   python3 ../autopkg/Code/autopkg run -vv com.github.jgstew.test.DateTimeFromString

# Run a specific recipe:
#   docker run --rm jgstewrecipes run -vv com.github.jgstew.test.DateTimeFromString

# run test recipes: docker run --rm jgstewrecipes run -vv --recipe-list Test-Recipes/Test-Recipes.recipelist.txt
