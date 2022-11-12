
REM create powershell profile file

if exist %UserProfile%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1 (
    REM file exists
    echo powershell profile found:
    type %UserProfile%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
    echo.
) else (
    REM file doesn't exist
    if not exist %UserProfile%\Documents\WindowsPowerShell (
        REM folder doesn't exist
        echo creating missing Autopkg user config folder
        mkdir %UserProfile%\Documents\WindowsPowerShell
        echo.
    )
    echo  creating blank powershell profile
    echo "" > %UserProfile%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
)

REM install chocolatey
powershell -ExecutionPolicy Bypass -command "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

call C:\ProgramData\chocolatey\bin\RefreshEnv.cmd

echo install visual studio code
choco install -y vscode

echo install windows WindowsTerminal 
choco install -y microsoft-windows-terminal

echo install git
REM https://github.com/chocolatey-community/chocolatey-packages/blob/master/automatic/git.install/ARGUMENTS.md
choco install -y git.install --params "'/GitAndUnixToolsOnPath /WindowsTerminal /NoGuiHereIntegration /WindowsTerminalProfile /Editor:VisualStudioCode /DefaultBranchName:main'"

echo install visualstudio2019-workload-vctools
choco install visualstudio2019-workload-vctools -y

call C:\ProgramData\chocolatey\bin\RefreshEnv.cmd

echo install python 3.10.x
REM https://docs.python.org/3/using/windows.html#installing-without-ui
choco install -y python --version="3.10.8" --install-arguments="'InstallAllUsers=1 PrependPath=1 CompileAll=1'"

call C:\ProgramData\chocolatey\bin\RefreshEnv.cmd

echo stop here!
exit


@REM echo update pip
@REM python -m pip install --upgrade pip

@REM echo update related python modules
@REM pip install --upgrade setuptools build wheel

@REM echo create UserProfile\_Code folder if missing:
@REM if not exist %UserProfile%\_Code (
@REM     REM folder doesn't exist
@REM     echo creating missing Autopkg user config folder
@REM     mkdir %UserProfile%\_Code
@REM     echo.
@REM )

@REM cd %UserProfile%\_Code

@REM git clone https://github.com/jgstew/jgstew-recipes.git

