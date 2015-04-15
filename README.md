## AbsoluteManageExport

AbsoluteManageExport is an AutoPkg Processor for Absolute Manage.

## Configure Absolute Manage

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
~/Library/Application Support/LANrev Admin/Database/
```

You should be all set to run your Absolute recipes.

## Installing the Processor

You can install this processor locally on the system by running this installer.
https://github.com/tburgin/AbsoluteManageExport/releases/latest

## AutoPkg Shared Processor

As of AutoPkg 0.4.0 you can use this processor as a shared processor.

Add the processor repo 
```bash
autopkg repo-add https://github.com/tburgin/AbsoluteManageExport
```
Then use this as the processor in your recipes
```bash
com.github.tburgin.AbsoluteManageExport/AbsoluteManageExport
```

See this wiki for more information on shared processor.
https://github.com/autopkg/autopkg/wiki/Processor-Locations

## Sample Processor

```xml
<dict>
		<key>Processor</key>
		<string>com.github.tburgin.AbsoluteManageExport/AbsoluteManageExport</string>
		<key>Arguments</key>
		<dict>
			<key>dest_payload_path</key>
			<string>%RECIPE_CACHE_DIR%/%NAME%-%version%.amsdpackages</string>
			<key>sdpackages_ampkgprops_path</key>
			<string>%RECIPE_DIR%/%NAME%-Defaults.ampkgprops</string>
			<key>source_payload_path</key>
			<string>%pkg_path%</string>
			<key>sd_name_prefix</key>
			<string>(OSX AutoPkg) </string>
			<key>payload_name_prefix</key>
			<string>(OSX) </string>
			<key>add_s_to_availability_date</key>
			<integer>86400</integer>
			<key>import_abman_to_servercenter</key>
			<true/>
		</dict>
</dict>
```

## Expected Behavior

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

## Sources

The `get_pref` method I borrowed from [munki](https://github.com/munki/munki)
