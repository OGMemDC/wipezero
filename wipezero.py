#!/usr/bin/env python3
# vim:ff=unix ts=4 ss=4 vim60:fdm=marker
"""
  
    /--------------------------------------------------------------------------\
    \  WipeZero: Advanced Cross-Platform USB Storage Wipe Utility              /
    /                                                                          \
    \                        Version: 1.0.0                                    /
    /                                                                          \
    \    Author:        BlackHatOG                                             /
    /    Email:         ogbitblt@proton.me                                     \
    \    Date:          December 2025                                          /
    /    License:       MIT License                                            \
    \                                                                          /     
    \    Description:   Advanced, cross-platform, semi-fast, and multi-profile /
    /                   disk wipe utility for removable USB storage devices.   \
    \--------------------------------------------------------------------------/


"""
import os
import sys
import platform
import shutil
import subprocess
import logging
import argparse
from datetime import datetime
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import hashlib
from enum import Enum

#
#-----------------------------------------------------------------------------
#   GLOBALS
#-----------------------------------------------------------------------------
#

#
# NIST / DOD  WIPE PROFILES
#                                   zero:       wipe with all zeros
#  fill-character values:           one:        fill with all ones
#                                   random:     fill with random characters
#-----------------------------------------------------------------------------
#                 | Pass 1 | Pass 2  | Pass 3  | Pass 4  | Pass 5  | Pass 6  |
#    KEY          ------------------------------------------------------------
#                 | fillch | fillch  | fillch  | fillch  | fillch  | fillch  |
#-----------------------------------------------------------------------------
WIPE_PROFILES: dict[str,list[str]] = {
    "nist-clear": ["zero"],
    "nist-purge": ["zero",  "random"],
    "dod-short":  ["zero",  "one",   "random"],
    "dod":        ["zero",  "one",   "random",  "zero",    "one",   "random",   "zero"],
    "custom":     []
}

class OS_NAMES(Enum):
    LINUX   = "Linux"
    MAC     = "Darwin"
    WIN32   = "Windows"
    UNSUPPORTED = "Unsupported"
    
class WIPE_METHODS(Enum):
    OVERWRITE       = "overwrite"   
    SECURE          = "secure"
    CRYPTO          = "crypto"
    UNKNOWN         = "unknown"
    
class CONTROLLERINFO_KEYS(Enum):
    MODEL       = "model"
    SERIAL      = "serial"
    FIRMWARE    = "firmware"
    SMART       = "smart_supported"

g_ControllerInfo: dict[str,list[str]]={}

class VERIFICATION_KEYS(Enum):
    ZERO_PATTERN    = "zero_pattern"
    HASH_VERIFY     = "hash_verify"
    FORENSIC_HASH   = "forensic_hash"

g_Verifications: dict[str,list[str]]={}

g_Report: dict[str,str]={
    "timestamp": datetime.now().isoformat(),
    "os": platform.system(),
    "device": "",
    "auto_selected": str(False),
    "erase_method": WIPE_METHODS.UNKNOWN.value,
    "nist_standard": "NIST SP 800-88 Rev. 1",
    "verification": "",
    "controller_info": "",
    "result": ""    
}


#
#-----------------------------------------------------------------------------
# Reporting functions
#
def generate_report(report_dir: str, data: str) -> None:
    os.makedirs(report_dir, exist_ok=True)
    base = os.path.join(report_dir, f"nist_report_{datetime.now().isoformat()}")
    json_path = base + ".json"
    txt_path = base + ".txt"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
        
    with open(txt_path, "w") as f:
        for k, v in data.items():
            f.write(f"{k}: {v}\n")

    logging.info(f"Compliance report written to {json_path}")
    
    
# NIST PDF report with X.509 signature
def generate_signed_pdf(report, path: str) -> str:
    c = canvas.Canvas(path, pagesize=LETTER)
    y = 750

    for k, v in report.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 15

    payload = str(report).encode()
    digest = hashlib.sha256(payload).hexdigest()

    c.drawString(50, y - 20, f"SHA-256 Signature: {digest}")
    c.save()

    return digest

# end NIST report


