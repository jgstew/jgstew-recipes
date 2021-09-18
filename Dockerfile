
FROM ubuntu:latest

# MAINTAINER is deprecated, but I don't know how else to set the `AUTHOR` metadata
MAINTAINER james@jgstew.com

# Labels.
LABEL maintainer="james@jgstew.com"

# https://medium.com/@chamilad/lets-make-your-docker-image-better-than-90-of-existing-ones-8b1e5de950d
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.name="jgstew/jgstew-recipes"
LABEL org.label-schema.description="Run jgstew-recipes using AutoPkg on Ubuntu:latest"
LABEL org.label-schema.url="https://github.com/jgstew/jgstew-recipes"
LABEL org.label-schema.vcs-url="https://github.com/jgstew/jgstew-recipes"
LABEL org.label-schema.docker.cmd="docker run --rm jgstewrecipes run -vv com.github.jgstew.test.DateTimeFromString"

# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
RUN apt-get update && apt-get install -y curl git python3 python3-pip && rm -rf /var/lib/apt/lists/*

# create empty autopkg config
RUN mkdir -p ~/.config/Autopkg
RUN echo {} > ~/.config/Autopkg/config.json

RUN git clone https://github.com/jgstew/autopkg.git
WORKDIR /autopkg
RUN git checkout dev
RUN pip3 install --requirement requirements.txt --quiet
WORKDIR /

COPY requirements.txt /tmp/
RUN pip3 install --requirement /tmp/requirements.txt --quiet

RUN python3 ../autopkg/Code/autopkg repo-add hansen-m-recipes
RUN python3 ../autopkg/Code/autopkg repo-add https://github.com/jgstew/jgstew-recipes

COPY . /recipes
WORKDIR /recipes
ENTRYPOINT ["python3", "../autopkg/Code/autopkg"]
CMD ["help"]
