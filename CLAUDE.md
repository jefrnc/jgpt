# Claude Session Memory - Trading Bot Project

## Project Overview
This is a trading bot for small-cap overnight breakouts with AI pattern recognition and statistical edge analysis.

## Key Components Implemented

### 1. Flash Research Integration
- **Purpose**: Verify statistics like gap frequency, closing patterns, continuation rates
- **Credentials**: jsfrnc@gmail.com / ge1hwZxFeN
- **Implementation**: Selenium-based web scraper for Next.js SPA
- **Features**:
  - Session persistence to avoid repeated logins
  - Multi-tab data extraction (Gap Day, Day 2, Financial metrics, SEC Filings, Notes)
  - Edge score calculation based on historical data
  - Clean alerts without mentioning Flash Research source

### 2. OpenAI Integration
- **Purpose**: AI pattern recognition and playbook generation
- **Model**: GPT-4
- **Features**:
  - Comprehensive gap analysis combining our scoring with Flash Research data
  - Pattern detection and risk assessment
  - English-only alerts with statistical context
  - Day trader focused prompts

### 3. Scoring System
- **Formula**: Gap Score + Volume Score + Float Score + Historical Score + AI Score = Total/100
- **Components**:
  - Gap strength (size and type)
  - Volume analysis (relative to average)
  - Float analysis (shares outstanding impact)
  - Historical edge from Flash Research
  - AI pattern recognition score

### 4. Alert System
- **Platform**: Telegram
- **Language**: English only (no Spanish)
- **Format**: Concise with key statistics
- **Content**: Score, historical edge, continuation rates, AI insights
- **Important**: No Flash Research mentions in alerts

## Technical Implementation

### Key Files
1. **`/src/api/flash_research_final_scraper.py`** (1457 lines)
   - Complete Selenium scraper for Flash Research
   - Handles login, navigation, multi-tab extraction
   - Session persistence implementation

2. **`/src/api/flash_research_client.py`** (632 lines)
   - Main client integrating scraper
   - Standardized data format conversion
   - Edge score calculations

3. **`/src/api/openai_client.py`** (427 lines)
   - GPT-4 integration
   - Comprehensive analysis methods
   - Alert message generation

4. **`/src/main.py`**
   - Integrated Flash Research and OpenAI
   - Comprehensive analysis pipeline
   - Alert generation without source mentions

### Dependencies Added
```
openai==1.6.1
selenium
schedule
```

## Deployment Status

### GCP VM Configuration
- **VM Name**: flask-vm
- **Project**: gap-detector-49a13
- **Zone**: us-central1-a
- **Status**: ✅ FULLY OPERATIONAL

### VM Components
- Google Chrome: 137.0.7151.103 ✅
- ChromeDriver: Installed ✅
- Python packages: All installed ✅
- Service: trading-bot.service (active) ✅

### Credentials on VM
- Flash Research: Configured ✅
- OpenAI API: Configured ✅
- Telegram Bot: Configured ✅
- All trading APIs: Configured ✅

## Important Notes

### User Preferences
1. **Language**: All alerts in English only
2. **No Risk/Reward Signals**: User explicitly doesn't want automatic R/R signals
3. **Clean Alerts**: Remove all Flash Research mentions to avoid problems
4. **Day Trading Focus**: Prompts and analysis tailored for day traders

### Technical Challenges Solved
1. **Flash Research Login**: It's a Next.js SPA requiring button clicks, not URL navigation
2. **Session Persistence**: Implemented to avoid repeated logins
3. **Multi-tab Extraction**: Successfully extracts from all tabs including hidden ones
4. **Chrome on VM**: Installed and configured for headless operation

### Sample Working Data
- **KLTO**: 53 gaps, 83% continuation rate
- **AAPL**: 57-58 gaps, 70-75% continuation rate
- Edge scores typically range 70-85/100 for good setups

## Next Session Checklist
- [ ] Bot is running 24/7 on VM waiting for market hours
- [ ] Flash Research integration working without issues
- [ ] Alerts being sent in English with statistics
- [ ] No Flash Research mentions in any user-facing content
- [ ] AI analysis providing pattern insights

## Commands for Future Reference

### SSH to VM
```bash
gcloud compute ssh flask-vm --zone=us-central1-a --project=gap-detector-49a13
```

### Check Bot Status
```bash
gcloud compute ssh flask-vm --zone=us-central1-a --project=gap-detector-49a13 --command="sudo systemctl status trading-bot"
```

### View Live Logs
```bash
gcloud compute ssh flask-vm --zone=us-central1-a --project=gap-detector-49a13 --command="journalctl -u trading-bot -f"
```

### Test Flash Research
```bash
gcloud compute ssh flask-vm --zone=us-central1-a --project=gap-detector-49a13 --command="cd trading-bot && source venv/bin/activate && python vm_quick_test.py"
```

## Session Context
This bot was built across multiple sessions. The main evolution was:
1. Started with basic gap detection
2. Added AI pattern recognition (OpenAI)
3. Integrated Flash Research for statistical edge
4. Converted everything to English
5. Deployed to GCP VM with full automation
6. Removed Flash Research mentions from alerts

The bot now runs autonomously, combining technical analysis, AI insights, and historical statistics to identify high-probability gap trades.