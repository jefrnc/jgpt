#!/bin/bash
# Setup systemd service para Trading Bot
# Ejecutar como: bash deploy/setup_service.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in correct directory
if [ ! -f "src/main.py" ]; then
    error "Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Get current directory and user
TRADING_DIR=$(pwd)
USER_NAME=$(whoami)

log "🔧 Configurando systemd service para Trading Bot"
log "Directorio: $TRADING_DIR"
log "Usuario: $USER_NAME"

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/trading-bot.service"

log "Creando service file: $SERVICE_FILE"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Trading Bot - Small Cap Gap Scanner
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$TRADING_DIR
Environment=PYTHONPATH=$TRADING_DIR
ExecStart=$TRADING_DIR/venv/bin/python src/main.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=trading-bot

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$TRADING_DIR/logs $TRADING_DIR/data
PrivateTmp=true

# Resource limits
LimitNOFILE=65536
MemoryMax=1G

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
log "Recargando systemd..."
sudo systemctl daemon-reload

# Enable service
log "Habilitando servicio..."
sudo systemctl enable trading-bot

log "✅ Servicio configurado correctamente!"
echo ""
echo "🎮 Comandos útiles:"
echo "   Iniciar:     sudo systemctl start trading-bot"
echo "   Detener:     sudo systemctl stop trading-bot"
echo "   Reiniciar:   sudo systemctl restart trading-bot"
echo "   Estado:      sudo systemctl status trading-bot"
echo "   Logs:        journalctl -u trading-bot -f"
echo "   Logs tail:   journalctl -u trading-bot -n 50"
echo ""
echo "📊 Para monitoring:"
echo "   htop                    # Ver recursos del sistema"
echo "   journalctl -u trading-bot --since '1 hour ago'"
echo ""

# Check if .env is configured
if grep -q "your_.*_here" .env 2>/dev/null; then
    warn "⚠️  CONFIGURA .env ANTES DE INICIAR:"
    warn "    nano .env"
    warn ""
    warn "    Necesitas configurar:"
    grep "your_.*_here" .env | sed 's/^/    /'
else
    log "📱 .env configurado - listo para iniciar!"
    echo ""
    echo "🚀 Para iniciar el bot:"
    echo "   sudo systemctl start trading-bot"
    echo "   journalctl -u trading-bot -f"
fi