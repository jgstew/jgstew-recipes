
REM curl -O https://raw.githubusercontent.com/jgstew/jgstew-recipes/main/setup_win.bat

echo set powershell ExecutionPolicy
powershell -command "Set-ExecutionPolicy -Force -ExecutionPolicy RemoteSigned -Scope CurrentUser"

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
        echo creating missing powershell profile folder
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

@REM echo install windows WindowsTerminal
@REM choco install -y microsoft-windows-terminal

echo install git
REM https://github.com/chocolatey-community/chocolatey-packages/blob/master/automatic/git.install/ARGUMENTS.md
choco install -y git.install --params "'/GitAndUnixToolsOnPath /NoGuiHereIntegration /Editor:VisualStudioCode /DefaultBranchName:main'"

echo install visualstudio2019-workload-vctools
choco install visualstudio2019-workload-vctools -y

choco install -y 7zip

call C:\ProgramData\chocolatey\bin\RefreshEnv.cmd

echo install python 3.10.x
REM https://docs.python.org/3/using/windows.html#installing-without-ui
choco install -y python3 --version="3.10.8" --params "'/NoLockdown'" --install-arguments="'InstallAllUsers=1 PrependPath=1 CompileAll=1'"

call C:\ProgramData\chocolatey\bin\RefreshEnv.cmd

echo update pip
python -m pip install --upgrade pip

call C:\ProgramData\chocolatey\bin\RefreshEnv.cmd

echo update related python modules
pip install --upgrade setuptools build wheel

echo create UserProfile\_Code folder if missing:
if not exist %UserProfile%\_Code (
    REM folder doesn't exist
    echo creating missing _Code folder
    mkdir %UserProfile%\_Code
    echo.
)

cd %UserProfile%\_Code

git clone https://github.com/jgstew/jgstew-recipes.git

git clone https://github.com/jgstew/autopkg.git

cd jgstew-recipes

call check_setup_win.bat
