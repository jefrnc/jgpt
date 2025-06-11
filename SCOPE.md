# Small-Cap Trading Edge System - Scope

## Objetivo
Sistema automatizado para detectar y alertar oportunidades de trading en small caps con foco en overnight breakouts y gaps premarket.

## Stack Tecnológico
- **Lenguaje**: Python 3.10+
- **APIs**: Alpaca, Finnhub, Benzinga, OpenAI/Anthropic, Telegram
- **Base de datos**: PostgreSQL para históricos
- **Infraestructura**: Docker + AWS/VPS para 24/7

## Componentes Core

### 1. Data Pipeline
- **Alpaca Market Data API v2**: Streaming realtime + premarket/afterhours
- **Finnhub API**: Float, shares outstanding, fundamentals
- **Benzinga Pro API**: Noticias realtime con tags (FDA, earnings, PR)

### 2. Análisis y Detección
- Scanner cada 5 min para gaps > 5%
- Filtros: Float < 50M, volumen > promedio, precio $0.50-$20
- Patrones: Gap & Go, Microfloat Squeeze, News Catalyst Breakout

### 3. Clasificación Inteligente
- GPT-4/Claude para análisis contextual de setups
- Scoring system: probabilidad de éxito basado en históricos
- Risk/Reward automático con stops y targets

### 4. Sistema de Alertas
- Telegram Bot con formato estructurado
- Webhooks para ejecución automática (opcional)
- Dashboard web para monitoreo

## Flujo de Trabajo

```
[Scanner] → [Filtros] → [AI Analysis] → [Alert] → [Track Performance]
```

## Métricas Target
- Latencia < 30 segundos desde detección
- Win rate > 60% en alertas enviadas
- Risk/Reward mínimo 1:2

## Fase 1 (MVP - 2 semanas)
- [ ] Setup APIs y autenticación
- [ ] Scanner básico de gaps
- [ ] Integración Telegram básica
- [ ] Testing con datos históricos

## Fase 2 (1 mes)
- [ ] AI classification system
- [ ] Performance tracking
- [ ] Backtesting framework
- [ ] Dashboard básico

## Fase 3 (Optimización)
- [ ] Machine learning para pattern recognition
- [ ] Auto-ajuste de parámetros
- [ ] Multi-exchange support
- [ ] Paper trading automation