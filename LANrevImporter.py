#!/usr/bin/env python
#
# Copyright 2016 Thomas Burgin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os,  \
       uuid, \
       time,  \
       shutil, \
       hashlib, \
       datetime, \
       sqlite3,   \
       plistlib,   \
       subprocess

from datetime import timedelta

from Foundation import  NSArray,     \
                        NSDictionary, \
                        NSUserName,    \
                        NSHomeDirectory

from os.path import expanduser
from CoreFoundation import CFPreferencesCopyAppValue
from autopkglib import Processor, ProcessorError

__all__ = ["LANrevImporter"]


class LANrevImporter(Processor):
    '''Take as input a pkg or executable and a SDPackages.ampkgprops (plist config)
       to output a .amsdpackages for use in LANrev. If no
       SDPackages.ampkgprops is specified a default config will be generated'''

    description = __doc__

    input_variables = {
        'source_payload_path': {
            'description': 'Path to a pkg or executable',
            'required': True,
        },
        'dest_payload_path': {
            'description': 'Path to the exported .amsdpackages',
            'required': True,
        },
        'sdpackages_ampkgprops_path': {
            'description': 'Path to a plist config for the Software Package to be used in LANrev',
            'required': False,
        },
        'sd_name_prefix': {
            'description': 'Define a prefix for the package to follow naming conventions',
            'required': False,
        },
        'payload_name_prefix': {
            'description': 'Define a prefix for the payload to follow naming conventions',
            'required': False,
        },
        'import_pkg_to_servercenter': {
            'description': 'Imports autopkg .pkg result to LANrev',
            'required': False,
        },
        'add_s_to_availability_date': {
            'description': 'Input additional number of seconds to be added to the AvailabilityDate on the default ampkgprops',
            'required': False,
        },
        'availability_hour': {
            'description': 'Input what time the package should be made available using 24-hour time format. I.e. 20 is 8PM',
            'required': False,
        },
        'installation_condition_name': {
            'description': 'Enter the Application name of the app that must be on the system in order to install. This corresponds to the "File Name" operator',
            'required': False,
        },
        'installation_condition_version_string': {
            'description': 'Enter the Version String that the app must be on the system in order to install. This corresponds to the "File Version String" operator',
            'required': False,
        },
        'os_platform': {
            'description': 'Enter the platform this is intended for. Mac or Win. Default is Mac',
            'required': False,
        },
        'platform_arch': {
            'description': 'Specify the Windows platform architecture. Choices are: x86, x64, or any. Do not specify for Mac packages',
            'required': False,
        },
        'min_os': {
            'description': 'Specify the minimum OS version. Options are: AnyWin, WinXP, Win7, Win8, Win10, Win2003, Win2008, Win2012, AnyOSX, OSX10.6, OSX10.7, OSX10.8, OSX10.9, OSX10.10, OSX10.11',
            'required': False,
        },
        'max_os': {
            'description': 'Specify the maximum OS version. Options are: AnyWin, WinXP, Win7, Win8, Win10, Win2003, Win2008, Win2012, AnyOSX, OSX10.6, OSX10.7, OSX10.8, OSX10.9, OSX10.10, OSX10.11',
            'required': False,
        },
        'executable_options': {
            'description': 'Specify the command line options for a package. More common with Windows packages',
            'required': False,
        }

    }

    output_variables = {
            "lanrev_importer_summary_result": {
                "description": "Description LANrevImporter Happenings"
            }
    }
    appleSingleTool = "/Applications/LANrev Admin.app/Contents/MacOS/AppleSingleTool"
    sdpackages_template = {'SDPackageExportVersion': 1,
                           'SDPayloadFolder': 'Payloads',
                           'SDPackageList': [{'IsNewEntry': False,
                                              'OptionalData': [],
                                              'RequiresLoggedInUser': False,
                                              'InstallTimeEnd': [],
                                              'AllowOnDemandInstallation': False,
                                              'InstallTime': [],
                                              'AutoStartInstallationMinutes': [],
                                              'SoftwarePatchIdentifier': [],
                                              'RestartNotificationNagTime': [],
                                              'PlatformArchitecture': 131071,
                                              'ExecutableSize': 0,
                                              'ResetSeed': 1,
                                              'Priority': 2,
                                              'WU_LanguageCode': [],
                                              'WU_SuperseededByPackageID': [],
                                              'WU_IsUninstallable': [],
                                              'WU_LastDeploymentChangeTime': [],
                                              'IsMacOSPatch': False,
                                              'UploadStatus': [],
                                              'id': 0,
                                              'RequiresAdminPrivileges': False,
                                              'InstallationContextSelector': 2,
                                              'SoftwareSpecNeedToExist': True,
                                              'MinimumOS': 0,
                                              'Description': '',
                                              'AllowOnDemandRemoval': False,
                                              'RetrySeed': 1,
                                              'MaximumOS': 0,
                                              'SoftwarePatchStatus': 0,
                                              'IsMetaPackage': False,
                                              'SoftwarePatchSupportedOS': [],
                                              'ScanAllVolumes': False,
                                              'DontInstallOnSlowNetwork': False,
                                              'ShowRestartNotification': False,
                                              'SelfHealingOptions': [],
                                              'AllowDeferMinutes': [],
                                              'last_modified': '',
                                              'SoftwarePatchRecommended': [],
                                              'UserContext': '',
                                              'EnableSelfHealing': False,
                                              'InstallationDateTime': [],
                                              'AllowToPostponeRestart': False,
                                              'PayloadExecutableUUID': '',
                                              'WU_IsBeta': [],
                                              'OSPlatform': 1,
                                              'RequiresRestart': 0,
                                              'Name': '',
                                              'FindCriteria':
                                                  {'Operator': 'AND', 'Value':
                                                   [{'Operator': 'AND', 'Value':
                                                     [{'Operator': '=',
                                                       'Units': 'Minutes',
                                                       'Property': 'Name',
                                                       'Value2': '',
                                                       'Value': ''}]},
                                                    {'UseNativeType': True,
                                                     'Value': True,
                                                     'Units': 'Minutes',
                                                     'Value2': '',
                                                     'Operator': '=',
                                                     'Property': 'IsPackage'},
                                                    {'UseNativeType': True,
                                                     'Value': True,
                                                     'Units': 'Minutes',
                                                     'Value2': '',
                                                     'Operator': '=',
                                                     'Property': 'IsApplication'}]},
                                              'SDPayloadList':
                                                  [{'IsNewEntry': 0,
                                                    'OptionalData': [],
                                                    'SelectedObjectIsExecutable': True,
                                                    'Description': '',
                                                    'ExecutableName': '',
                                                    'ExecutableSize': 0,
                                                    'TransferExecutableFolder': False,
                                                    'id': 0,
                                                    'SourceFilePath': '',
                                                    'last_modified': '',
                                                    'PayloadOptions': 0,
                                                    'UniqueID': '',
                                                    'IsVisible': True,
                                                    'UploadStatus': 2,
                                                    'MD5Checksum': '',
                                                    'Name': ''}],
                                              'DisplayProgressDuringInstall': False,
                                              'ContinueInstallationAfterFailure': False,
                                              'UserInteraction': 1,
                                              'WarnAboutSlowNetwork': False,
                                              'InstallTimeOptions': 1,
                                              'WU_IsMandatory': [],
                                              'DownloadPackagesBeforeShowingToUser': False,
                                              'PackageType': 1,
                                              'WU_Deadline': [],
                                              'SoftwarePatchVersion': [],
                                              'WU_DeploymentAction': [],
                                              'TargetInstallationVolume': '',
                                              'KeepPackageFileAfterInstallation': False,
                                              'MD5Checksum': [],
                                              'TransferExecutableFolder': [],
                                              'WU_SuperseededByPackageName': [],
                                              'StagingServerOption': 1,
                                              'ExecutableOptions': '',
                                              'WU_UninstallationBehaviorImpact': [],
                                              'ExecutableName': [],
                                              'ExecutableServerVolume': [],
                                              'DontInstallIfUserIsLoggedIn': False,
                                              'SourceFilePath': [],
                                              'UserContextPassword': '',
                                              'AvailabilityDate': datetime.datetime.today(),
                                              'WU_InstallationBehaviorImpact': [],
                                              'PostNotificationAutoClose': [],
                                              'UniqueID': '',
                                              'UseSoftwareSpec': False,
                                              'ExecutablePath': [],
                                              'IsWindowsPatch': False}]}
    open_exe = "/usr/bin/open"
    BUNDLE_ID = "com.poleposition-sw.lanrev_admin"

    
    def get_pref(self, key, domain=BUNDLE_ID):
        """Return a single pref value (or None) for a domain."""
        value = CFPreferencesCopyAppValue(key, domain) or None
        # Casting NSArrays and NSDictionaries to native Python types.
        # This a workaround for 10.6, where PyObjC doesn't seem to
        # support as many common operations such as list concatenation
        # between Python and ObjC objects.
        if isinstance(value, NSArray):
            value = list(value)
        elif isinstance(value, NSDictionary):
            value = dict(value)
        return value


    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d


    def md5_for_file(self, path, block_size=256*128):
        md5 = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(block_size), b''): 
                 md5.update(chunk)
        return md5.hexdigest()
    

    def set_summary_report(self, server, package, payload_id):
        # clear any pre-exising summary result
        if 'lanrev_importer_summary_result' in self.env:
            del self.env['lanrev_importer_summary_result']

        self.env["lanrev_importer_summary_result"] = {
            'summary_text': 'The following SDPackages were uploaded:',
            'report_fields': ['server', 'package', 'id'],
            'data': {
                'server': server,
                'package': package,
                'id': payload_id
            }
        }


    def check_sd_payload(self, exe_name):
        self.output("[+] Checking if [%s] exists in SDCaches.db" % self.sdpackages_template['SDPackageList'][0]['Name'])

        self.output("[+] Attempting to build SDCaches.db path")
        am_server = self.get_pref("ServerAddress")
        self.output("[+] Current AM Server [%s]" % am_server)

        database_path = None

        try:
            database_path = expanduser(self.get_pref("DatabaseDirectory"))
        except:
            pass

        if not database_path:
            database_path = NSHomeDirectory() + "/Library/Application Support/LANrev Admin/Database/"
            self.output("[+] Using default database path [%s]" % database_path)
        else:
            if not database_path[-1] == "/":
                database_path = expanduser(database_path + "/")
            self.output("[+] Using override database path [%s]" % database_path)


        servers_list = os.listdir(database_path)

        for e in servers_list:
            if am_server in e:
                database_path = database_path + e + "/SDCaches.db"
                break

        self.output("[+] Full path to database [%s]" % database_path)

        conn = sqlite3.connect(database_path)
        conn.row_factory = self.dict_factory
        c = conn.cursor()
        sd_packages = c.execute("select * from 'sd_payloads_latest'").fetchall()
        c.close()
        conn.close()

        for e in sd_packages:
            if e["ExecutableName"] == exe_name:
                self.output("[+] [%s] already exists in LANrev Server Center" % exe_name)
                return True

        return False

    def export_amsdpackages(self, source_dir, dest_dir, am_options, sd_name_prefix,
                            payload_name_prefix, sec_to_add, availability_hour, import_pkg,
                            installation_condition_name,
                            installation_condition_version_string, os_platform, platform_arch, min_os, max_os, executable_options):

        unique_id = str(uuid.uuid4()).upper()
        unique_id_sd = str(uuid.uuid4()).upper()
        self.output("[+] unique_id [%s]" % unique_id)
        self.output("[+] unique_id_sd [%s]" % unique_id_sd)
        use_software_spec = False
        
        self.output("[+] ExecutableOptions set to: %s" % executable_options)        
        if executable_options is None:
            executable_options = ""
            
        if sd_name_prefix is None:
            sd_name_prefix = ""

        if payload_name_prefix is None:
            payload_name_prefix = ""

        if availability_hour is None and sec_to_add is 0:
            pass
        elif availability_hour is not None and sec_to_add is 0:
            if not 0 <= int(availability_hour) <= 23:
                if int(availability_hour) is 24:
                    self.output("[+] availability_hour was set to 24, changing to 0")
                    availability_hour = 0
                else:
                    raise ProcessorError("[!] Please enter a valid 24-hour time (i.e. between 0-23)")
            today = datetime.date.today()
            timestamp = time.strftime('%H')
            utc_datetime = datetime.datetime.utcnow()
            utc_datetime_formatted = utc_datetime.strftime("%H")
            time_difference = ((int(utc_datetime_formatted) - int(timestamp)) * 60 * 60)
            #availability_time = datetime.timedelta(hours=int(time_difference))
            if int(utc_datetime_formatted) < int(availability_hour):
                sec_to_add = int(((int(availability_hour) - int(timestamp)) * 60 * 60) + int(time_difference))
            elif int(utc_datetime_formatted) > int(availability_hour):
                sec_to_add = int(((24 - int(timestamp) + int(availability_hour)) * 60 * 60) + int(time_difference))
        elif availability_hour is None and sec_to_add is not 0:
            pass
        else:
            raise ProcessorError("[!] Please only use either `availability_hour` or `add_s_to_availability_date`\n Cannot use both keys at the same time.")

        if installation_condition_name is not None or installation_condition_version_string is not None:
            use_software_spec = True

        if installation_condition_name is not None:
            if ".app" not in installation_condition_name and ".pkg" not in installation_condition_name:
                installation_condition_name = installation_condition_name + ".app"
                self.output("[+] Appending installation condition name with '.app'")

        if platform_arch is not None and os_platform is None:
            raise ProcessorError("[!] You cannot use the 'platform_arch' input variable without also defining the 'os_platform' input variable")

        # OSPlatform setting. 
        if os_platform is not None:
            if os_platform == 'Win':
                os_platform = 4
                self.output("[+] OSPlatform set to Windows")
            elif os_platform == 'Mac':
                os_platform = 1
                self.output("[+] OSPlatform set to Mac")
        else:
            os_platform = 1
            self.output("[+] OSPlatform set to Mac")

        # Platform architecture setting
        if platform_arch is not None:
            if platform_arch == 'x86':
                self.output("[+] Platform Arch set to Windows X86")
                platform_arch = 131073
            elif platform_arch == 'x64':
                self.output("[+] Platform Arch set to Windows x64")
                platform_arch = 131074
            elif platform_arch == 'any':
                self.output("[+] Platform Arch set to Windows any")
                platform_arch = 196607
        else:
            if os_platform == 4:
                platform_arch = 196607
            elif os_platform == 1:
                platform_arch = 131071 # Mac

        if os_platform == 4 and platform_arch == 131071:
            platform_arch = 196607

         
        # List of OS options to be used with min_os and max_os. This will need to be updated when new OS's come out. 
        # Went back to WinXP, OS X 10.5 and Win2008. If you need older, file an issue.
        # These values are available in /Applications/LANrev\ Admin/Contents/Resources/InfoItemEnumerations.plist
        os_options = {'AnyWin': 1, 'WinXP': 1024, 'Win7': 16384, 'Win8': 65536, 'Win10': 131072, 'Win2008': 8192, 'Win2012': 32768, \
        'AnyOSX': 0, 'OSX10.5': 4176, 'OSX10.6': 4192, 'OSX10.7': 4208, 'OSX10.8': 4224, 'OSX10.9': 4240, 'OSX10.10': 4256, 'OSX10.11': 4272}
        
        # MinimumOS setting
        for i in xrange(1000000):
            min_choice = os_options.get(min_os)
        min_os = min_choice
        
        # MaximumOS setting
        for i in xrange(1000000):
            max_choice = os_options.get(max_os)
        max_os = max_choice
        
        # Making sure OSPlatform has something for min/max OS
        if min_os is None and os_platform == 4:
            min_os = 1
        if max_os is None and os_platform == 4:
            max_os = 1
        if min_os is None and os_platform == 1:
            min_os = 0
        if max_os is None and os_platform == 1:
            max_os = 0
                
        def add_comparison_operators():
            name_dict = dict(
                Operator="=",
                Units="Minutes",
                Property="Name",
                Value="",
                Value2=""
            )
            version_dict = dict(
                Operator="=",
                Units="Minutes",
                Property="VersionString",
                Value="",
                Value2=""
            )
            self.sdpackages_template['SDPackageList'][0]['FindCriteria']['Value'][0]['Value'] = [name_dict, version_dict]

        if os.path.exists(dest_dir):
            self.output("[+] dest_dir [%s] exists. Removing it." % dest_dir)
            shutil.rmtree(dest_dir)

        try:
            self.output("[+] Creating [%s]" % dest_dir)
            os.mkdir(dest_dir)
            self.output("[+] Creating [%s/Payloads]" % dest_dir)
            os.mkdir(dest_dir + "/Payloads")
        except OSError, err:
            if os.path.exists(dest_dir):
                pass
            else:
                self.output("[+] Failed to create [%s] Please check your permissions and try again. Error [%s]" % (dest_dir, err))

        try:
            subprocess.check_output([self.appleSingleTool, "encode", "-s", source_dir, "-t", dest_dir + "/Payloads/" + unique_id, "-p", "-x", "-z", "3"])
            self.output("[+] Exported [%s] to [%s]" % (source_dir, dest_dir))
        except (subprocess.CalledProcessError, OSError), err:
            self.output("[!] Please make sure [%s] exists" % self.appleSingleTool)
            raise err

        try:
            if os.path.exists(am_options):
                shutil.copyfile(am_options, dest_dir + "/SDPackages.ampkgprops")
            else:
                plistlib.writePlist(self.sdpackages_template, dest_dir + "/SDPackages.ampkgprops")
        except (TypeError, OSError):
            plistlib.writePlist(self.sdpackages_template, dest_dir + "/SDPackages.ampkgprops")

        try:
            executable_size = subprocess.check_output(["/usr/bin/stat", "-f%z", source_dir])
            md5_checksum = self.md5_for_file(dest_dir + "/Payloads/" + unique_id)
        except (subprocess.CalledProcessError, OSError), err:
            raise err

        self.sdpackages_template = plistlib.readPlist(dest_dir + "/SDPackages.ampkgprops")

        if installation_condition_name is None and installation_condition_version_string is not None:
            raise ProcessorError("[!] You cannot use the 'installation_condition_version_string' input variable without also defining the 'installation_condition_name' input variable")

        if installation_condition_name is None:
            installation_condition_name = ""
        
        source_dir = source_dir.strip('.msi')
        source_dir = source_dir.strip('.exe')

        self.sdpackages_template['SDPackageList'][0]['Name'] = sd_name_prefix + source_dir.split("/")[-1].strip(".pkg")
        self.sdpackages_template['SDPackageList'][0]['PayloadExecutableUUID'] = unique_id
        self.sdpackages_template['SDPackageList'][0]['UniqueID'] = unique_id_sd
        self.sdpackages_template['SDPackageList'][0]['ExecutableSize'] = int(executable_size)
        self.sdpackages_template['SDPackageList'][0]['SDPayloadList'][0]['ExecutableName'] = source_dir.split("/")[-1]
        self.sdpackages_template['SDPackageList'][0]['SDPayloadList'][0]['ExecutableSize'] = int(executable_size)
        self.sdpackages_template['SDPackageList'][0]['SDPayloadList'][0]['MD5Checksum'] = md5_checksum
        self.sdpackages_template['SDPackageList'][0]['SDPayloadList'][0]['Name'] = payload_name_prefix + source_dir.split("/")[-1].strip(".pkg")
        self.sdpackages_template['SDPackageList'][0]['SDPayloadList'][0]['SourceFilePath'] = source_dir
        self.sdpackages_template['SDPackageList'][0]['SDPayloadList'][0]['UniqueID'] = unique_id
        self.sdpackages_template['SDPackageList'][0]['SDPayloadList'][0]['last_modified'] = ""
        self.sdpackages_template['SDPackageList'][0]['UseSoftwareSpec'] = use_software_spec
        self.sdpackages_template['SDPackageList'][0]['OSPlatform'] = os_platform
        self.sdpackages_template['SDPackageList'][0]['PlatformArchitecture'] = platform_arch
        self.sdpackages_template['SDPackageList'][0]['MinimumOS'] = min_os
        self.sdpackages_template['SDPackageList'][0]['MaximumOS'] = max_os
        self.sdpackages_template['SDPackageList'][0]['ExecutableOptions'] = executable_options
        if installation_condition_version_string is not None:
            add_comparison_operators()
            self.sdpackages_template['SDPackageList'][0]['FindCriteria']['Value'][0]['Value'][1]['Value'] = installation_condition_version_string
        self.sdpackages_template['SDPackageList'][0]['FindCriteria']['Value'][0]['Value'][0]['Value'] = installation_condition_name
        ## Add defined sec to AvailabilityDate
        date = datetime.datetime.today()
        if availability_hour is not None:
          current_minute = date.strftime("%M")
          current_second = date.strftime("%S")
          date = date - timedelta(minutes=int(current_minute), seconds=int(current_second))
          date = date + datetime.timedelta(seconds=sec_to_add)
        else:
          date = date + datetime.timedelta(seconds=sec_to_add)

        self.sdpackages_template['SDPackageList'][0]['AvailabilityDate'] = date
        plistlib.writePlist(self.sdpackages_template, dest_dir + "/SDPackages.ampkgprops")


        if import_pkg and not self.check_sd_payload(source_dir.split("/")[-1]):
            self.output("[+] Attempting to upload [%s] to LANrev Server Center" % dest_dir)
            try:
                subprocess.check_output([self.open_exe, "lanrevadmin://importsoftwarepackage?packagepath=" + dest_dir])
                subprocess.check_output([self.open_exe, "lanrevadmin://commitsoftwarepackagechanges"])
                self.output("[+] Uploading...")
                time.sleep(5)
                lanrev_pid = subprocess.check_output(["/usr/bin/pgrep", "LANrev Admin"]).strip("\n")
                while True:
                    lanrev_open_files = subprocess.check_output(["/usr/sbin/lsof", "-p", lanrev_pid])
                    payload_check = dest_dir + "/Payloads/" + unique_id
                    if payload_check in lanrev_open_files:
                        self.output("[+] Uploading...")
                        time.sleep(3)
                    else:
                        self.set_summary_report(self.get_pref("ServerAddress"),
                            self.sdpackages_template['SDPackageList'][0]['Name'],
                            unique_id)
                        break
    
            except (subprocess.CalledProcessError, OSError), err:
                raise err
        else:
            self.output("[+] Nothing uploaded to LANrev")


    def main(self):
        self.output("[+] Using LANrevImporter version: 0.5.3")
        source_payload = self.env.get('source_payload_path')
        dest_payload = self.env.get('dest_payload_path')
        sdpackages_ampkgprops = self.env.get('sdpackages_ampkgprops_path')
        sd_name_prefix = self.env.get('sd_name_prefix')
        payload_name_prefix = self.env.get('payload_name_prefix')
        import_pkg = self.env.get('import_pkg_to_servercenter')
        installation_condition_name = self.env.get('installation_condition_name')
        installation_condition_version_string = self.env.get('installation_condition_version_string')
        os_platform = self.env.get('os_platform')
        platform_arch = self.env.get('platform_arch')
        min_os = self.env.get('min_os')
        max_os = self.env.get('max_os')
        executable_options = self.env.get('executable_options')
        availability_hour = self.env.get('availability_hour')
        try:
            sec_to_add = int(self.env.get('add_s_to_availability_date'))
        except (ValueError, TypeError):
            self.output("[+] add_s_to_availability_date is not an int. Reverting to default of 0")
            sec_to_add = 0

        self.export_amsdpackages(source_payload, dest_payload, sdpackages_ampkgprops, sd_name_prefix, payload_name_prefix, sec_to_add, availability_hour, import_pkg, installation_condition_name, installation_condition_version_string, os_platform, platform_arch, min_os, max_os, executable_options)


if __name__ == '__main__':
    processor = LANrevImporter()
    processor.execute_shell()
