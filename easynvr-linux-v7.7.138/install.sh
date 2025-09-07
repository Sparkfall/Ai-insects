#!/bin/bash

# ANSI escape codes
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Reset color

# Read TOML file
TOML_FILE="./configs/config.toml"

# Check if EasyNVR service is already installed and running
if systemctl is-active --quiet easynvr; then
    echo -e "  ${YELLOW}[WARNING] EasyNVR Service is already installed.${NC}"
    exit 1
fi

echo -e "${GREEN}=============================== Environment Checking ================================${NC}"
echo

# Check if the user is root
if [ "$(id -u)" -eq 0 ]; then
    echo -e "  ${GREEN}****** The user is the root user, loading. ******${NC}"
else
    # Check if the user has sudo privileges
    if sudo -n true 2>/dev/null; then
        echo -e "  ${GREEN}****** The current user has sudo privileges, continue execution. ******${NC}"
        # Execute the script itself with sudo
        sudo "$0"
        exit 0
    else
        echo -e "  ${RED}****** Use the following method to execute the start.sh script. ******${NC}"
        echo -e "  ${RED}****** 1.Switch to root user and run ./start.sh ******${NC}"
        echo -e "  ${RED}****** 2.Try running sudo ./start.sh command. ******${NC}"
        echo -e "${RED}***************************** Information ***********************************${NC}"
        exit 1
    fi
fi

fileExtension=1
# Check if the file exists
if [ ! -f "$TOML_FILE" ]; then
    fileExtension=0
    echo
    echo -e "  ${YELLOW}Warning: Configuration file $TOML_FILE does not exist.${NC}"
    echo
    echo -e "  ${YELLOW}Will be checking the default port status...${NC}"
fi

testNum=0
allPortsFree=1

echo -e "${GREEN}[Port Status]----------------------------------[Port Number]--+${NC}"

check_port() {
    local port=$1
    port="$(echo "$port" | sed 's/\r$//')"
    port=$(echo "$port" | sed "s/^'\(.*\)'\$/\1/")
    local desc=$2

    if [ "$port" -eq 0 ]; then
        return
    fi

    while true; do
        local pid=$(sudo lsof -t -i :$port)
        if [ -n "$pid" ]; then
            # Get process name
            local processName=$(sudo lsof -i :$port | awk 'NR==2 {print $1}')
            echo -e "${RED}|  [ NO ]  | Checking ${desc} port:${port}    | Process ID:$pid Process Name:$processName${NC}"
            let testNum++
            echo -n "This port is already in use. Force to kill this process? (Y/N): "
            read -n 1 choice
            if [[ "$choice" =~ ^[Yy]$ ]]; then
                sudo kill -9 $pid
                if [ $? -eq 0 ]; then
                    echo -e " [Done]"
                    # Reset testNum after killing the process
                    testNum=0
                    continue  # Re-check the port
                else
                    echo -e " Failed to terminate the process with PID $pid."
                    allPortsFree=0
                    break
                fi
            else
                echo -e " [No]"
                allPortsFree=0
                break
            fi
        else
            echo -e "${GREEN}|  [ OK ]  | Checking ${desc} port:${port}    | ${NC}"
            break
        fi
    done
}

check_udp_port() {
    local port=$1
    local desc=$2

    # Remove single quotes from the port value
    port=$(echo "$port" | sed "s/^'\(.*\)'\$/\1/")

    # Check if the port is 0 or not a number
    if ! [[ "$port" =~ ^[0-9]+$ ]] || [ "$port" -eq 0 ]; then
        return
    fi

    while true; do
        # Use netstat to check UDP port
        local pid=$(sudo netstat -anp | grep -E "udp.*:$port " | awk '{print $7}' | cut -d'/' -f1)
        if [ -n "$pid" ]; then
            # Get process name
            local processName=$(ps -p $pid -o comm=)
            echo -e "${RED}|  [ NO ]  | Checking ${desc} port:${port}    | Process ID:$pid Process Name:$processName${NC}"
            let testNum++
            echo -n "This port is already in use. Force to kill this process? (Y/N): "
            read -n 1 choice
            if [[ "$choice" =~ ^[Yy]$ ]]; then
                sudo kill -9 $pid
                if [ $? -eq 0 ]; then
                    echo -e " [Done]"
                    testNum=0
                    continue
                else
                    echo -e " Failed to terminate the process with PID $pid."
                    allPortsFree=0
                    break
                fi
            else
                echo -e " [No]"
                allPortsFree=0
                break
            fi
        else
            echo -e "${GREEN}|  [ OK ]  | Checking ${desc} port:${port}    | ${NC}"
            break
        fi
    done
}

