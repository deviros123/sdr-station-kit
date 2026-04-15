#!/bin/bash
# sdr-station-kit installer
# Installs OpenWebRX+ (Docker), configures SDR devices, deploys bookmarks and automation
# Tested on DragonOS (Debian 13 trixie) on Raspberry Pi 5

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_USER="${SUDO_USER:-$(whoami)}"
HOME_DIR="/home/$INSTALL_USER"

echo "============================================"
echo "  sdr-station-kit installer"
echo "============================================"
echo "Install user: $INSTALL_USER"
echo "Home dir: $HOME_DIR"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./install.sh"
    exit 1
fi

# 1. Blacklist DVB drivers
echo "[1/8] Configuring DVB driver blacklist..."
cp "$SCRIPT_DIR/config/blacklist-rtlsdr.conf" /etc/modprobe.d/blacklist-rtlsdr.conf

# 2. Install Docker
echo "[2/8] Installing Docker..."
if ! command -v docker &> /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io
    usermod -aG docker "$INSTALL_USER"
    systemctl enable docker
    systemctl start docker
else
    echo "  Docker already installed"
fi

# 3. Install dependencies
echo "[3/8] Installing dependencies..."
apt-get install -y sox python3-soapysdr soapysdr-tools 2>/dev/null || true
pip3 install soapy_power numpy Pillow --break-system-packages 2>/dev/null || true

# 4. Pull and start OpenWebRX+
echo "[4/8] Starting OpenWebRX+ Docker container..."
docker pull slechev/openwebrxplus-softmbe:latest

mkdir -p "$HOME_DIR/openwebrx-config/bookmarks.d"
mkdir -p "$HOME_DIR/openwebrx-data"
mkdir -p "$HOME_DIR/weatherfax/wav"
mkdir -p "$HOME_DIR/weatherfax/images"
mkdir -p "$HOME_DIR/weatherfax/latest"
mkdir -p "$HOME_DIR/weather-text"

# Copy configs
cp "$SCRIPT_DIR/config/bookmarks/seattle.json" "$HOME_DIR/openwebrx-config/bookmarks.d/seattle.json"
if [ ! -f "$HOME_DIR/openwebrx-data/settings.json" ]; then
    cp "$SCRIPT_DIR/config/openwebrx/settings.json" "$HOME_DIR/openwebrx-data/settings.json"
fi

docker rm -f openwebrx 2>/dev/null || true
docker run -d \
    --name openwebrx \
    --restart unless-stopped \
    -p 8073:8073 \
    --device /dev/bus/usb \
    -v "$HOME_DIR/openwebrx-config:/etc/openwebrx" \
    -v "$HOME_DIR/openwebrx-data:/var/lib/openwebrx" \
    -v "$HOME_DIR/weatherfax:/usr/lib/python3/dist-packages/htdocs/weatherfax" \
    slechev/openwebrxplus-softmbe:latest

# 5. Create admin user
echo "[5/8] Creating admin user..."
sleep 15
echo -e "dragon\ndragon" | docker exec -i openwebrx openwebrx admin adduser admin 2>/dev/null || true

# 6. Install scripts
echo "[6/8] Installing scripts..."
cp "$SCRIPT_DIR/bin/"*.sh "$HOME_DIR/"
cp "$SCRIPT_DIR/bin/"*.py "$HOME_DIR/"
chmod +x "$HOME_DIR/"*.sh "$HOME_DIR/"*.py

# 7. Generate bookmarks page
echo "[7/8] Generating bookmarks page..."
python3 "$HOME_DIR/gen_bookmarks.py"
docker cp "$HOME_DIR/openwebrx-config/seattle-bookmarks.html" openwebrx:/usr/lib/python3/dist-packages/htdocs/seattle-bookmarks.html

# 8. Install crontab
echo "[8/8] Installing capture schedule..."
crontab "$SCRIPT_DIR/config/crontab"

# Install inject service for bookmarks persistence
cp "$SCRIPT_DIR/config/systemd/sdr-inject.service" /etc/systemd/system/ 2>/dev/null || true
systemctl daemon-reload
systemctl enable sdr-inject.service 2>/dev/null || true

echo ""
echo "============================================"
echo "  Installation complete!"
echo "============================================"
echo ""
echo "OpenWebRX+:  http://$(hostname -I | awk '{print $1}'):8073"
echo "Bookmarks:   http://$(hostname -I | awk '{print $1}'):8073/static/seattle-bookmarks.html"
echo "Weather:     http://$(hostname -I | awk '{print $1}'):8073/static/weatherfax/index.html"
echo "Admin login: admin / dragon"
echo ""
echo "Run 'sudo $HOME_DIR/sdr-weekly-scan.sh' to do an initial frequency scan."
