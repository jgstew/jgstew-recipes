{{! This is a template for installing Firefox on Windows systems with PowerShell. }}
# URL of the file to download:
$url = "{{download_url}}"

# Expected SHA256 hash of the file (replace with your actual hash)
$expectedHash = "{{file_sha256}}"

# Path where the downloaded file will be saved
$outputFile = "C:\Windows\Temp\{{file_name}}"

# Download the file
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri $url -OutFile $outputFile

# Calculate the actual SHA256 hash of the downloaded file
$actualHash = Get-FileHash -Path $outputFile -Algorithm SHA256 | Select-Object -ExpandProperty Hash

# Compare the actual and expected hashes
if ($actualHash -eq $expectedHash) {
    Write-Output "Hashes match. Proceeding to install."

    # Execute the downloaded file
    Start-Process -FilePath $outputFile -ArgumentList "/S" -Wait

    Write-Output "Install completed."
} else {
    Write-Output "Hashes do not match. The downloaded file may be corrupted or tampered with."
    # You can choose to delete the downloaded file in case of hash mismatch
    # Remove-Item -Path $outputFile
}
