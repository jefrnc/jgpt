# 🚀 Deployment Guide - GCP VM

Guía completa para desplegar el Trading Bot en Google Cloud Platform VM.

## 📋 Prerrequisitos

### 1. **GCP VM Setup**
```bash
# VM recomendada:
- Machine type: e2-small (2 vCPU, 2GB RAM)
- OS: Ubuntu 20.04 LTS o superior
- Disk: 20GB SSD
- Network: Allow HTTP/HTTPS traffic
```

### 2. **API Keys necesarias**
- ✅ Alpaca API (paper trading)
- ✅ Finnhub API (free tier)
- ✅ Telegram Bot Token
- ✅ Telegram Chat ID

## 🚀 Deployment Rápido (5 minutos)

### **Opción A: Setup completo automático**
```bash
# En tu VM GCP:
wget -O setup.sh https://raw.githubusercontent.com/jefrnc/jgpt/main/deploy/setup_vm.sh
chmod +x setup.sh
bash setup.sh
```

### **Opción B: Setup manual paso a paso**

#### **1. Clonar repositorio**
```bash
git clone https://github.com/jefrnc/jgpt.git
cd jgpt
```

#### **2. Setup del sistema**
```bash
bash deploy/setup_vm.sh
```

#### **3. Configurar environment**
```bash
nano .env
# Editar con tus API keys
```

#### **4. Setup del servicio**
```bash
bash deploy/setup_service.sh
```

#### **5. Deploy final**
```bash
bash deploy/deploy.sh
```

## ⚙️ Configuración de .env

```bash
# Alpaca API
ALPACA_API_KEY=tu_alpaca_key
ALPACA_SECRET_KEY=tu_alpaca_secret

# Telegram Bot  
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id

# Finnhub API
FINNHUB_API_KEY=tu_finnhub_key

# Trading Hours
ENABLE_PREMARKET=true
ENABLE_AFTERHOURS=false
WEEKEND_PAUSE=true
```

## 🎮 Comandos del Sistema

### **Control del bot**
```bash
# Iniciar bot
sudo systemctl start trading-bot

# Detener bot  
sudo systemctl stop trading-bot

# Reiniciar bot
sudo systemctl restart trading-bot

# Estado del bot
sudo systemctl status trading-bot
```

### **Monitoring**
```bash
# Ver logs en tiempo real
journalctl -u trading-bot -f

# Ver últimos 50 logs
journalctl -u trading-bot -n 50

# Logs de la última hora
journalctl -u trading-bot --since '1 hour ago'

# Recursos del sistema
htop

# Espacio en disco
df -h
```

## 🔧 Updates y Maintenance

### **Update del código**
```bash
cd /home/$USER/trading-bot
bash deploy/deploy.sh
```

### **Backup de configuración**
```bash
# Backup de .env
cp .env .env.backup

# Backup de logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

## 📊 Monitoring y Alertas

### **Verificar funcionamiento**
```bash
# Check que el bot esté corriendo
systemctl is-active trading-bot

# Ver últimos escáneos
journalctl -u trading-bot | grep "Gap scan\|Market\|Alert"

# Monitor de recursos
watch -n 5 'ps aux | grep python | head -5'
```

### **Health checks**
```bash
# Test de conectividad
PYTHONPATH=. python test_alpaca_connection.py

# Test del market hours manager  
PYTHONPATH=. python test_market_hours.py

# Test de alertas (simulado)
PYTHONPATH=. python test_enhanced_scanner.py
```

## 🚨 Troubleshooting

### **Bot no inicia**
```bash
# Ver error específico
journalctl -u trading-bot -n 20

# Verificar permisos
ls -la /home/$USER/trading-bot/

# Test manual
cd /home/$USER/trading-bot
source venv/bin/activate
PYTHONPATH=. python src/main.py --once --debug
```

### **No recibe alertas**
```bash
# Verificar configuración Telegram
grep TELEGRAM .env

# Test de Telegram
PYTHONPATH=. python test_simulate_alert.py
```

### **High memory usage**
```bash
# Ver procesos Python
ps aux | grep python

# Limitar memoria en service
sudo systemctl edit trading-bot
# Agregar: MemoryMax=512M
```

## 📈 Optimizaciones

### **Performance**
```bash
# Usar menor intervalo en premarket
echo "SCANNER_INTERVAL=180" >> .env

# Deshabilitar after hours para ahorrar API quota
echo "ENABLE_AFTERHOURS=false" >> .env
```

### **Security**
```bash
# Firewall básico
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Backup automático
echo "0 2 * * * cd /home/$USER/trading-bot && tar -czf /home/$USER/backup_\$(date +\%Y\%m\%d).tar.gz .env logs/" | crontab -
```

## 🎯 Next Steps

Una vez que tengas el bot corriendo:

1. **Monitor por 24h** para verificar estabilidad
2. **Ajustar parámetros** según necesidades
3. **Setup alertas de sistema** (CPU, disk, memory)  
4. **Considerar upgrade** a Docker para mejor isolation

## 📞 Support

Si tienes problemas:
1. Revisa logs: `journalctl -u trading-bot -f`
2. Verifica .env configuration
3. Test conexiones: APIs, Telegram, market data