# 🚀 GitHub Actions Auto-Deployment Setup

Configuración necesaria para que GitHub se encargue automáticamente del deployment en tu GCP VM.

## 📋 Configuración de Secrets en GitHub

### 1. **Ir a tu repositorio en GitHub**
```
https://github.com/jefrnc/jgpt/settings/secrets/actions
```

### 2. **Agregar estos Repository Secrets:**

#### **GCP_SA_KEY** (Service Account Key)
```bash
# 1. En GCP Console, ve a IAM & Admin > Service Accounts
# 2. Crear nueva service account: "github-actions-bot"
# 3. Roles necesarios:
#    - Compute Instance Admin (v1)
#    - Service Account User
# 4. Generar key JSON y copiar TODO el contenido al secret
```

#### **VM_SSH_PRIVATE_KEY** (SSH Private Key)
```bash
# En tu VM GCP, generar nuevo par de keys:
ssh-keygen -t ed25519 -f ~/.ssh/github_actions -N ""

# Copiar la PRIVATE key al secret:
cat ~/.ssh/github_actions

# Agregar la PUBLIC key a authorized_keys:
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
```

## 🔧 Setup Completo Paso a Paso

### **Paso 1: Service Account en GCP**
```bash
# 1. Ve a GCP Console > IAM & Admin > Service Accounts
# 2. Click "CREATE SERVICE ACCOUNT"
# 3. Nombre: github-actions-bot
# 4. Description: Bot for automated deployments from GitHub
# 5. Click "CREATE AND CONTINUE"

# 6. Agregar roles:
#    - Compute Instance Admin (v1)
#    - Service Account User
# 7. Click "CONTINUE" y "DONE"

# 8. Click en la service account creada
# 9. Tab "KEYS" > "ADD KEY" > "Create new key"
# 10. Tipo: JSON > "CREATE"
# 11. Guardar el archivo JSON
```

### **Paso 2: SSH Keys en VM**
```bash
# Conectar a tu VM GCP:
gcloud compute ssh flask-vm --zone=us-central1-a

# Generar SSH keys:
ssh-keygen -t ed25519 -f ~/.ssh/github_actions -N ""

# Ver la private key (copiar TODO esto):
cat ~/.ssh/github_actions

# Configurar authorized_keys:
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### **Paso 3: Configurar Secrets en GitHub**
```bash
# 1. Ve a: https://github.com/jefrnc/jgpt/settings/secrets/actions
# 2. Click "New repository secret"

# Secret 1: GCP_SA_KEY
# - Name: GCP_SA_KEY  
# - Value: [Pegar TODO el contenido del archivo JSON del service account]

# Secret 2: VM_SSH_PRIVATE_KEY
# - Name: VM_SSH_PRIVATE_KEY
# - Value: [Pegar TODO el contenido de ~/.ssh/github_actions de la VM]
```

### **Paso 4: Configurar .env en VM**
```bash
# En tu VM, crear/editar .env:
nano /home/$USER/trading-bot/.env

# Agregar tus API keys:
ALPACA_API_KEY=tu_alpaca_key
ALPACA_SECRET_KEY=tu_alpaca_secret
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id
FINNHUB_API_KEY=tu_finnhub_key
ENABLE_PREMARKET=true
ENABLE_AFTERHOURS=false
WEEKEND_PAUSE=true
```

## ✅ Verificar Setup

### **Test 1: Service Account**
```bash
# Download del JSON key y test:
gcloud auth activate-service-account --key-file=service-account-key.json
gcloud compute instances list --project=gap-detector-49a13
```

### **Test 2: SSH Access**
```bash
# Desde tu máquina local, test SSH:
ssh -i github_actions user@EXTERNAL_IP_DE_TU_VM
```

### **Test 3: Manual Workflow**
```bash
# 1. Ve a: https://github.com/jefrnc/jgpt/actions
# 2. Click "Deploy Trading Bot to GCP"
# 3. Click "Run workflow" > "Run workflow"
# 4. Observar logs del deployment
```

## 🎯 Después del Setup

Una vez configurado, **cada push a main** ejecutará automáticamente:

1. ✅ **VM Health Check** - Verifica estado del VM
2. 🛠️ **Initial Setup** - Instala dependencias si es necesario  
3. 📦 **Code Deployment** - Clona/actualiza repositorio
4. 🐍 **Python Setup** - Configura virtual environment
5. 🔧 **Service Setup** - Configura systemd service
6. 🚀 **Bot Start** - Inicia/reinicia trading bot
7. 🏥 **Health Check** - Verifica funcionamiento
8. 📱 **Notifications** - Reporta estado del deployment

## 🔍 Monitoring del Auto-Deployment

### **Ver deployment en GitHub**
```bash
# Ve a: https://github.com/jefrnc/jgpt/actions
# Cada push mostrará el progreso del deployment
```

### **Verificar en VM**
```bash
# SSH a tu VM:
gcloud compute ssh flask-vm --zone=us-central1-a

# Ver estado del bot:
sudo systemctl status trading-bot

# Ver logs recientes:
journalctl -u trading-bot -n 20

# Monitor en tiempo real:
journalctl -u trading-bot -f
```

## 🚨 Troubleshooting

### **Error: Service Account Permissions**
```bash
# Verificar roles en GCP Console:
# IAM & Admin > IAM > Buscar github-actions-bot
# Debe tener: Compute Instance Admin (v1) + Service Account User
```

### **Error: SSH Permission Denied**
```bash
# En VM, verificar:
ls -la ~/.ssh/
cat ~/.ssh/authorized_keys

# La public key debe estar en authorized_keys
# Permisos: ~/.ssh (700), authorized_keys (600)
```

### **Error: Bot not starting**
```bash
# En VM, debug manual:
cd /home/$USER/trading-bot
source venv/bin/activate
PYTHONPATH=. python src/main.py --once --debug
```

## 🎉 ¡Listo!

Después de este setup, solo necesitas:

1. **Hacer cambios** en tu código local
2. **git push** to main
3. **GitHub se encarga** del resto automáticamente
4. **Recibir alertas** de Telegram cuando haya gaps

**¡Tu sistema está completamente automatizado!** 🚀