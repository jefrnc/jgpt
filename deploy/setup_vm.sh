#!/bin/bash
# Setup script para GCP VM - Trading Bot Deployment
# Ejecutar como: bash setup_vm.sh

set -e  # Exit on any error

echo "🚀 Trading Bot GCP VM Setup"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "No ejecutes este script como root. Usa tu usuario normal."
   exit 1
fi

# Update system
log "Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+ and dependencies
log "Instalando Python y dependencias..."
sudo apt install -y python3 python3-pip python3-venv git curl wget htop

# Install additional packages for trading
sudo apt install -y build-essential python3-dev pkg-config

# Check Python version
PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
log "Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -ne 1 ]]; then
    error "Se requiere Python 3.8 o superior"
    exit 1
fi

# Create trading user directory
TRADING_DIR="/home/$USER/trading-bot"
log "Creando directorio: $TRADING_DIR"

# Clone repository
if [ -d "$TRADING_DIR" ]; then
    warn "Directorio ya existe. Actualizando..."
    cd "$TRADING_DIR"
    git pull origin main
else
    log "Clonando repositorio..."
    git clone https://github.com/jefrnc/jgpt.git "$TRADING_DIR"
    cd "$TRADING_DIR"
fi

# Create virtual environment
log "Creando entorno virtual..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
log "Instalando dependencias Python..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs
mkdir -p data

# Setup environment file
if [ ! -f ".env" ]; then
    log "Creando archivo .env..."
    cp .env.example .env
    warn "⚠️  IMPORTANTE: Edita el archivo .env con tus API keys:"
    warn "    nano $TRADING_DIR/.env"
    warn ""
    warn "    Configura:"
    warn "    - ALPACA_API_KEY"
    warn "    - ALPACA_SECRET_KEY"
    warn "    - TELEGRAM_BOT_TOKEN"
    warn "    - TELEGRAM_CHAT_ID"
    warn "    - FINNHUB_API_KEY"
else
    log "Archivo .env ya existe"
fi

# Set permissions
chmod +x src/main.py
chmod +x test_*.py

# Test installation
log "Probando instalación..."
PYTHONPATH=. python test_alpaca_connection.py || warn "Test de Alpaca falló - verifica .env"

log "✅ Setup básico completado!"
echo ""
echo "🔧 Próximos pasos:"
echo "1. Editar archivo .env: nano $TRADING_DIR/.env"
echo "2. Ejecutar setup del service: bash deploy/setup_service.sh"
echo "3. Iniciar bot: sudo systemctl start trading-bot"
echo ""
echo "📁 Directorio del bot: $TRADING_DIR"
echo "📝 Logs del sistema: journalctl -u trading-bot -f"