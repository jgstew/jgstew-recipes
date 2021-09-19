# jgstew-recipes

AutoPkg recipes which anyone can use from [JGStew](https://github.com/jgstew).

Where possible recipes will be in YAML format for better cross platform support at the expense of requiring AutoPkg 2.3+

## Python Requirements:

`requirements.txt` contains the python modules required for the AutoPkg processors used by this repo

Example pip command:

- `pip3 install --requirement requirements.txt`

## AutoPkg Recipe Repo Requirements:

`.autopkg_repos.txt` contains a list of recipe repos required for the recipes within this repo

Example bash command to add all listed repos:

- `for line in $(cat /tmp/.autopkg_repos.txt); do python3 ../autopkg/Code/autopkg repo-add $line; done`

## Docker:

The example `Dockerfile` in this repo sets up a working AutoPkg dev channel Docker container running on Ubuntu.

## References:

- AutoPkg for Windows Software: https://www.youtube.com/watch?v=w4WM6M89hmg
- https://github.com/homebysix/recipe-robot/issues/74
- https://github.com/autopkg/autopkg/pull/698#issuecomment-783522503
- https://github.com/autopkg/n8felton-recipes/tree/master/SharedProcessors
- https://github.com/autopkg/autopkg/wiki/Processor-Locations
- https://github.com/autopkg/recipes/blob/master/SampleSharedProcessor/SampleSharedProcessor.recipe
