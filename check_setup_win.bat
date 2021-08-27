@echo off
REM This script should be invoked with CMD
REM This script will not work properly if invoked with CMD from Git Bash
REM This script checks autopkg setup and development on Windows
echo.

echo.
echo Python location:
where python

REM check python install
echo.
echo Python Version:  (Python for Windows)
python --version
REM check pip install (generally included in python install)
echo.
echo Pip Version:  (Python for Windows)
pip --version
REM check GIT install
echo.
echo GIT Version:  (GIT for Windows)
git --version

REM check ssh-keygen.exe exists:
if exist "%ProgramFiles%\Git\usr\bin\ssh-keygen.exe" (
    REM file exists
) else (
    REM file doesn't exist
    echo ERROR: "C:\Program Files\Git\usr\bin\ssh-keygen.exe" is missing
    echo.
    echo  - Did you install GIT for Windows? -
    echo.
    pause
    REM exit 2
)

REM check SSH keys (ssh-keygen included with GIT, but must be run)
REM must generate SSH keys
REM must copy public key to github
echo.
echo check ssh keys exist: (~\.ssh\id_rsa.pub)
if exist %UserProfile%\.ssh\id_rsa.pub (
    REM file exists
    echo    ~\.ssh\id_rsa.pub file found!
) else (
    REM file doesn't exist
    echo ERROR: ~\.ssh\id_rsa.pub missing!
    echo RUN: cmd /C "C:\Program Files\Git\usr\bin\ssh-keygen.exe"
    echo          to generate ~\.ssh\id_rsa.pub
    echo          NOTE: just hit enter at "Enter file in which to save the key (/c/Users/_USER_/.ssh/id_rsa):" prompt
    echo      then copy the contents of ~\.ssh\id_rsa.pub to your GitHub account SSH keys at https://github.com/settings/keys
    pause
    REM exit 3
)

echo.
REM https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/testing-your-ssh-connection
REM https://stackoverflow.com/a/28469910/861745
echo Test SSH connection to GitHub:
echo ssh -T -o StrictHostKeyChecking=no git@github.com
ssh -T -o StrictHostKeyChecking=no git@github.com
if errorlevel 1 (
    echo   - ssh test succeeded!  exit code: %errorlevel%
) else if errorlevel 0 (
    echo   - ssh test succeeded!  exit code: %errorlevel%
) else (
    echo ERROR: ssh test failed!  exit code: %errorlevel%
    echo   - Have you copied ssh keys to your github account?
    echo.
    type %UserProfile%\.ssh\id_rsa.pub
    echo.
    REM copy public key to clipboard? powershell -c [Windows.Forms.Clipboard]::SetText(???)
    pause
    REM exit %errorlevel%
)


REM check if autopkg config file exists
REM %UserProfile%\AppData\Local\AutoPkg\config.json
echo.
if exist %UserProfile%\AppData\Local\Autopkg\config.json (
    REM file exists
    echo Autopkg config found:
    type %UserProfile%\AppData\Local\Autopkg\config.json
    echo.
) else (
    REM file doesn't exist
    if not exist %UserProfile%\AppData\Local\Autopkg (
        REM autopkg folder doesn't exist
        echo creating missing Autopkg user config folder
        mkdir %UserProfile%\AppData\Local\Autopkg
        echo.
    )
    echo Autopkg config does not exist
    echo  creating blank Autopkg config
    echo {} > %UserProfile%\AppData\Local\Autopkg\config.json
)

