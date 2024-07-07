# https://github.com/Homebrew/homebrew-cask/blob/master/Casks/f/firefox.rb
# brew install --cask --verbose ~/Library/AutoPkg/Cache/com.github.jgstew.cask.Firefox-Mac/firefox.rb
cask "firefox" do
    version "{{version}}"

    language "en", default: true do
      sha256 "{{file_sha256}}"
      "en-US"
    end

    url "https://download-installer.cdn.mozilla.net/pub/firefox/releases/#{version}/mac/#{language}/Firefox%20#{version}.dmg",
        verified: "download-installer.cdn.mozilla.net/pub/firefox/releases/"
    name "Mozilla Firefox"
    desc "Web browser"
    homepage "https://www.mozilla.org/firefox/"

    livecheck do
      url "https://download.mozilla.org/?product=firefox-latest-ssl&os=osx"
      strategy :header_match
    end

    auto_updates true
    conflicts_with cask: [
      "firefox@beta",
      "firefox@cn",
      "firefox@esr",
    ]
    depends_on macos: ">= :catalina"

    app "Firefox.app"
    # shim script (https://github.com/Homebrew/homebrew-cask/issues/18809)
    shimscript = "#{staged_path}/firefox.wrapper.sh"
    binary shimscript, target: "firefox"

    preflight do
      File.write shimscript, <<~EOS
        #!/bin/bash
        exec '#{appdir}/Firefox.app/Contents/MacOS/firefox' "$@"
      EOS
    end

    uninstall quit: "org.mozilla.firefox"

    zap trash: [
          "/Library/Logs/DiagnosticReports/firefox_*",
          "~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/org.mozilla.firefox.sfl*",
          "~/Library/Application Support/CrashReporter/firefox_*",
          "~/Library/Application Support/Firefox",
          "~/Library/Caches/Firefox",
          "~/Library/Caches/Mozilla/updates/Applications/Firefox",
          "~/Library/Caches/org.mozilla.crashreporter",
          "~/Library/Caches/org.mozilla.firefox",
          "~/Library/Preferences/org.mozilla.crashreporter.plist",
          "~/Library/Preferences/org.mozilla.firefox.plist",
          "~/Library/Saved Application State/org.mozilla.firefox.savedState",
          "~/Library/WebKit/org.mozilla.firefox",
        ],
        rmdir: [
          "~/Library/Application Support/Mozilla", #  May also contain non-Firefox data
          "~/Library/Caches/Mozilla",
          "~/Library/Caches/Mozilla/updates",
          "~/Library/Caches/Mozilla/updates/Applications",
        ]
  end
