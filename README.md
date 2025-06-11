# Small-Cap Trading Edge System

Sistema automatizado para detectar oportunidades de trading en small caps con enfoque en overnight breakouts.

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

### APIs Adicionales (Próximamente)
- **Finnhub**: Para datos fundamentales y float
- **Benzinga**: Para noticias en tiempo real
- **OpenAI/Claude**: Para análisis inteligente
- **Telegram**: Para alertas instantáneas

## 🎯 Uso Básico

```python
# Iniciar scanner (próximamente)
python src/main.py

# Modo desarrollo
python src/main.py --debug

# Backtest
python src/backtest.py --date 2024-01-01
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
- [ ] Conexión Alpaca API
- [ ] Scanner básico de gaps
- [ ] Sistema de alertas Telegram
- [ ] Integración AI para análisis
- [ ] Dashboard web
- [ ] Backtesting framework

## ⚠️ Disclaimer

Este software es solo para fines educativos. El trading conlleva riesgos significativos. No nos hacemos responsables por pérdidas financieras.

## 📝 License

MIT License