REM TODO: check visual studio build tools
REM VSWhere check:
REM   .\vswhere.exe -all -legacy -products * -format json
REM WMI Relevance check:
REM   selects "* from MSFT_VSInstance" of wmis
REM Install Powershell VSSetup module
REM   powershell -ExecutionPolicy Bypass -command "Import-Module PowerShellGet ; Install-Module VSSetup -Scope CurrentUser -AcceptLicense -Confirm ; Get-VSSetupInstance"
REM   powershell -ExecutionPolicy Bypass -command "Import-Module PowerShellGet ; Install-Module VSSetup -Scope CurrentUser -AcceptLicense -Confirm ; (Get-VSSetupInstance | Select-VSSetupInstance -Product *).packages"
REM Install command:
REM   vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
REM Relevance to generate relevance for folder check:
REM   ("number of unique values of preceding texts of firsts %22,%22 of names of folders whose(name of it starts with %22" & it & "%22) of folders %22Microsoft\VisualStudio\Packages%22 of /* ProgramData */ csidl folders 35") of concatenations "%22 OR name of it starts with %22" of tuple string items of "Microsoft.VisualCpp.Redist.14, Microsoft.PythonTools.BuildCore, Microsoft.VisualStudio.Workload.MSBuildTools, Microsoft.VisualStudio.Workload.VCTools, Win10SDK"
REM Relevance to detect required vsbuildtools are missing:
REM   5 != number of unique values of preceding texts of firsts "," of names of folders whose(name of it starts with "Microsoft.VisualCpp.Redist.14.Latest" OR name of it starts with "Microsoft.PythonTools.BuildCore" OR name of it starts with "Microsoft.VisualStudio.Workload.MSBuildTools" OR name of it starts with "Microsoft.VisualStudio.Workload.VCTools" OR name of it starts with "Win10SDK") of folders "Microsoft\VisualStudio\Packages" of /* ProgramData */ csidl folders 35
REM distutils.errors.DistutilsPlatformError: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
REM ParentFolder: C:\ProgramData\Microsoft\VisualStudio\Packages\
REM   SubFolders:
REM     Microsoft.VisualCpp.Redist.14*
REM     Microsoft.Build*
REM     Microsoft.PythonTools.BuildCore*
REM     Microsoft.VisualStudio.PackageGroup.VC.Tools*
REM     Microsoft.VisualStudio.Workload.MSBuildTools*
REM     Microsoft.VisualStudio.Workload.VCTools*
REM     Win10SDK*
if not exist %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.VisualCpp.Redist.14* (
    REM folder missing
    echo.
    echo ERROR: missing required Visual Studio Build Tools - Required for Python Pip installs
    echo ERROR: missing folder %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.VisualCpp.Redist.14*
    echo Install Command:
    echo   vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    echo.
    pause
    exit 9
)
if not exist %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.Build* (
    REM folder missing
    echo.
    echo ERROR: missing required Visual Studio Build Tools - Required for Python Pip installs
    echo ERROR: missing folder %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.Build*
    echo Install Command:
    echo   vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    echo.
    pause
    exit 9
)
if not exist %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.PythonTools.BuildCore* (
    REM folder missing
    echo.
    echo ERROR: missing required Visual Studio Build Tools - Required for Python Pip installs
    echo ERROR: missing folder %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.PythonTools.BuildCore*
    echo Install Command:
    echo   vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    echo.
    pause
    exit 9
)
if not exist %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.VisualStudio.PackageGroup.VC.Tools* (
    REM folder missing
    echo.
    echo ERROR: missing required Visual Studio Build Tools - Required for Python Pip installs
    echo ERROR: missing folder %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.VisualStudio.PackageGroup.VC.Tools*
    echo Install Command:
    echo   vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    echo.
    pause
    exit 9
)
if not exist %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.VisualStudio.Workload.MSBuildTools* (
    REM folder missing
    echo.
    echo ERROR: missing required Visual Studio Build Tools - Required for Python Pip installs
    echo ERROR: missing folder %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.VisualStudio.Workload.MSBuildTools*
    echo Install Command:
    echo   vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    echo.
    pause
    exit 9
)
if not exist %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.VisualStudio.Workload.VCTools* (
    REM folder missing
    echo.
    echo ERROR: missing required Visual Studio Build Tools - Required for Python Pip installs
    echo ERROR: missing folder %ProgramData%\Microsoft\VisualStudio\Packages\Microsoft.VisualStudio.Workload.VCTools*
    echo Install Command:
    echo   vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    echo.
    pause
    exit 9
)
if not exist %ProgramData%\Microsoft\VisualStudio\Packages\Win10SDK* (
    REM folder missing
    echo.
    echo ERROR: missing required Visual Studio Build Tools - Required for Python Pip installs
    echo ERROR: missing folder %ProgramData%\Microsoft\VisualStudio\Packages\Win10SDK*
    echo Install Command:
    echo   vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    echo.
    pause
    exit 9
)

