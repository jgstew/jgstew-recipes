
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
choco install vscode -y

echo install python 3.10.x
REM https://docs.python.org/3/using/windows.html#installing-without-ui
choco install python --version="3.10.8" -y --install-arguments="InstallAllUsers=1 PrependPath=1 CompileAll=1"


echo install visualstudio2019-workload-vctools
choco install visualstudio2019-workload-vctools -y
