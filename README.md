# LANrevImporter

LANrevImporter is an AutoPkg Processor for LANrev by HEAT.

## Configure LANrev

Enable External SD Package Upload. Run this in the same user context that you will be running LANrev Admin:

```bash
defaults write com.poleposition-sw.lanrev_admin AllowURLSDPackageImport -bool true
```

Launch the LANrev Admin application. Sign into the correct server with a user that has rights to upload SD packages.

```bash
/Applications/LANrev Admin.app
```

Double check there is a folder entry for your server - username in:

```bash
~/Library/Application Support/LANrev Admin/Database/
```

You should be all set to run your LANrev recipes.

## Installing the Processor

You can install this processor locally on the system by running this installer:
https://github.com/jbaker10/LANrevImporter/releases/latest

## AutoPkg Shared Processor

As of AutoPkg 0.4.0 you can use this processor as a shared processor.

Add the processor repo:
```bash
autopkg repo-add https://github.com/jbaker10/LANrevImporter
```
Then use this as the processor in your recipes:
```bash
com.github.jbaker10.LANrevImporter/LANrevImporter
```

See this wiki for more information on shared processor:
https://github.com/autopkg/autopkg/wiki/Processor-Locations

## Sample Processor

```xml
<dict>
		<key>Processor</key>
		<string>com.github.jbaker10.LANrevImporter/LANrevImporter</string>
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
			<key>import_pkg_to_servercenter</key>
			<true/>
			<key>installation_condition_name</key>
			<string>%NAME%.app</string>
			<key>installation_condition_version_string</key>
			<string>1.0</string>
		</dict>
</dict>
```

## Expected Behavior

LANrevImporter currently only performs a basic check to see if an executable with the same name is already in the SD Package database. If so, no upload takes place. If not, a new Software Package and Payload are created.

### New package uploaded.

_Remember, the LANrev Admin app must be open for an upload to complete._

```
LANrevImporter
LANrevImporter: [+] Exported [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.pkg] to [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.amsdpackages]
LANrevImporter: [+] Checking if [AdobeFlashPlayer-16.0.0.305] exists in SDCaches.db
LANrevImporter: [+] Attemting to upload [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.amsdpackages] to LANrev Server Center
Receipt written to /Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/receipts/AdobeFlashPlayer-receipt-20150223-232722.plist
```

### Package Exists

```
LANrevImporter
LANrevImporter: [+] Exported [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.pkg] to [/Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/AdobeFlashPlayer-16.0.0.305.amsdpackages]
LANrevImporter: [+] Checking if [AdobeFlashPlayer-16.0.0.305] exists in SDCaches.db
LANrevImporter: [+] [AdobeFlashPlayer-16.0.0.305.pkg] already exists in LANrev Server Center
LANrevImporter: [+] Nothing uploaded to Absolute Manage
Receipt written to /Users/burgintj/Library/AutoPkg/Cache/com.github.tburgin.Absolute.AdobeFlashPlayer/receipts/AdobeFlashPlayer-receipt-20150223-232413.plist
```

## Sources

The `get_pref` method I borrowed from [munki](https://github.com/munki/munki).

## Contributors

Thanks to:
### [Tom Burgin](https://github.com/tburgin)
* Tom is the original creator of the formerly named AbsoluteManageExport, that evolved into LANrev when the application was bought by HEAT. Thanks Tom for all the hard work that makes us look good!
* [Patrick Gallagher](https://github.com/patgmac)
