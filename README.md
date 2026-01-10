# WipeZero

![wipezero logo](https://github.com/OGMemDC/wipezero/blob/main/doc/resources/wipezero_small.png)  

Lightweight USB storage wipe utility for Linux, provides NIST & DoD level wipe functionality

- [Overview](#overview)
- [Installation](#installation)
- [Running](#running)
  - [Using Profiles](#using-profiles)
  - [Custom Wipe Settings](#custom-wipe-setting)
  - [Cryptographic and Secure Wipe](#cryptographic-and-secure-wipe)
  - [Automatic Mode](#automatic-wipe)
- [Verification Methods](#verification-methods)
- [Reporting](#reporting)
- [Additional Features](#additional-features)
  - [List USB Devices](#list-detected-usb-devices)
  - [Progress Bar](#progress-bar)
  - [GUI Confirmation](#gui-confirmation)
  - [GUI Report](#gui-report)
  - [Detect Fake USB](#detect-fake-usb)
- [Contributing](#contributing)

## Overview

WipeZero quickly wipes any remenants of data from a USB storage device. You can select the level of data wipe to be performed using a pre-built profile, or you can set custom data wipe parameters.

The utility will create you a NIST data wipe report, and a cryptographically signed with hardware hash signature report if you so desire.

## Installation

WipeZero was designed and developed on Ubuntu 25.10 Linux because that was my need at the time. I did add code for Mac & Windows platforms but I will admit it has not been thouroughly tested (other then on Ubuntu).

To install on Ubuntu Linux:

**`[bash shell]:`**
`$ # clone the git repository`  
`$ git clone https://github.com/OGMemDC/wipezero.git`  
`$ cd wipezero`
`$ # run setup to install dependencies`
`$ bash ./setup.sh`
`$ # resolve any dependancy issues...`
`$ bash ./install.sh`

To install on other operating systems:
*write your own installer, I have not got to it yet ;-)*

## Running

WipeZero uses a CLI interface and long style command line parameters. The most important of which is **--force**. Due to the nature of the utility and the risk of data loss, the default operating mode is always a dry run unless the --force flag is used.

>**usage:&nbsp;&nbsp;wipezero&nbsp;&nbsp;[-h] [--force] [--profile {nist-clear,nist-purge,dod-short,dod custom}]**
>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**[--passes PASSES] [--progress] [--gui] [--list] [--crypto-erase] [--secure-erase]**  
>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**[--auto] [--verify] [--report] [--report-dir REPORT_DIR] [--pdf-report]**
>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**[--hash-verify] [--gui-report] [--detect-fake-usb] [--forensic-verify]**
>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**[path]**
>
> Advanced, cross-platform, multi-profile disk wipe utility for removable USB storage devices. Includes multiple reporting options and additional features such as listing removable USB storage devices and detecting fake removable USB storage devices.  
>
> Author: BlackHatOG Email: [bitbltog@proton.me](mailto:bitbltog@proton.me) Date: December 2025
>
> **positional arguments:**
>&nbsp;&nbsp;&nbsp;&nbsp;**path**&nbsp;&nbsp;-&nbsp;&nbsp;Path to the USB storage device/directory/block/etc to be wiped
>
> **options:**
> &nbsp;&nbsp;&nbsp;&nbsp;**-h, --help**&nbsp;&nbsp;-&nbsp;&nbsp;show this help message and exit
> &nbsp;&nbsp;&nbsp;&nbsp;**--force**&nbsp;&nbsp;-&nbsp;&nbsp;without this flag specified nothing gets deleted or wiped, just a dry-run
> &nbsp;&nbsp;&nbsp;&nbsp;**--profile**&nbsp;&nbsp;-&nbsp;&nbsp;{nist-clear,nist-purge,dod-short,dod,custom}  specify the wipe profile or a custom profile (default: nist-clear)
> &nbsp;&nbsp;&nbsp;&nbsp;**--passes PASSES**&nbsp;&nbsp;-&nbsp;&nbsp;if you do not select a wipe profile then you can specify the number of wipe passes manually (default: 1)
> &nbsp;&nbsp;&nbsp;&nbsp;**--progress** &nbsp;&nbsp;-&nbsp;&nbsp;display a progress bar with progress updates
> &nbsp;&nbsp;&nbsp;&nbsp;**--gui**&nbsp;&nbsp;-&nbsp;&nbsp;display a message box that confirms delete
> &nbsp;&nbsp;&nbsp;&nbsp;**--list**&nbsp;&nbsp;-&nbsp;&nbsp;display a list of automatically detected USB storage devices
> &nbsp;&nbsp;&nbsp;&nbsp;**--crypto-erase**&nbsp;&nbsp;-&nbsp;&nbsp;Attempt hardware cryptographic erase (if supported)
> &nbsp;&nbsp;&nbsp;&nbsp;**--secure-erase**&nbsp;&nbsp;-&nbsp;&nbsp;Attempt controller secure erase (if supported)
> &nbsp;&nbsp;&nbsp;&nbsp;**--auto**&nbsp;&nbsp;-&nbsp;&nbsp;Automatically select safest erase method per device
> &nbsp;&nbsp;&nbsp;&nbsp;**--verify**&nbsp;&nbsp;-&nbsp;&nbsp;Perform post-erase verification pass
> &nbsp;&nbsp;&nbsp;&nbsp;**--report**&nbsp;&nbsp;-&nbsp;&nbsp;Generate NIST compliance report
> &nbsp;&nbsp;&nbsp;&nbsp;**--report-dir REPORT_DIR**&nbsp;&nbsp;-&nbsp;&nbsp;Directory for reports (default: cwd)
> &nbsp;&nbsp;&nbsp;&nbsp;**--pdf-report**&nbsp;&nbsp;-&nbsp;&nbsp;Generate a X.509 signed PDF report with hardware identification hashes
> &nbsp;&nbsp;&nbsp;&nbsp;**--hash-verify**&nbsp;&nbsp;-&nbsp;&nbsp;Generate a unique hashcode and embed it in the report as part of the signature payload
> &nbsp;&nbsp;&nbsp;&nbsp;**--gui-report**&nbsp;&nbsp;-&nbsp;&nbsp;display a gui report reader at the end
> &nbsp;&nbsp;&nbsp;&nbsp;**--detect-fake-usb**&nbsp;&nbsp;-&nbsp;&nbsp;examine and display warning messages about suspect USB storage devices
> &nbsp;&nbsp;&nbsp;&nbsp;**--forensic-verify**&nbsp;&nbsp;-&nbsp;&nbsp;forensic evidence level verification and reporting

### Using Profiles

WipeZero "wipes" fragments of old data by filling the storage device with new data until the storage device is full, effectively overwriting whatever remenants are left on the device. Then deletes the data that was written to the device so that it is empty again.  

Each time that the storage device is filled to capacity and deleted is called a "pass".

The data that is written to the device is called "fill character", it is common to use the character 1 (one) or 0 (zero), or to just use random data.

The following table outlines how each profile wipes the storage device by defining the number of passes and what fill character is used in each pass. Each profile has a different number of passes that are performed, and will contains different combinations of fill characters that are used on each pass.

|   PROFILE  |Pass:1| Pass:2 | Pass:3 |Pass:4|Pass:5| Pass:6 |Pass:7|
| ---------- | ---- | ------ | ------ | ---- | ---- | ------ | ---- |
| nist-clear | zero |        |        |      |      |        |      |
| nist-purge | zero | random |        |      |      |        |      |
| dod-short  | zero |  one   | random |      |      |        |      |
|    dod     | zero |  one   | random | zero | one  | random | zero |
|   custom   |      |        |        |      |      |        |      |

**examples:**

The following will wipe the device at /dev/dm-0 using the nist-clear
profile and produce a NIST approved report:
`sudo wipezero --profile nist-clear --force --report --report-dir ~/wipezero/out/report.pdf /dev/dm-0`

To wipe a USB storage device to DoD standards:
`sudo wipezero --profile dod --force --report --report-dir ~/wipezero/out/report.pdf /dev/dm-0`

### Custom Wipe Setting

The custom wipe setting is for when you want to perform a wipe that is not satisfied by one of the pre-built profiles.

A custom wipe uses the command line arguments `--profile custom` and `--passes`, when you perform a custom wipe WipeZero will use zero (0) as the fill character.

**examples:**

The following will wipe the device at /dev/dm-0 6 times and produce a NIST approved report:
`sudo wipezero --profile custom --passes 6 --report --report-dir ~/wipezero/out/report.pdf /dev/dm-0`

### Cryptographic and Secure Wipe

TODO: Write this section

### Automatic Wipe

TODO: Write this section

### Verification Methods

TODO: Write this section

### Reporting

TODO: Write this section

### Additional Features

TODO: Write this section

#### List Detected USB Devices

TODO: Write this section

#### Progress Bar

TODO: Write this section

#### GUI Confirmation 

TODO: Write this section

#### GUI Report

TODO: Write this section

#### Detect Fake USB

TODO: Write this section

## Contributing

TODO: Write this section
