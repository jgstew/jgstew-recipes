#!/bin/bash
{{! This is a template for installing Firefox on Linux systems with bash. }}
# URL of the file to download
url="{{download_url}}"

# Expected SHA-256 hash of the file
expected_sha256="{{file_sha256}}"

# Temporary file to store downloaded content
download_file_path=/tmp/{{file_name}}

# install prereqs if missing (docker)
if command -v apt &> /dev/null; then
    apt install -y curl bzip2
fi

# Download the file using curl
curl -sSL "$url" -o "$download_file_path"

# Calculate the SHA-256 hash of the downloaded file
actual_sha256=$(sha256sum "$download_file_path" | awk '{print $1}')

# Compare the calculated hash with the expected hash
if [ "$actual_sha256" == "$expected_sha256" ]; then
    echo "File downloaded successfully and hash matched: $actual_sha256"
    echo "Installing"
    # https://support.mozilla.org/en-US/kb/install-firefox-linux
    cd /tmp
    tar xjf $download_file_path
    rm -rf /opt/firefox
    mv firefox /opt
    rm -f /usr/local/bin/firefox
    ln -s /opt/firefox/firefox /usr/local/bin/firefox
    mkdir -p /usr/local/share/applications
    cat <<ENDOFTOKEN > /usr/local/share/applications/firefox.desktop
[Desktop Entry]
Version=1.0
Name=Firefox Web Browser
Comment=Browse the World Wide Web
GenericName=Web Browser
Keywords=Internet;WWW;Browser;Web;Explorer
Exec=firefox %u
Terminal=false
X-MultipleArgs=false
Type=Application
Icon=/opt/firefox/browser/chrome/icons/default/default128.png
Categories=GNOME;GTK;Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/rss+xml;application/rdf+xml;image/gif;image/jpeg;image/png;x-scheme-handler/http;x-scheme-handler/https;x-scheme-handler/ftp;x-scheme-handler/chrome;video/webm;application/x-xpinstall;
StartupNotify=true
ENDOFTOKEN
    echo "FireFox installed!"
else
    echo "Hash verification failed! Expected: $expected_sha256, Actual: $actual_sha256"
fi
