#!/bin/bash
# Deploy completo del Trading Bot en GCP VM
# Ejecutar como: bash deploy.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

header() {
    echo -e "${BLUE}$1${NC}"
}

# Banner
header "
╔══════════════════════════════════════════════════╗
║            Trading Bot Deployment                ║
║                                                  ║
║  🚀 Automated setup for GCP VM                  ║
║  📊 Gap Scanner + Float Screener                ║
║  📱 Telegram Alerts                             ║
║  ⏰ 24/7 Market Monitoring                      ║
╚══════════════════════════════════════════════════╝
"

# Check if in correct directory
if [ ! -f "src/main.py" ]; then
    error "Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

TRADING_DIR=$(pwd)
USER_NAME=$(whoami)

log "Iniciando deployment en: $TRADING_DIR"
log "Usuario: $USER_NAME"

# Step 1: Update repository
header "📥 Step 1: Actualizando código..."
git pull origin main || warn "No se pudo actualizar desde git"

# Step 2: Update dependencies
header "📦 Step 2: Actualizando dependencias..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 3: Run tests
header "🧪 Step 3: Ejecutando tests..."
PYTHONPATH=. python test_market_hours.py || warn "Test de market hours falló"

if [ -f ".env" ] && ! grep -q "your_.*_here" .env; then
    PYTHONPATH=. python test_alpaca_connection.py || warn "Test de Alpaca falló"
    log "✅ Tests básicos completados"
else
    warn "⚠️  .env no configurado - saltando tests de API"
fi

# Step 4: Update service if needed
header "🔧 Step 4: Actualizando servicio..."
if systemctl is-active --quiet trading-bot; then
    log "Deteniendo servicio para actualización..."
    sudo systemctl stop trading-bot
fi

# Reload service definition
sudo systemctl daemon-reload

# Step 5: Start service
header "🚀 Step 5: Iniciando servicio..."
sudo systemctl start trading-bot
sudo systemctl enable trading-bot

# Wait a moment and check status
sleep 3

if systemctl is-active --quiet trading-bot; then
    log "✅ Trading Bot iniciado correctamente!"
else
    error "❌ Error al iniciar el servicio"
    echo "Ver logs: journalctl -u trading-bot -n 20"
    exit 1
fi

# Step 6: Show status and logs
header "📊 Step 6: Estado del sistema..."
sudo systemctl status trading-bot --no-pager -l

echo ""
header "📝 Últimos logs del bot:"
journalctl -u trading-bot -n 10 --no-pager

echo ""
log "🎉 Deployment completado exitosamente!"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs en vivo:    journalctl -u trading-bot -f"
echo "   Estado del servicio: sudo systemctl status trading-bot"
echo "   Reiniciar bot:       sudo systemctl restart trading-bot"
echo "   Detener bot:         sudo systemctl stop trading-bot"
echo ""
echo "🔍 Monitoring:"
echo "   htop                 # Recursos del sistema"
echo "   df -h                # Espacio en disco"
echo "   free -h              # Memoria RAM"
echo ""

# Check if bot is receiving data
header "🔍 Verificando funcionamiento..."
sleep 5

if journalctl -u trading-bot --since '1 minute ago' | grep -q "Trading session active\|Market closed"; then
    log "✅ Bot detectando horarios de mercado correctamente"
else
    warn "⚠️  Verifica que el bot esté funcionando: journalctl -u trading-bot -f"
fi

echo ""
log "🚀 Trading Bot desplegado y funcionando en GCP VM!"
log "📱 Las alertas se enviarán automáticamente a Telegram cuando se detecten gaps"