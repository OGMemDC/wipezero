#!/usr/bin/env bash
clear

cat << EOF
.........................................
.........................................
......@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.....
.....@@@@@@@@@@@@@@@@@@@@@.....@@@@@.....
.....@@...............@....@@@@...@@.....
.....@@......@..@@@@@@..@@.....@..@@.....
.....@@.........@.........@@@@@@..@@.....
.....@@......@..@@@@..@@@@@.......@@.....
.....@@...........@@@@@...........@@.....
.....@@...........................@@.....
.....@@...........................@@.....
.....@@...........................@@.....
.....@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.....
......@@@@@@@@@@@@@@@@@@@@@@@@@@@@@......
.........................................                                                                            
EOF
echo ""
echo "Welcome to the WipeZero Installer!"
echo ""

############################################
# Default installation settings
INSTALL_DIR="/opt/wipezero"
ICON="/usr/share/pixmaps/wipezero.png"
DESKTOP_FILE="/usr/share/applications/wipezero.desktop"
BIN_FILE="/usr/local/bin/wipezero"

##########################################
# Text Color Codes
RED='\033[0;31m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

############################################
# Check for root privileges
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}This script must be run as root.${NC}"
    exit 1 
fi

############################################
# Detect the platform
unameOut=$(uname -a)
case "${unameOut}" in
    *Microsoft*)     OS="WSL";; #must be first since Windows subsystem for linux will have Linux in the name too
    *microsoft*)     OS="WSL2";; #WARNING: My v2 uses ubuntu 20.4 at the moment slightly different name may not always work
    Linux*)     OS="Linux";;
    Darwin*)    OS="Mac";;
    CYGWIN*)    OS="Cygwin";;
    MINGW*)     OS="Windows";;
    *Msys)     OS="Windows";;
    *)          OS="UNKNOWN:${unameOut}"
esac
echo -e "${PURPLE}Detected ${OS} as our operating system.${NC}"
case "${OS}" in
    Linux*)     
        echo -e "    ${GREEN}Proceeding with Linux installation...${NC}"
        ;;
    WSL*|Windows*|Cygwin*|Mac*|UNKNOWN*)
        echo -e "    ${RED}WipeZero can only be installed on Linux systems at this time.${NC}"
        exit 1
        ;;
esac

####################################
# Confirm or modify installation settings
while [[ true  ]]; do
    echo "1. Installation Directory: ${INSTALL_DIR}"
    echo "2. Icon Path: ${ICON}"
    echo "3. Desktop File Path: ${DESKTOP_FILE}"
    echo "4. Binary Link Path: ${BIN_FILE}"  
    echo -e "${PURPLE}Select an option to modify (1-4) or press enter to accept all:${NC}"
    read -r choice
    if [[ -z "$choice" ]]; then
        break
        elif [[ -n "$choice" ]]; then
            case $choice in
                1)
                echo "Enter new installation directory:"
                read -r INSTALL_DIR
                ;;
                2)
                echo "Enter new icon path:"
                read -r ICON
                ;;
                3)
                echo "Enter new desktop file path:"
                read -r DESKTOP_FILE
                ;;
                4)
                echo "Enter new binary link path:"
                read -r BIN_FILE
                ;;
                *)
                echo -e "${RED}Invalid choice. Exiting.${NC}"
                exit 1
                ;;
            esac
    fi
done

############################################
# create the group wipezero if it does not 
# exist
if ! getent group wipezero > /dev/null 2>&1; then
    echo -e "${PURPLE}Creating group 'wipezero'...${NC}"
    groupadd wipezero
    if [[ $? -ne 0 ]]; then
        echo -e "    ${RED}Failed to create group 'wipezero'.${NC}"
        exit 1
    else
        echo -e "    ${GREEN}Group 'wipezero' created successfully.${NC}"
    fi
else
    echo -e "    ${GREEN}Group 'wipezero' already exists. Skipping creation${NC}"
fi

############################################
# Create installation directory
echo -e "${PURPLE}Creating installation directory at ${INSTALL_DIR}...${NC}"
if [[ -d "${INSTALL_DIR}" ]]; then
    echo -e "    ${GREEN}Installation directory already exists.${NC}"
elif [[ $(mkdir -p "${INSTALL_DIR}") -ne 0 ]]; then
    echo -e "    ${RED}Failed to create installation directory!${NC}"
    exit 1
else 
    echo -e "    ${GREEN}Installation directory created at ${INSTALL_DIR}.${NC}"
fi
if [[ ! -d "${INSTALL_DIR}" ]]; then
    echo -e "    ${RED}ERROR: ${INSTALL_DIR} does not exist!${NC}"
    exit 1
else 
    echo -e "    ${GREEN}${INSTALL_DIR}...${NC}"
fi 
if [[ ! -w "${INSTALL_DIR}" ]]; then
    echo -e "    ${RED}    ...is not writable!${NC}"
    exit 1
