# Small-Cap Trading Edge System 🚀

Sistema automatizado para detectar oportunidades de trading en small caps con enfoque en overnight breakouts.

## 📊 Estado del Sistema

**✅ Bot Activo en GCP VM** - Funcionando 24/7 con auto-deployment desde GitHub Actions
**📢 Canal de Alertas** - Premarket Pulse - Small Caps configurado y activo
**🤖 AI Integration** - Pattern recognition y statistical edge analysis implementado

**🔥 Características principales:**
- Gap scanner automático (>5% gaps)
- Float screener para microfloat detection  
- **AI Pattern Recognition** con OpenAI GPT-4
- **Statistical Edge Analysis** con datos históricos
- Sistema de scoring inteligente (0-100 puntos)
- Alertas de Telegram en tiempo real (English only)
- Market hours detection inteligente
- Auto-deployment con cada push to main

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (opcional para históricos)
- Cuenta Alpaca (paper trading incluido)

### Installation

1. Clonar el repositorio
```bash
git clone https://github.com/jefrnc/jgpt.git
cd jgpt
```

2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus API keys
```

## 📁 Estructura del Proyecto

```
jgpt/
├── src/
│   ├── api/           # Conectores para APIs externas
│   ├── scanners/      # Lógica de escaneo de mercado
│   ├── alerts/        # Sistema de alertas (Telegram, etc)
│   ├── analysis/      # Análisis técnico y AI
│   └── utils/         # Utilidades y helpers
├── tests/             # Tests unitarios
├── config/            # Archivos de configuración
├── logs/              # Logs del sistema
└── data/              # Data temporal y cache
```

## 🔧 Configuración

### Alpaca API
- Obtener API keys en [Alpaca Markets](https://alpaca.markets/)
- Paper trading disponible para testing
- Configurar en `.env`:
  ```
  ALPACA_API_KEY=your_key
  ALPACA_SECRET_KEY=your_secret
  ```

### Telegram Bot
1. Crear un bot con [@BotFather](https://t.me/botfather) en Telegram
2. Obtener el token del bot
3. Configurar en `.env`:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   ```
4. Ejecutar el bot para obtener tu Chat ID:
   ```bash
   python run_telegram_bot.py
   ```
5. Enviar `/start` al bot en Telegram
6. Agregar el Chat ID a `.env`:
   ```
   TELEGRAM_CHAT_ID=tu_chat_id
   ```

### APIs Adicionales
- **Finnhub**: Datos fundamentales y float ✅
- **OpenAI**: Análisis de patrones con GPT-4 ✅
- **Statistical Data**: Edge histórico integrado ✅
- **Benzinga**: Para noticias en tiempo real (próximamente)

## 🎯 Uso Básico

```bash
# Monitoreo continuo inteligente (recomendado)
PYTHONPATH=. python src/main.py

# Una sola ejecución
PYTHONPATH=. python src/main.py --once

# Modo debug
PYTHONPATH=. python src/main.py --debug

# Cambiar intervalo de escaneo
PYTHONPATH=. python src/main.py --interval 180  # 3 minutos
```

## 💰 Optimización de API Quota

El sistema conserva inteligentemente el uso de API:

- **Premarket (4:00-9:30 AM)**: Escaneo cada 5 min 🔥
- **Market Hours (9:30-4:00 PM)**: Escaneo cada 10 min 📊  
- **After Hours (4:00-8:00 PM)**: Escaneo cada 15 min 📈
- **Closed/Weekend**: Pausa total, chequeo cada 1 hora ⏸️

**Configuración en `.env`:**
```bash
ENABLE_PREMARKET=true     # Escanear premarket
ENABLE_AFTERHOURS=false   # Ahorrar quota after hours
WEEKEND_PAUSE=true        # Pausa total en fines de semana
```

## 📊 Estrategias Implementadas

1. **Gap & Go**: Detecta gaps > 5% en premarket
2. **Microfloat Squeeze**: Acciones con float < 10M
3. **News Catalyst**: Reacciones a noticias (FDA, earnings, etc)

## 🛠️ Desarrollo

### Testing
```bash
pytest tests/
```

### Linting
```bash
black src/
flake8 src/
```

## 📈 Roadmap

- [x] Setup inicial y estructura
- [x] Conexión Alpaca API
- [x] Scanner básico de gaps
- [x] Sistema de alertas Telegram
- [x] **SISTEMA FUNCIONAL** 🎉
- [x] Integración AI para análisis (OpenAI GPT-4) ✅
- [x] Scanner de float/fundamentales (Finnhub) ✅
- [x] Statistical edge analysis ✅
- [x] Sistema de scoring inteligente (0-100) ✅
- [ ] Dashboard web
- [ ] Backtesting framework
- [ ] Risk management automático

## ⚠️ Disclaimer

Este software es solo para fines educativos. El trading conlleva riesgos significativos. No nos hacemos responsables por pérdidas financieras.

## 📝 License

MIT License
