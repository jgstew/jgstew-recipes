
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
RUN apt-get update && apt-get install -y curl git python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN git clone https://github.com/jgstew/autopkg.git
WORKDIR /tmp/autopkg
RUN git checkout dev
RUN pip3 install --requirement requirements.txt --quiet

WORKDIR /
COPY requirements.txt /tmp/
RUN pip3 install --requirement /tmp/requirements.txt --quiet
RUN rm -f /tmp/requirements.txt

# create empty autopkg config
RUN mkdir -p ~/.config/Autopkg
# create config if it does not exist
RUN echo {} > ~/.config/Autopkg/config.json

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