files=()
if [ $fileExtension -eq 1 ]; then
    while read line; do
        files+=("$line")
    done < "$TOML_FILE"
elif [ $fileExtension -eq 0 ]; then
    files+=("Port = 10000")
    files+=("Port = 10010") # 占位符不能注释
    files+=("Port = 15060") # 占位符不能注释
    # files+=("HTTPPort = 28080")
    # files+=("HTTPSPort = 24433")
    # files+=("RTSPAddr = 25544")
    # files+=("RTMPAddr = 21935")
fi

PORTS=()
PortNum=0

# Parse array content
for file in "${files[@]}"; do
    if echo "$file" | awk -F' *= *' '{ if ($2 ~ /^[^ ]/) { gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2; } }' | grep -q '.'; then
        key=$(echo "$file" | awk -F'=' '{gsub(/^[ \t]+|[ \t]+$/, "", $1); print $1}')
        value=$(echo "$file" | awk -F' *= *' '{ gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2 }')

        if [[ "$key" == "Port" ]]; then
            let PortNum++
            if [[ $PortNum == 1 ]]; then
                check_port "$value" "HTTP(TCP)                "
            fi
        fi

        #if [[ "$key" == "HTTPPort" ]]; then
            #check_port "$value" "SMS-HTTP(TCP)            "
        #fi
    fi
done
echo -e "${GREEN}+-------------------------------------------------------------+${NC}"

# Final check for all ports
if [[ $testNum -gt 0 ]]; then
    allPortsFree=0
fi

echo
if [[ $allPortsFree -eq 1 ]]; then
    echo -e "  ${GREEN}All ports are free.${NC}"
else
    echo -e "  ${RED}One or more ports are occupied. Modify config.toml to change ports and restart again...${NC}"
    echo -e "  ${RED}Program startup failed${NC}"
    echo
    echo -e "${GREEN}=============================== Environment Checking ================================${NC}"
    echo -e "${RED}"
    echo "                                -----------------------"
    echo "                                |   _   _  ___    _   |"
    echo "                                |  | \ | |/ _ \  | |  |"
    echo "                                |  |  \| | | | | | |  |"
    echo "                                |  | |\  | |_| | |_|  |"
    echo "                                |  |_| \_|\___/  (_)  |"
    echo "                                |                     |"
    echo "                                -----------------------"
    echo -e "${NC}"
    exit 1
fi

echo
echo -e "${GREEN}=============================== Environment Checking ================================${NC}"

# Grant executable permissions
chmod +x ./easynvr
chmod +x ./ntd
chmod +x ./easynvr.com
chmod +x ./ffmpeg

# Install EasyNVR service
./easynvr install > /dev/null 2>&1

# Start EasyNVR service
./easynvr start > /dev/null 2>&1
echo
if systemctl is-active --quiet easynvr; then
    echo -e "  ${GREEN}[OK] EasyNVR Service has been installed and started successfully.${NC}"
    echo -e "${GREEN}"
    echo "                                -----------------------------"
    echo "                                |  __   _______ ____    _   |"
    echo "                                |  \ \ / / ____/ ___|  | |  |"
    echo "                                |   \ V /|  _| \___ \  | |  |"
    echo "                                |    | | | |___ ___) | |_|  |"
    echo "                                |    |_| |_____|____/  (_)  |"
    echo "                                |                           |"
    echo "                                -----------------------------"
    echo -e "${NC}"
else
    echo -e "  ${RED}[FALSE] EasyNVR Service failed to install and start.${NC}"
    echo -e "${RED}"
    echo "                                -----------------------"
    echo "                                |   _   _  ___    _   |"
    echo "                                |  | \ | |/ _ \  | |  |"
    echo "                                |  |  \| | | | | | |  |"
    echo "                                |  | |\  | |_| | |_|  |"
    echo "                                |  |_| \_|\___/  (_)  |"
    echo "                                |                     |"
    echo "                                -----------------------"
    echo -e "${NC}"
    exit 1
fi

exit 0