echo.
echo Upgrade pip:
echo python -m pip install --upgrade pip
python -m pip install --upgrade pip

echo.
echo NOTE: The following should be run from within the cloned git "recipes" folder:
if exist .git (
    echo .git folder found
    echo.
) else (
    echo ERROR: .git folder not found!
    echo Are you running this from the cloned git "recipes" folder?
    echo NOTE: this error is expected if you are running this script independantly
    echo         to check intial setup. You should later run this from a cloned repo.
    pause
    exit 99
)

echo Update Current Repo:
echo git pull
git pull

echo.
echo check pip install requirements for cloned recipes:
echo pip install -r .\requirements.txt --quiet --quiet
pip install -r .\requirements.txt --quiet --quiet
if errorlevel 0 (
    echo   - pip install for recipes succeeded!  exit code: %errorlevel%
) else (
    echo ERROR: pip install for recipes failed! exit code: %errorlevel%
    echo   - Have you installed visual studio build tools?
    echo vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    pause
    exit %errorlevel%
)
REM https://stackoverflow.com/a/334890/861745

echo.
echo besapi python module version:
echo python -c "import besapi ; print(besapi.__version__)"
python -c "import besapi ; print(besapi.__version__)"

echo.
echo Check if besapi config file exists:
REM %UserProfile%\.besapi.conf
if exist %UserProfile%\.besapi.conf (
    REM file exists
    echo ~\.besapi.conf file found!
    echo.
    echo Test besapi config and login:
    python -m besapi ls quit
) else (
    echo ERROR: ~\.besapi.conf file does not exist!
    echo  copying blank besapi config
    echo copy _setup\.besapi.conf %UserProfile%\.besapi.conf
    copy _setup\.besapi.conf %UserProfile%\.besapi.conf
)

echo.
echo Check for ..\autopkg git repo folder:
if not exist ..\autopkg (
    echo ERROR: autopkg git folder missing!
    REM TODO: Consider attempt at automatic fix with the following:
    REM CMD /C "cd .. && git clone https://github.com/jgstew/autopkg.git"
    pause
    exit 4
) else (
    echo ..\autopkg folder found!
)

echo.
echo check autopkg on dev branch:
echo CMD /C "cd ..\autopkg && git checkout dev"
CMD /C "cd ..\autopkg && git checkout dev"

echo.
echo update autopkg repo:
echo CMD /C "cd ..\autopkg && git pull"
CMD /C "cd ..\autopkg && git pull"

echo.
echo check pip install requirements for AutoPkg:
echo pip install -r ..\autopkg\requirements.txt --quiet --quiet
pip install -r ..\autopkg\requirements.txt --quiet --quiet
if errorlevel 0 (
    echo   - pip install for autopkg succeeded!  exit code: %errorlevel%
) else (
    echo ERROR: pip install for autopkg failed!  exit code: %errorlevel%
    echo   - Have you installed visual studio build tools?
    echo vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    pause
    exit %errorlevel%
)

echo.
echo AutoPkg Version Check: (WARNINGS are expected on Windows)
REM this is assuming you ran check_setup_win.bat from within the recipes folder and that Autopkg is in a sibling folder
echo python ..\autopkg\Code\autopkg version
python ..\autopkg\Code\autopkg version
echo      --- AutoPkg version (expected 2.3 or later)

echo.
echo Add/Update jgstew-recipes to AutoPkg
echo python ..\autopkg\Code\autopkg repo-add https://github.com/jgstew/jgstew-recipes
python ..\autopkg\Code\autopkg repo-add https://github.com/jgstew/jgstew-recipes

REM add pre-commit:
pre-commit install --install-hooks --allow-missing-config

echo.
echo Check the _setup folder for other items
echo.
pause