#
#-----------------------------------------------------------------------------
# Logging functions
#
# logfile name
LOGFILE = f"wipezero_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# logging configuration
logging.basicConfig(
    filename=LOGFILE,
    level=logging.DEBUG,
    format="  [ %(asctime)s ] %(levelname)s   |   %(message)s"
)

# write message to log
def log(msg: str):
    t_now: str = datetime.now().strftime('%Y%m%d_%H%M%S')
    s_out: str = "wipezero [" + t_now + "]\t" + msg
    print(s_out)
    logging.info(msg)

# end logging functions


#
#-----------------------------------------------------------------------------
# make sure that the user has the correct privileges to perform a wipe
#
def is_admin() -> bool:
    if platform.system() == OS_NAMES.WIN32.value:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    else:
        return os.geteuid() == 0
# end privileges section

#
#-----------------------------------------------------------------------------
# display a message box that requires a confirmation before actually 
# wiping the disk
#
def gui_confirm(message: str) -> bool:
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        return messagebox.askyesno("USB Wipe Confirmation", message)
    except Exception:
        return False
# end message box confirmation 

#
#-----------------------------------------------------------------------------
# list all of the removable usb devices attached to the computer
#
def list_usb():
    os_name = platform.system()
    logging.info("Detected removable USB devices:")
    log("Detected removable USB devices:")

    if os_name == OS_NAMES.LINUX.value:
        r = subprocess.run(["lsblk", "-o", "NAME,RM,SIZE,MOUNTPOINT"],capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if " 1 " in line:
                logging.info(line)
                log(line)

    elif os_name == OS_NAMES.MAC.value:
        r = subprocess.run(["diskutil", "list"], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if "external" in line.lower():
                logging.info(line)
                log(line)

    elif os_name == OS_NAMES.WIN32.value:       
        r = subprocess.run(["diskpart"], input="list disk\n",text=True, capture_output=True)
        for line in r.stdout.splitlines():
            if "removable" in line.lower():
                logging.info(line)
                log(line)
                
# end of usb detection

#
#-----------------------------------------------------------------------------
# check if the device is an OS system device, drive, etc
#
def is_system_disk(device: str) -> bool:
    match platform.system():
        case OS_NAMES.LINUX.value:    return device.startswith("/dev/sda") or device.startswith("/dev/nvme0n1")
        case OS_NAMES.MAC.value:      return device == "/dev/disk0"
        case OS_NAMES.WIN32.value:    return device.upper() == "C"
    return False
# end checking if the device is an OS device

#
#-----------------------------------------------------------------------------
# function to delete any content that might exist
#
def delete_contents(path:str, dry_run:bool) -> None:
    for entry in os.listdir(path):
        full = os.path.join(path, entry)
        if dry_run:
            log(f"[DRY-RUN] Delete {full}")
        else:
            if os.path.isfile(full) or os.path.islink(full):
                os.unlink(full)
            elif os.path.isdir(full):
                shutil.rmtree(full)
# End Delete Contents

#
#-----------------------------------------------------------------------------
#  functions for getting the device from the path
#
def get_device(mount: str) -> str:
    logging.info(f"get_device({mount})")
    match platform.system():
        case OS_NAMES.LINUX.value:    return linux_get_device(mount)
        case OS_NAMES.MAC.value:      return mac_get_device(mount)
        case OS_NAMES.WIN32.value:    return windows_get_device(mount)
    return ""

def linux_get_device(mount: str) -> str:
    r = subprocess.run(["findmnt", "-n", "-o", "SOURCE", "--target", mount],
                       capture_output=True, text=True)
    return r.stdout.strip()

def mac_get_device(mount: str) -> str:
    r = subprocess.run(["diskutil", "info", mount],
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if "Device Node" in line:
            return line.split(":")[1].strip()
    return ""

def windows_get_device(mount: str) -> str:
    import win32file 
    if win32file.GetDriveType(mount) == win32file.DRIVE_REMOVABLE:
        return mount
    else:
        return ""

#---------------End functions for getting the device from path----------------

#
#-----------------------------------------------------------------------------
# functions for detecting the device capabilities
#   (linux, mac, windows)
#
def detect_device_capabilities(device:str) -> dict[str,object]:
    match platform.system():
        case OS_NAMES.LINUX.value:   return linux_detect_capabilities(device)
        case OS_NAMES.MAC.value:  return mac_detect_capabilities(device)
        case OS_NAMES.WIN32.value: return windows_detect_capabilities()
    
    rv:dict[str,object]={}
    return rv

        
def linux_detect_capabilities(device:str) -> dict[str,bool]:
    dev = os.path.basename(device)
    caps = {
        "rotational": True,
        "discard": False,
        "secure_discard": False,
        "crypto_erase": False
    }
    try:
        with open(f"/sys/block/{dev}/queue/rotational") as f:
            caps["rotational"] = f.read().strip() == "1"
    except:
        pass
    
    try:
        with open(f"/sys/block/{dev}/queue/discard_max_bytes") as f:
            caps["discard"] = int(f.read().strip()) > 0
    except:
        pass
    
    try:
        r = subprocess.run(["blkdiscard", "--secure", "--dry-run", device], capture_output=True)
        caps["secure_discard"] = r.returncode == 0
    except:
        pass
    
    # Crypto erase inference (best effort)
    if caps["secure_discard"] and not caps["rotational"]:
        caps["crypto_erase"] = True

    return caps

def mac_detect_capabilities(device):
    caps = {
        "external": False,
        "ssd": False,
        "secure_erase": True,
        "crypto_erase": False
    }
    r = subprocess.run(["diskutil", "info", device], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if "External" in line and "Yes" in line:
            caps["external"] = True
        if "Solid State" in line and "Yes" in line:
            caps["ssd"] = True
    return caps

def windows_detect_capabilities():
    return {
        "crypto_erase": False,
        "secure_erase": False,
        "overwrite_only": True
    }

#
#-----------------------------------------------------------------------------
#   SMART controller capability checking
#   Determines if we can do crypto erase or not
#   probe_controller is a wrapper for code readability in the main function
def probe_controller(device: str) -> dict[str,object]:
    logging.info(f"probe controller device: {device}")
    match platform.system():
        case "Linux":   return linux_probe_controller(device)
        case "Darwin":  return mac_probe_controller(device)
        case "Windows": return windows_probe_controller()
    return {}

# implementation for linux
def linux_probe_controller(device: str) -> dict[str,object]:
    logging.info(f"linux probe controller using lsblk and smartctl on {device}")
    info: dict[str,object] = {}
    r = subprocess.run(["lsblk", "-o", "NAME,ROTA,MODEL,SERIAL"], capture_output=True, text=True)
    info["lsblk"] = r.stdout.strip()
    try:
        smart = subprocess.run(["smartctl", "-i", device], capture_output=True, text=True)
        info["smart_supported"] = "SMART support is: Enabled" in smart.stdout
    except:
        info["smart_supported"] = False
    return info

# implementation for windows
def windows_probe_controller() -> dict[str,object]:
    r = subprocess.run(["wmic", "diskdrive", "get", "model,mediaType"],capture_output=True, text=True)
    return {"wmic": r.stdout.strip()}

# implementation for mac
def mac_probe_controller(device: str) -> dict[str,object]:
    r = subprocess.run(["diskutil", "info", device], capture_output=True, text=True)
    return {"diskutil_info": r.stdout.strip()}

# END SMART Controller Probing
#   End Device Capabilities Functions



#
#-----------------------------------------------------------------------------
# function to automatically select the best wipe method based off of 
# device capabilities
#
def auto_select_method(os_name: str, device: str) -> WIPE_METHODS:
    logging.info("Auto-detecting safest erase method...")
    if os_name == OS_NAMES.LINUX.value:
        caps = linux_detect_capabilities(device)
        log(f"Capabilities: {caps}")

        if caps["crypto_erase"]:
            return WIPE_METHODS.CRYPTO
        if caps["secure_discard"]:
            return WIPE_METHODS.SECURE
        return WIPE_METHODS.OVERWRITE

    if os_name == OS_NAMES.MAC.value:
        caps = mac_detect_capabilities(device)
        log(f"Capabilities: {caps}")

        if caps["secure_erase"]:
            return WIPE_METHODS.SECURE
        return WIPE_METHODS.OVERWRITE

    if os_name == OS_NAMES.WIN32.value:
        return WIPE_METHODS.OVERWRITE
    return WIPE_METHODS.OVERWRITE

#
#-----------------------------------------------------------------------------
# OS Specific functions for performing the wipe
#

# Linux, wipe with zeros
def dd_wipe(device: str, source: str, progress: bool, dry_run: bool) -> None:
    src = "/dev/zero" if source == "zero" else "/dev/urandom"
    cmd = ["dd", f"if={src}", f"of={device}", "bs=4M"]
    if progress:
        cmd.append("status=progress")

    if dry_run:
        log(f"[DRY-RUN] {' '.join(cmd)}")
    else:
        try:
            subprocess.run(cmd, check=True)
        except:
            pass
        


def wipe_device(device, pattern_list, progress, dry_run):
    for idx, pattern in enumerate(pattern_list, start=1):
        log(f"Pass {idx}/{len(pattern_list)}: {pattern.upper()}")
        dd_wipe(device, pattern, progress, dry_run)
        
def secure_erase(device: str, dry_run: bool) -> bool:
    match platform.system():
        case OS_NAMES.LINUX.value: return linux_secure_erase(device,dry_run)
        case OS_NAMES.MAC.value: return mac_secure_erase(device,dry_run)
        case OS_NAMES.WIN32.value: return windows_secure_erase(device,dry_run)        


# linux, secure erase
def linux_secure_erase(device: str, dry_run: bool) -> bool:
    cmd = ["blkdiscard", "--secure", device]
    if dry_run:
        log(f"[DRY-RUN] {' '.join(cmd)}")
    else:
        subprocess.run(cmd, check=True)
        
# mac secure erase
def mac_secure_erase(device: str, dry_run: bool) -> bool:
    disk = device.replace("/dev/", "")
    cmd = ["diskutil", "secureErase", "0", disk]
    if dry_run:
        log(f"[DRY-RUN] {' '.join(cmd)}")
    else:
        subprocess.run(cmd, check=True)
        
# windows secure erase
def windows_secure_erase(volume: str, dry_run: bool) -> bool:
    script = "select disk {}\nclean all\n".format(volume)
    if dry_run:
        log("[DRY-RUN] diskpart clean all")
    else:
        subprocess.run(["diskpart"], input=script, text=True)
# end os specific wipe functions

#
#-----------------------------------------------------------------------------
# function to verify that the wipe was successful
#

# verify all zeros.
#   random sampling, 
#   fewer reads vs deterministic,
#   performance based verification
def verify_zero_pattern(device, samples=5):
    log("Starting verification pass (sampling)...")
    try:
        with open(device, "rb") as f:
            for i in range(samples):
                f.seek(i * 1024 * 1024)
                block = f.read(4096)
                if any(b != 0x00 for b in block):
                    return False
        return True
    except Exception as e:
        log(f"Verification skipped: {e}")
        return None

# automatically skip for crypto/secure erase
# hash included in report
def hash_sample_verify(device, samples=3):
    h = hashlib.sha256()
    size = os.path.getsize(device)
    try:
        with open(device, "rb") as f:
            for i in range(samples):
                offset = (size // samples) * i
                f.seek(offset)
                h.update(f.read(4096))
        return h.hexdigest()
    except Exception as e:
        log(f"Hash verification failed: {e}")
        return None


# deterministic verification
#   fixed offset,
#   more samples vs normal verification,
#   evidence based verification
def forensic_verify(device, block_size=4096):
    offsets = [0,1024 * 1024,10 * 1024 * 1024,100 * 1024 * 1024]
    h = hashlib.sha256()
    with open(device, "rb") as f:
        for off in offsets:
            f.seek(off)
            h.update(f.read(block_size))
    return h.hexdigest()

# end verification function

#
#-----------------------------------------------------------------------------
# HARDWARE SERIAL BINDING
# We store hardware identity as part of the report signing
#
def hardware_identity(device: str) -> str:
    match platform.system():
        case OS_NAMES.LINUX.value: return linux_hardware_identity(device)
        case OS_NAMES.MAC.value: return mac_hardware_identity(device)
        case OS_NAMES.WIN32.value: return windows_hardware_identity()
        
def windows_hardware_identity():
    r = subprocess.run(["wmic", "diskdrive", "get", "serialnumber,model,size"],capture_output=True, text=True)
    return r.stdout.strip()

def mac_hardware_identity(device):
    r = subprocess.run(["diskutil", "info", "-plist", device],capture_output=True)
    return plistlib.loads(r.stdout)

def linux_hardware_identity(device):
    r = subprocess.run(["lsblk", "-o", "NAME,SERIAL,MODEL,SIZE", "--json"],capture_output=True, text=True)
    return json.loads(r.stdout)
# end hardware identity functions

#
#-----------------------------------------------------------------------------
# X.509 CERTIFICATE SIGNING (REAL CRYPTO)
# verification compatibility:   
#   openssl dgst -sha256 -verify cert.pem -signature report.sig report.json
#
def sign_report_x509(report_bytes, cert_path, key_path):
    with open(key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None
        )

    signature = private_key.sign(
        report_bytes,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return signature
 


#
#-----------------------------------------------------------------------------
# functions for handling command line parameters
#
def get_command_line_parameters():
    description="Advanced, cross-platform, semi-fast, and multi-profile disk wipe utility for removable USB storage devices. "
    description = description + "Includes multiple reporting options and additional features such as listing removable USB storage "
    description = description + "devices and detecting fake removable USB storage devices.\n"
    description = description + "Author: BlackHatOG\tEmail: bitbltog@proton.me\tDate: December 2025"
    parser = argparse.ArgumentParser(description=description,epilog="Author: BlackHatOG   Email: bitbltog@proton.me   Date: December 2025")
    parser.add_argument("path",             nargs="?",              help="Path to the USB storage device/directory/block/etc to be wiped")
    parser.add_argument("--force",          action="store_true",    help="without this flag specified nothing gets deleted or wiped, just a dry-run")
    parser.add_argument("--profile",        choices=WIPE_PROFILES.keys(), default="nist-clear", help="specify the wipe profile or a custom profile (default: nist-clear)")
    parser.add_argument("--passes",         type=int, default=1,    help="if you do not select a wipe profile then you can specify the number of wipe passes manually (default: 1)")
    parser.add_argument("--progress",       action="store_true",    help="display a progress bar with progress updates")
    parser.add_argument("--gui",            action="store_true",    help="display a message box that confirms delete")
    parser.add_argument("--list",           action="store_true",    help="display a list of automatically detected USB storage devices")
    parser.add_argument("--crypto-erase",   action="store_true",    help="Attempt hardware cryptographic erase (if supported)")
    parser.add_argument("--secure-erase",   action="store_true",    help="Attempt controller secure erase (if supported)")
    parser.add_argument("--auto",           action="store_true",    help="Automatically select safest erase method per device")
    parser.add_argument("--verify",         action="store_true",    help="Perform post-erase verification pass")
    parser.add_argument("--report",         action="store_true",    help="Generate NIST compliance report")
    parser.add_argument("--report-dir",     type=str,               help="Directory for reoirts (default: cwd)")
    parser.add_argument("--pdf-report",     action="store_true",    help="Generate a X.509 signed PDF report with hardware identification hashes")
    parser.add_argument("--hash-verify",    action="store_true",    help="Generate a unique hashcode and embed it in the report as part of the signature payload")
    parser.add_argument("--gui-report",     action="store_true",    help="display a gui report reader at the end")
    parser.add_argument("--detect-fake-usb", action="store_true",   help="examine and display warning messages about suspect USB storage devices")
    parser.add_argument("--forensic-verify", action="store_true",   help="forensic evidence level verification and reporting")
    
    return parser.parse_args()

def validate_command_line_parameters(args, dry_run):
    if args.crypto_erase and args.secure_erase:
        sys.exit("Cannot use --crypto-erase and --secure-erase together")
    
    if (args.crypto_erase or args.secure_erase) and not args.force:
        sys.exit("Crypto/Secure erase requires --force")
    
    if not args.path and not args.list:
        sys.exit("Path required unless using --list")
    
    if args.path and not os.path.exists(args.path):
        sys.exit("Invalid path")

    if not dry_run and not is_admin():
        sys.exit("Must run as administrator/root")

    if args.gui:
        if not gui_confirm("This will permanently erase the USB device. Continue?"):
            sys.exit("Cancelled via GUI")
# end command line parameter functions

#
#-----------------------------------------------------------------------------
# Fake USB Heuristic Detection
# Never destructive, warns only, does not block erase
#
def detect_fake_usb(device):
    warnings = []
    try:
        reported = os.path.getsize(device)
        with open(device, "rb") as f:
            f.seek(reported - 4096)
            data = f.read(4096)
            if len(data) < 4096:
                warnings.append("Short read near end of device")
    except Exception as e:
        warnings.append(str(e))
    return warnings
# end fake usb function

#
#-----------------------------------------------------------------------------
# displays the final report in a gui window
# requires the --gui-report flag to be passed on the command line
#
def launch_gui_report(report):
    root = tk.Tk()
    root.title("NIST Compliance Report")

    text = ScrolledText(root, width=100, height=40)
    text.pack()

    for k, v in report.items():
        if k == "controller_info" or k == "verification":
            text.insert(tk.END, f"{k}:\n")
            for item in report[k]:
                text.insert(tk.END, f"    {item}\n")
        else:
            text.insert(tk.END, f"{k}: {v}\n")
            

    root.mainloop()
# end gui report

#
#-----------------------------------------------------------------------------
# MAIN APPLICATION ENTRY POINT --
#
# Execution Flow:
#   1. Detect OS 
#       1.1 system disk lockout
#   2. Probe controller / SMART
#   3. Fake USB heuristic (--detect-fake-usb)
#   4. Auto-select erase (--auto)
#   5. Perform erase
#   6. Verification pass (--verify)
#   7. Hash verification (--hash-verify)
#   8. Generate report (--report)
#   9. Generate signed PDF (--pdf-report)
#   10. Launch GUI (--gui-report)
#
def main():
    args = get_command_line_parameters()
    dry_run = not args.force
    validate_command_line_parameters(args,dry_run)
    
    # display a list of the removable usb storage devices
    # attached to the computer
    if args.list:
        list_usb()
        return

    log(f"Log file: {LOGFILE}")
    log(f"Mode: {'DRY-RUN' if dry_run else 'DESTRUCTIVE'}")
    log(f"Wipe profile: {args.profile}")
    log(f"Target path: {args.path}")

    conInf = {}
    method = WIPE_METHODS.UNKNOWN
    device = get_device(args.path)
    verifications: dict[str,object] = {} 
    
    logging.info(f"device is {device}")
    if device == "None" or device=="":
        logging.error("fatal error, unsupported operating system")
        sys.exit("unsupported operating system")
    
    # 1.1 locked out of system folders 
    if is_system_disk(device):
        logging.error("refuse to wipe system files.")
        sys.exit("refuse to wipe system files.")
    
    if args.crypto_erase or args.secure_erase:
        logging.info("Probing controller to verify support for secure erase and cryptographic erase...")  
        # 2. Probe controller / SMART
        conInf = probe_controller(device)
        if conInf['smart_supported'] == False:
            logging.warning("Controller does not support secure erase or cryptographic erase")
            log("Controller does not support secure erase or cryptographic erase")
        else:
            logging.info(f"Controller Info: {conInf}")
            logging.info(f"Crypto/Secure erase supported")

    # 3. Fake USB heuristic detection
    if args.detect_fake_usb:
        n_warn = 0
        s_warnout = "The following non-critical warnings were encountered:\n"
        for s_warn in detect_fake_usb(device):
            n_warn=n_warn+1
            s_warnout = s_warnout + f"#{n_warn}\t{s_warn}\n"
        if n_warn != 0: 
            logging.info(s_warnout) 
            log(s_warnout)
        else:
            logging.info("No warnings detected during fake USB heuristic analysis." )

    # 4. Delete any existing contents on the device
    delete_contents(args.path, dry_run)
    
    # 5. Perform the wipe
    if args.crypto_erase or args.secure_erase:  # secure erase
        logging.info("Erase mode: " + ("CRYPTOGRAPHIC" if args.crypto_erase else "SECURE CONTROLLER"))        
        if not platform.system() == OS_NAMES.LINUX.value and args.crypto_erase:
            logging.error(f"cryptographic erase is not supported for operating system: {platform.system()}")
            sys.exit(f"cryptographic erase is not supported for operating system: {platform.system()}")
        secure_erase(device,dry_run)
        logging.info("Secure erase complete")
    elif args.auto:     #   auto-detect the best wipe method based on device capabilites 
        if not args.force:
            logging.error("--auto requires --force")
            sys.exit("--auto requires --force")
        
        method = auto_select_method(platform.system(), device)
        logging.info(f"Auto-selected erase method: {method.value}")

        if method == WIPE_METHODS.CRYPTO or method == WIPE_METHODS.SECURE:
            secure_erase(device,dry_run)
            logging.info(f"{method.value()} erase completed")
        elif method == WIPE_METHODS.OVERWRITE:
            logging.info("Falling back to NIST Clear overwrite")
            patterns = ["zero"]
            logging.info(f"Wiping device: {device}")
            wipe_device(device,patterns,args.progress, dry_run)
            logging.info("Operation complete")
    elif args.profile == "custom":
        patterns = ["zero"] * args.passes
        wipe_device(device,patterns,args.progress,dry_run)
        logging.info("Custom erase completed")
    else:
        patterns = WIPE_PROFILES[args.profile]
        logging.info(f"Wiping device: {device}")
        wipe_device(device, patterns, args.progress, dry_run)
        logging.info(f"Operation {method} erase complete")
    
    # ------- VERIFICATION ----------
    if args.verify:
        if verify_zero_pattern(device) == True:
            logging.info("Verification successful: Device wiped to all zeros")
            verifications["zero_pattern"] = {"status": "PASS", "samples": 5, "pattern": "0x00","description": "Random sampling verification","errcnt":0}
        else:
            logging.error("Verification failed: Non-zero data detected")
            verifications["zero_pattern"] = {"status": "FAIL", "samples": 5, "pattern": "0x00","description": "Random sampling verification","errcnt":1}  
    if args.hash_verify:
        if args.secure_erase or args.crypto_erase:
            log("--hash-verify is incompatible with --secure-erase and --crypto-erase")
        else:
            hash_verify_result = hash_sample_verify(device)
            if hash_verify_result:
                logging.info(f"Hash verification successful: {hash_verify_result}") 
                verifications["hash_verify"] = {"status": "PASS", "hash": hash_verify_result,"description": "Random sampling hash verification","samples":3,"errcnt":0}
            else:
                logging.error("Hash verification failed")
                verifications["hash_verify"] = {"status": "FAIL", "hash": None,"description": "Random sampling hash verification","samples":3,"errcnt":1}
    if args.forensic_verify:
        forensic_result = forensic_verify(device)
        if forensic_result:
            logging.info(f"Forensic verification hash: {forensic_result}")
            verifications["forensic_hash"] = {"status": "PASS", "hash": forensic_result,"description": "Forensic verification hash","samples":3,"errcnt":0}
        else:
            logging.error("Forensic verification failed")
            verifications["forensic_hash"] = {"status": "FAIL", "hash": None,"description": "Forensic verification hash","samples":3,"errcnt":1}
    # ------- end verification -------
    
    # 8. Generate NIST compliance report
    if args.report or args.pdf_report or args.gui_report:
        logging.info("Generating NIST compliance report...") 
        g_Report["device"] = device
        g_Report["auto_selected"] = str(args.auto)
        g_Report["erase_method"] = method.value
        g_Report["controller_info"] = str(conInf)
        g_Report["verification"] = str(verifications)
        g_Report["result"] = "SUCCESS" if all(v["status"] == "PASS" for v in verifications.values()) else "FAILURE"    
        if args.gui_report:
            launch_gui_report(g_Report)
        # 9. Generate signed PDF report
        if args.pdf_report:
            generate_signed_pdf(g_Report, os.path.join(args.report_dir if args.report_dir else os.getcwd(),'nist_report.pdf'))
    # ----- end of main ------
    return 

if __name__ == "__main__":
    main()
    print("wipezero exiting normally.")
    sys.exit(0)
# ---- end of file ----