else
    echo -e "    ${GREEN}    ...is writable.${NC}" 
fi
if [[ ! -x "${INSTALL_DIR}" ]]; then
    echo "       ${RED}    ...is not accessible!${NC}"
    exit 1
else 
    echo -e "    ${GREEN}    ...is accessible.${NC}" 
fi
if [[ ! -r "${INSTALL_DIR}" ]]; then
    echo -e "    ${RED}    ...is not readable!${NC}"
    exit 1
else
    echo -e "    ${GREEN}    ...is readable.${NC}" 
fi
if [[ "$(ls -A ${INSTALL_DIR})" ]]; then
    echo -e "${PURPLE}${INSTALL_DIR} contains a previous version of WipeZero, removing...${NC}"
    rm -rf "${INSTALL_DIR}"/* &> /dev/null
    if [[ $? -ne 0 ]]; then
        echo -e "    ${RED}Failed to remove previous version of WipeZero!${NC}"
        exit 1
    else 
        echo -e "    ${GREEN}Removed previous version of WipeZero.${NC}"
    fi
fi

############################################
# Set ownership and permissions
echo -e "${PURPLE}Setting ownership and permissions for ${INSTALL_DIR}...${NC}"
chown root:wipezero "${INSTALL_DIR}" &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to set ownership of ${INSTALL_DIR} to root:wipezero!${NC}"
    exit 1
else 
    echo -e "    ${GREEN}Set ownership of ${INSTALL_DIR} to root:wipezero.${NC}"
fi
chmod 755 "${INSTALL_DIR}" &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to set permissions on ${INSTALL_DIR}!${NC}"
    exit 1
else 
    echo -e "    ${GREEN}Set permissions on ${INSTALL_DIR} to 755.${NC}"
fi   

############################################ 
# Copy files to installation directory
echo -e "${PURPLE}Copying files to ${INSTALL_DIR}...${NC}"
cp -r ./tests "${INSTALL_DIR}"/ &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to copy test files to ${INSTALL_DIR}.${NC}"
    exit 1
else
    echo -e "    ${GREEN}Test files copied to ${INSTALL_DIR}.${NC}"
fi
cp -r ./doc "${INSTALL_DIR}"/ &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to copy documentation files to ${INSTALL_DIR}.${NC}"
    exit 1
else
    echo -e "    ${GREEN}Documentation files copied to ${INSTALL_DIR}.${NC}"
fi
cp ./wipezero.py "${INSTALL_DIR}"/ &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to copy wipezero.py to ${INSTALL_DIR}.${NC}"
    exit 1
else
    # verify wipezero.py was copied
    if [[ -f "${INSTALL_DIR}/wipezero.py" ]]; then
        echo -e "    ${GREEN}wipezero.py copied to ${INSTALL_DIR}.${NC}"
    else
        echo -e "    ${RED}Failed to copy wipezero.py to ${INSTALL_DIR}.${NC}"
        exit 1
    fi
fi
cp ./README.md "${INSTALL_DIR}"/ &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to copy README.md to ${INSTALL_DIR}.${NC}"
    exit 1
else
    echo -e "    ${GREEN}README.md copied to ${INSTALL_DIR}.${NC}"
fi
cp ./LICENSE "${INSTALL_DIR}"/ &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to copy LICENSE to ${INSTALL_DIR}.${NC}"
    exit 1
else
    echo -e "    ${GREEN}LICENSE copied to ${INSTALL_DIR}.${NC}"
fi

############################################
# Set executable permissions
echo -e "${PURPLE}Setting executable permissions for ${INSTALL_DIR}/wipezero.py...${NC}"
chmod +x "${INSTALL_DIR}"/wipezero.py &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to set executable permissions on ${INSTALL_DIR}/wipezero.py.${NC}"
    exit 1
else 
    # verify that wipezero.py is executable
    if [[ -x "${INSTALL_DIR}/wipezero.py" ]]; then
        echo -e "    ${GREEN}...success${NC}"
    else
        echo -e "    ${RED}... ERROR! Failed to make ${INSTALL_DIR}/wipezero.py executable.${NC}"
        exit 1
    fi
fi  

############################################
# set ownership and permissions for all files
echo -e "${PURPLE}Setting ownership and permissions for all files in ${INSTALL_DIR}...${NC}"
chown -R root:wipezero "${INSTALL_DIR}"/* &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to set ownership of files to root:wipezero!${NC}"
    exit 1
else
    echo -e "    ${GREEN}Set ownership of files to root:wipezero.${NC}"
fi
chmod -R 750 "${INSTALL_DIR}"/* &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to set permissions on files in ${INSTALL_DIR}!${NC}"
    exit 1
else 
    echo -e "    ${GREEN}Set permissions on files in ${INSTALL_DIR} to 750.${NC}"
fi

############################################
# Create symbolic link
echo -e "${PURPLE}Creating symbolic link at ${BIN_FILE}...${NC}"
ln -sf "${INSTALL_DIR}"/wipezero.py "${BIN_FILE}" &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to create symbolic link at ${BIN_FILE}.${NC}"
    exit 1
else
    # verify that the symbolic link was created
    if [[ -L "${BIN_FILE}" ]]; then
        echo -e "    ${GREEN}Symbolic link created at ${BIN_FILE}.${NC}"
    else
        echo -e "    ${RED}Failed to create symbolic link at ${BIN_FILE}.${NC}"
        exit 1
    fi
    # verify that it is executable
    if [[ ! -x "${BIN_FILE}" ]]; then
        echo -e "    ${RED}Symbolic link creation failed; ${BIN_FILE} is not executable!${NC}"
        exit 1
    else
        echo -e "    ${GREEN}Symbolic link at ${BIN_FILE} is executable${NC}"
    fi
fi

############################################
# Copy icon
echo -e "${PURPLE}Copying icon to ${ICON}...${NC}"
cp -v ./doc/resources/wipezero_small.png "${ICON}" &> /dev/null
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to copy icon to ${ICON}!${NC}"
    exit 1
else 
    # verify that the icon was copied
    if [[ -f "${ICON}" ]]; then
        echo -e "    ${GREEN}Icon copied to ${ICON}.${NC}"
    else
        echo -e "    ${RED}Failed to copy icon to ${ICON}!${NC}"
        exit 1
    fi
    # set permissions for the icon
    chmod 644 "${ICON}" &> /dev/null
    if [[ $? -ne 0 ]]; then
        echo -e "    ${RED}Failed to set permissions on ${ICON}!${NC}"
        exit 1
    else 
        echo -e "    ${GREEN}Set permissions on ${ICON} to 644.${NC}"
    fi
fi

#############################################
# Create desktop entry
echo -e "${PURPLE}Creating desktop entry at ${DESKTOP_FILE}...${NC}"
if [[ ! -d "$(dirname ${DESKTOP_FILE})" ]]; then
    mkdir -p "$(dirname ${DESKTOP_FILE})" &> /dev/null
    if [[ $? -ne 0 ]]; then
        echo -e "    ${RED}Failed to create directory for desktop file at $(dirname ${DESKTOP_FILE})!${NC}"
        exit 1
    else 
        echo -e "    ${GREEN}Created directory for desktop file at $(dirname ${DESKTOP_FILE}).${NC}"
    fi
fi
if [[ -f "${DESKTOP_FILE}" ]]; then
    echo -e "${PURPLE}Existing desktop file found at ${DESKTOP_FILE}, removing...${NC}"
    rm -f "${DESKTOP_FILE}" &> /dev/null
    if [[ $? -ne 0 ]]; then
        echo -e "    ${RED}Failed to remove existing desktop file at ${DESKTOP_FILE}!${NC}"
        exit 1
    else
        echo -e "    ${GREEN}Removed existing desktop file at ${DESKTOP_FILE}.${NC}"
    fi
fi
echo "[Desktop Entry]\nName=WipeZero\nComment=Lightweight USB storage wipe utility for Linux, provides NIST & DoD level wipe functionality\nExec=${BIN_FILE}\nIcon=${ICON}\nTerminal=true\nType=Application\nCategories=Utility;" >> ${DESKTOP_FILE}
if [[ $? -ne 0 ]]; then
    echo -e "    ${RED}Failed to create desktop entry at ${DESKTOP_FILE}!${NC}"
    exit 1
else 
    # verify that the desktop file was created
    if [[ -f "${DESKTOP_FILE}" ]]; then
        echo -e "    ${GREEN}Desktop entry created.${NC}"
    else
        echo -e "    ${RED}Failed to create desktop entry at ${DESKTOP_FILE}!${NC}"
        exit 1
    fi
    # set permissions for desktop file
    chmod 644 "${DESKTOP_FILE}" &> /dev/null
    if [[ $? -ne 0 ]]; then
        echo -e "    ${RED}Failed to set permissions on ${DESKTOP_FILE}!${NC}"
        exit 1
    else
        echo -e "    ${GREEN}Set permissions on ${DESKTOP_FILE} to 644.${NC}"
        # Rebuild desktop database
        if command -v update-desktop-database &> /dev/null; then
            update-desktop-database "$(dirname ${DESKTOP_FILE})" &> /dev/null
            if [[ $? -ne 0 ]]; then
                echo -e "    ${RED}Failed to update desktop database.${NC}"
                exit 1
            else
                echo -e "    ${GREEN}Desktop database updated successfully.${NC}"
            fi
        fi
    fi
fi

############################################
# Installation complete
echo ""
echo "WipeZero installed successfully!"
echo "You can launch it from your application menu or by running 'wipezero' in the terminal."
exit 0