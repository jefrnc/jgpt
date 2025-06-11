#!/bin/bash
# Script de monitoring para Trading Bot
# Uso: bash deploy/monitoring.sh

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

header() {
    echo -e "${BLUE}$1${NC}"
}

log() {
    echo -e "${GREEN}[OK]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
header "
╔══════════════════════════════════════════════════╗
║              Trading Bot Monitor                  ║
╚══════════════════════════════════════════════════╝
"

# Bot Status
header "🤖 Bot Status"
if systemctl is-active --quiet trading-bot; then
    log "Trading Bot está corriendo"
    UPTIME=$(systemctl show trading-bot --property=ActiveEnterTimestamp --value)
    echo "   Iniciado: $UPTIME"
else
    error "Trading Bot NO está corriendo"
    echo "   Para iniciar: sudo systemctl start trading-bot"
fi

# Resource Usage
header "💻 Resource Usage"
MEMORY=$(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')
DISK=$(df -h / | awk 'NR==2{print $5}')
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

echo "   Memory: $MEMORY used"
echo "   Disk: $DISK used"
echo "   CPU: ${CPU}% used"

# Check if resources are healthy
MEM_NUM=$(echo $MEMORY | cut -d'%' -f1)
DISK_NUM=$(echo $DISK | cut -d'%' -f1)

if (( $(echo "$MEM_NUM > 80" | bc -l) )); then
    warn "High memory usage: $MEMORY"
fi

if (( $(echo "$DISK_NUM > 85" | bc -l) )); then
    warn "High disk usage: $DISK"
fi

# Bot Process Info
header "🔍 Process Info"
if pgrep -f "python.*main.py" > /dev/null; then
    PID=$(pgrep -f "python.*main.py")
    MEM_MB=$(ps -p $PID -o rss= | awk '{print $1/1024}')
    CPU_PCT=$(ps -p $PID -o %cpu= | awk '{print $1}')
    
    log "Bot process found (PID: $PID)"
    echo "   Memory: ${MEM_MB} MB"
    echo "   CPU: ${CPU_PCT}%"
else
    error "Bot process not found"
fi

# Recent Activity
header "📊 Recent Activity (Last 10 logs)"
journalctl -u trading-bot -n 10 --no-pager --output=short | \
    sed 's/^/   /' | \
    grep -E "(Gap|Alert|Market|ERROR|INFO)" --color=always || echo "   No recent activity"

# Error Check
header "❗ Error Summary (Last 1 hour)"
ERROR_COUNT=$(journalctl -u trading-bot --since '1 hour ago' | grep -c ERROR || echo 0)
if [ "$ERROR_COUNT" -gt 0 ]; then
    error "Found $ERROR_COUNT errors in the last hour"
    journalctl -u trading-bot --since '1 hour ago' | grep ERROR | tail -3 | sed 's/^/   /'
else
    log "No errors in the last hour"
fi

# Market Hours Check
header "⏰ Market Status"
CURRENT_HOUR=$(date +%H)
DAY_OF_WEEK=$(date +%u)  # 1=Monday, 7=Sunday

if [ "$DAY_OF_WEEK" -gt 5 ]; then
    echo "   📅 Weekend - Market closed"
elif [ "$CURRENT_HOUR" -ge 4 ] && [ "$CURRENT_HOUR" -lt 9 ]; then
    echo "   🌅 Premarket hours (Active scanning)"
elif [ "$CURRENT_HOUR" -ge 9 ] && [ "$CURRENT_HOUR" -lt 16 ]; then
    echo "   📈 Market hours (Active scanning)"
elif [ "$CURRENT_HOUR" -ge 16 ] && [ "$CURRENT_HOUR" -lt 20 ]; then
    echo "   🌆 After hours (Limited scanning)"
else
    echo "   🌙 Market closed"
fi

# API Status Check
header "🔌 API Health"

# Check if we can reach APIs
if timeout 5 curl -s https://api.alpaca.markets > /dev/null; then
    log "Alpaca API reachable"
else
    warn "Alpaca API unreachable"
fi

if timeout 5 curl -s https://finnhub.io > /dev/null; then
    log "Finnhub API reachable"
else
    warn "Finnhub API unreachable"
fi

# Telegram check
if timeout 5 curl -s https://api.telegram.org > /dev/null; then
    log "Telegram API reachable"
else
    warn "Telegram API unreachable"
fi

# Recent Scans
header "🔍 Recent Scans"
SCAN_COUNT=$(journalctl -u trading-bot --since '1 hour ago' | grep -c "Starting gap scan" || echo 0)
echo "   Scans in last hour: $SCAN_COUNT"

if [ "$SCAN_COUNT" -eq 0 ]; then
    warn "No scans detected in the last hour"
elif [ "$SCAN_COUNT" -gt 20 ]; then
    warn "High scan frequency: $SCAN_COUNT scans/hour"
else
    log "Normal scan frequency"
fi

# Alerts Sent
ALERT_COUNT=$(journalctl -u trading-bot --since '24 hours ago' | grep -c "Alert sent successfully" || echo 0)
echo "   Alerts sent (24h): $ALERT_COUNT"

# Summary
header "📋 Summary"
if systemctl is-active --quiet trading-bot && [ "$ERROR_COUNT" -eq 0 ]; then
    log "System is healthy"
else
    warn "System needs attention"
fi

echo ""
echo "🔧 Quick Actions:"
echo "   View live logs:    journalctl -u trading-bot -f"
echo "   Restart bot:       sudo systemctl restart trading-bot"
echo "   Check resources:   htop"
echo "   Full status:       sudo systemctl status trading-bot"