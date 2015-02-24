## AbsoluteManageExport

AbsoluteManageExport is an AutoPkg Processor for Absolute Manage.

### Configure Absolute Manage

Enable External SD Package Upload. Run this in the same user contex that you will be running Absolute Manage Admin.

```bash
defaults write com.poleposition-sw.lanrev_admin AllowURLSDPackageImport -bool true
```

Launch the Absolute Manage Admin Application. Sign into the correct server with a user that has rights to upload SD packages.

```bash
/Applications/LANrev Admin.app
```

Double check there is a folder entry for your server - username in:

```bash
~/Library/Application Support/LANrev\ Admin/Database/
```

You should be all set to run your Absolute recipe.

### Expected Behavior

AbsoluteManageExport currently only performs a basic check to see if an executable with the same name is already in the SD Package database. If so, no upload takes place. If not, a new Software Package and Payload are created.

##### New package uploaded.
Remember, the Absolute Manage Admin app must be open for an upload to complete.
```
AbsoluteManageExport
AbsoluteManageExport: [+] Exported [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.pkg] to [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.amsdpackages]
AbsoluteManageExport: [+] Checking if [AdobeFlashPlayer-16.0.0.305] exists in SDCaches.db
AbsoluteManageExport: [+] Attemting to upload [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.amsdpackages] to Absolute Manage Server Center
Receipt written to /Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/receipts/AdobeFlashPlayer-receipt-20150223-232722.plist
```

##### Package Exists
```
AbsoluteManageExport
AbsoluteManageExport: [+] Exported [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.pkg] to [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.amsdpackages]
AbsoluteManageExport: [+] Checking if [AdobeFlashPlayer-16.0.0.305] exists in SDCaches.db
AbsoluteManageExport: [+] [AdobeFlashPlayer-16.0.0.305.pkg] already exists in Absolute Manage Server Center
AbsoluteManageExport: [+] Nothing uploaded to Absolute Manage
Receipt written to /Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/receipts/AdobeFlashPlayer-receipt-20150223-232413.plist
```
