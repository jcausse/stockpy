echo "This script will install all dependencies needed to run StockPy, and will download the latest version of Stockfish"
sudo echo "" # Request password

download_ok=0

# Download stockfish
printf "Downloading Stockfish...\n"
wget -q --show-progress -O stockfish.tar https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar
if [ $? -eq 0 ]; then
    printf "Download successful.\n"
    printf "Extracting... "
    tar -xf stockfish.tar > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        printf "Extraction successful.\n"
        download_ok=1
    else
        printf "Extraction failed.\n"
    fi
else
    printf "Download failed. Please check the URL or your internet connection.\n"
fi
rm stockfish.tar

if [ $download_ok -ne 1 ];then
  exit 1
fi

# Install dependencies
printf "Installing dependencies... "
sudo apt-get --yes update > /dev/null 2>&1
sudo apt-get --yes install python3 python3-pip python3-venv > /dev/null 2>&1
sudo apt-get --yes install libxcb-cursor0 > /dev/null 2>&1
python3 -m pip install --upgrade pip > /dev/null 2>&1
printf "Done.\n"

# Create Virtual Environment and install Python dependencies
printf "Creating Python Virtual Environment... "
python3 -m venv .venv > /dev/null 2>&1
printf "Done.\n"
printf "Installing Python dependencies... "
python3 -m pip install -r requirements.txt > /dev/null 2>&1
printf "Done.\n"

# Miscellaneous
chmod a+x scripts/ubuntu/run.sh
