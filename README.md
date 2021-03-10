# jgstew-recipes

AutoPkg recipes which anyone can use from [JGStew](https://github.com/jgstew).

Where possible recipes will be in YAML format for better cross platform support at the expense of requiring AutoPkg 2.3+

## Setup:

- Requires "com.github.n8felton.shared" processors
  - `autopkg repo-add n8felton-recipes`


## Example YAML for VirusTotal:
```
- Processor: io.github.hjuutilainen.VirusTotalAnalyzer/VirusTotalAnalyzer
  Arguments:
    pathname: '%pathname%'
```

References:
- https://github.com/homebysix/recipe-robot/issues/74
- https://github.com/autopkg/autopkg/pull/698#issuecomment-783522503
- https://github.com/autopkg/n8felton-recipes/tree/master/SharedProcessors 
- https://github.com/autopkg/autopkg/wiki/Processor-Locations
- https://github.com/autopkg/recipes/blob/master/SampleSharedProcessor/SampleSharedProcessor.recipe
