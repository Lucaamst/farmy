# 🚀 GUIDA DEPLOY FARMYGO.CH

## STATO ATTUALE
- ✅ FarmyGo funzionante in locale: http://localhost:3000
- ❌ farmygo.ch non configurato (normale!)

## OPZIONI DI DEPLOY

### 🌟 OPZIONE A: Deploy Completo Professionale

#### 1. **Server VPS/Cloud** (Consigliato)
```bash
# Provider consigliati per farmygo.ch:
- DigitalOcean: €6/mese (2GB RAM, 50GB SSD)
- Hetzner: €4/mese (2GB RAM, 40GB SSD) 
- AWS Lightsail: $5/mese
- Linode: $5/mese
```

#### 2. **Configurazione Server**
```bash
# Ubuntu 22.04 LTS
sudo apt update && sudo apt upgrade -y

# Installa Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Installa MongoDB
sudo apt install -y mongodb

# Installa Nginx (reverse proxy)
sudo apt install nginx

# Installa Certbot (SSL gratis)
sudo apt install certbot python3-certbot-nginx
```

#### 3. **Deploy FarmyGo**
```bash
# Clona il progetto sul server
git clone [il-tuo-repo] /var/www/farmygo

# Backend
cd /var/www/farmygo/backend
npm install
pm2 start server.py --name farmygo-backend

# Frontend Build
cd /var/www/farmygo/frontend
npm install
npm run build

# Copia build in Nginx
sudo cp -r build/* /var/www/html/
```

#### 4. **Configurazione Nginx**
```nginx
server {
    server_name farmygo.ch www.farmygo.ch;
    
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 5. **DNS Configuration**
```
# Nel tuo provider DNS (Cloudflare/GoDaddy/etc):
A record: farmygo.ch → [IP-SERVER]
A record: www.farmygo.ch → [IP-SERVER]
```

#### 6. **SSL Certificate**
```bash
sudo certbot --nginx -d farmygo.ch -d www.farmygo.ch
```

---

### ⚡ OPZIONE B: Deploy Veloce (Per Test)

#### **Ngrok - Tunnel Pubblico**
```bash
# Installa ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Registrati su https://ngrok.com e ottieni il token

# Configura il tunnel
ngrok config add-authtoken [TUO-TOKEN]
ngrok http 3000

# Ti darà un URL pubblico tipo: https://abc123.ngrok.io
```

#### **Configurazione Dominio per Ngrok**
```
# DNS record:
CNAME: farmygo.ch → abc123.ngrok.io
```

---

### 🏗️ OPZIONE C: Platform-as-a-Service

#### **Vercel (Frontend)**
```bash
cd /app/frontend
npm install -g vercel
vercel --prod
# Configura dominio custom: farmygo.ch
```

#### **Railway/Render (Backend)**
```bash
# Railway.app o Render.com
# Deploy automatico da GitHub
# Costo: ~$5-10/mese
```

---

## 📋 CHECKLIST DEPLOY

### Pre-Deploy
- [ ] Backup database locale
- [ ] Test completo applicazione
- [ ] Configurazione variabili ambiente
- [ ] Build frontend per produzione

### Deploy
- [ ] Server configurato
- [ ] Database MongoDB attivo
- [ ] Backend avviato su porta 8001
- [ ] Frontend build servito da Nginx
- [ ] DNS configurato correttamente

### Post-Deploy
- [ ] SSL certificate attivo
- [ ] Test completo da farmygo.ch
- [ ] Monitoring attivo
- [ ] Backup automatici configurati

---

## 🆘 HELP IMMEDIATO

### Test Veloce Ngrok (5 minuti)
```bash
# Dal container attuale:
curl -sSL https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -o ngrok.zip
unzip ngrok.zip
./ngrok http 3000
```

### Test Localhost su Rete Locale
```bash
# Trova IP del container
ip addr show | grep inet

# Testa da dispositivo mobile sulla stessa rete:
http://[IP-CONTAINER]:3000
```

---

## 💰 COSTI STIMATI

### Deploy Professionale
- **VPS**: €4-6/mese
- **Dominio**: €10-15/anno (già hai farmygo.ch!)
- **SSL**: Gratis (Let's Encrypt)
- **Totale**: ~€5-7/mese

### Deploy Sviluppo
- **Ngrok Pro**: $8/mese (dominio custom)
- **Railway**: $5/mese (backend)
- **Vercel**: Gratis (frontend)
- **Totale**: ~$13/mese

---

## 🔧 SUPPORT

Scegli l'opzione che preferisci e ti guido passo-passo nel deploy!

**Consiglio**: Inizia con **Ngrok** per test veloce, poi passa al **VPS professionale** per produzione.