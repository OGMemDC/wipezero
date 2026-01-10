![wipezero logo](https://github.com/OGMemDC/wipezero/blob/main/doc/resources/wipezero_small.png)
# WipeZero

Lightweight USB storage wipe utility for linux.

- [Overview]
- [Installation]
- [Running]
  - [Using Profiles]
  - [Custom Wipe Settings]
- [Contributing]

## Overview
WipeZero quickly wipes any remenants of data from a USB storage device. You can select the level of data wipe to be performed using a pre-built profile, or you can set custom data wipe parameters.

The utility will create you a NIST data wipe report, and a cryptographically signed with hardware hash signature report if you so desire.

## Installation
WipeZero was designed and developed on Ubuntu 25.10 Linux because that was my need at the time. I did add code for Mac & Windows platforms but I will admit it has not been thouroughly tested (other then on Ubuntu).

To install on Ubuntu Linux:

- clone the repository `git clone https://github.com/OGMemDC/wipezero.git`
- change to the newly created wipezero directory `cd wipezero`
- check that all the dependencies have been met by running `bash setup.sh` and resolving any issues before continuing.
- finally run `sudo ./install.sh` and follow the prompts.

To install on other operating systems:

- write your own installer, I have not got to it yet ;-)

## Running
WipeZero takes a fair number of command line arguments to run:

> **usage: wipezero [-h] [--force] [--profile {nist-clear,nist-purge,dod-short,dod custom}] [--passes PASSES] [--progress] [--gui] [--list]**
>                   **[--crypto-erase] [--secure-erase] [--auto] [--verify] [--report] [--report-dir REPORT_DIR] [--pdf-report] [--hash-verify]**
>                   **[--gui-report] [--detect-fake-usb] [--forensic-verify]**
>                   **[path]**

> Advanced, cross-platform, semi-fast, and multi-profile disk wipe utility for removable USB storage devices. Includes multiple reporting options and
> additional features such as listing removable USB storage devices and detecting fake removable USB storage devices. Author: BlackHatOG Email:
> <bitbltog@proton.me> Date: December 2025
> 
> positional arguments:
>   path                  Path to the USB storage device/directory/block/etc to be wiped
> 
> options:
>  -h, --help            show this help message and exit
>  --force               without this flag specified nothing gets deleted or wiped, just a dry-run
  --profile {nist-clear,nist-purge,dod-short,dod,custom}
                        specify the wipe profile or a custom profile (default: nist-clear)
  --passes PASSES       if you do not select a wipe profile then you can specify the number of wipe passes manually (default: 1)
  --progress            display a progress bar with progress updates
  --gui                 display a message box that confirms delete
  --list                display a list of automatically detected USB storage devices
  --crypto-erase        Attempt hardware cryptographic erase (if supported)
  --secure-erase        Attempt controller secure erase (if supported)
  --auto                Automatically select safest erase method per device
  --verify              Perform post-erase verification pass
  --report              Generate NIST compliance report
  --report-dir REPORT_DIR
                        Directory for reoirts (default: cwd)
  --pdf-report          Generate a X.509 signed PDF report with hardware identification hashes
  --hash-verify         Generate a unique hashcode and embed it in the report as part of the signature payload
  --gui-report          display a gui report reader at the end
  --detect-fake-usb     examine and display warning messages about suspect USB storage devices
  --forensic-verify     forensic evidence level verification and reporting
`

### Running - Using Profiles

The following table outlines how each profile wipes the storage device.
There are 1 to 7 iterations of wiping the storage device with a fill character which can be one of either 0, 1, or a random character depending on the profile.
On the below table FC = Fill Character, and WI = Wipe Iteraction.

|   PROFILE  | WI 1 |   WI 2 |  WI 3  | WI 4 | WI 5 |  WI 6  | WI 7 |
| ---------- | ---- | ------ | ------ | ---- | ---- | ------ | ---- |
| nist-clear | zero |        |        |      |      |        |      |
| nist-purge | zero | random |        |      |      |        |      |
| dod-short  | zero |  one   | random |      |      |        |      |
|    dod     | zero |  one   | random | zero | one  | random | zero |
|   custom   |      |        |        |      |      |        |      |

To wipe a USB storage device to NIST standards:
`sudo wipezero -profile nist-clear -force`

To wipe a USB storage device to DoD standards:
`sudo wipezero --profile dod`

### Running - Custom Wipe Settings

## Contributing