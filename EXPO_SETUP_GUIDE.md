# 📱 GUIDA SETUP EXPO FARMYGO COURIER

## 🚨 SITUAZIONE ATTUALE
- ✅ Ho preparato tutto il codice nel container
- ❌ L'app non è ancora nel TUO account Expo
- 🎯 Devi creare l'app sul TUO computer e copiarci il codice

## 🔧 PROCEDURA COMPLETA

### STEP 1: Installa Expo CLI (Sul tuo computer)
```bash
npm install -g @expo/cli
npm install -g eas-cli
```

### STEP 2: Login in Expo
```bash
npx expo login
# Inserisci le tue credenziali Expo
```

### STEP 3: Crea l'App Expo
```bash
npx create-expo-app FarmyGoCourier --template blank
cd FarmyGoCourier
eas init --id 2f53e315-043e-4bce-b8a3-0bffba91dad3
```

### STEP 4: Copia il Codice FarmyGo
**IMPORTANTE**: Scarica la cartella `courier-app` dal container e sostituisci tutto:

1. **Elimina** i file generati automaticamente da Expo
2. **Copia** tutti i file dalla cartella `/app/courier-app/` del container
3. **Mantieni** solo il file `.expo/` se esiste

**Struttura da copiare:**
```
FarmyGoCourier/
├── App.js              ← Copia da courier-app/App.js
├── package.json        ← Copia da courier-app/package.json  
├── app.json           ← Copia da courier-app/app.json
├── eas.json           ← Copia da courier-app/eas.json
├── src/               ← Copia tutta la cartella src/
│   ├── screens/
│   ├── services/
│   └── theme/  
├── assets/            ← Crea cartella e copia README.md
└── README.md          ← Copia da courier-app/README.md
```

### STEP 6: Installa Dipendenze
```bash
npm install
```

### STEP 7: Configura Assets
1. **Copia** il file `assets/README.md` 
2. **Sostituisci** gli asset placeholder con il branding FarmyGo
3. **Assets richiesti:**
   - `icon.png` (1024x1024)
   - `splash.png` (1284x2778) 
   - `adaptive-icon.png` (1024x1024)
   - `favicon.png` (32x32)

### STEP 8: Test Locale
```bash
# Avvia development server
npx expo start

# Su dispositivo iOS  
npx expo start --ios

# Su dispositivo Android
npx expo start --android
```

### STEP 9: Test su Dispositivo Reale
1. **Installa Expo Go** dal tuo app store
2. **Scansiona QR code** dal terminale
3. **Testa funzionalità:**
   - Login corriere
   - Lista consegne
   - Navigazione
   - Notifiche

## 📋 CODICE COMPLETO DA COPIARE

*(Il codice completo è nel container, copia direttamente i file)*

### App.js
```javascript
*(Copia da courier-app/App.js)*
```

**package.json**
```json
*(Copia da courier-app/package.json)*
```

**app.json**
```json
*(Copia da courier-app/app.json)*
```

## 🚀 FASE 2: BUILD E DEPLOY

### Build per Testing
```bash
# Build di sviluppo
eas build --profile development --platform all

# Build per testing interno
eas build --profile preview --platform all
```

### Build di Produzione
```bash
# Build finale per store
eas build --profile production --platform all
```

### Submit agli Store
```bash
# App Store + Google Play
eas submit --profile production --platform all
```

## 🔧 TROUBLESHOOTING

### Errori Comuni

**"Project not found"**
```bash
eas init --id 2f53e315-043e-4bce-b8a3-0bffba91dad3
```

**"Dependencies error"**  
```bash
rm -rf node_modules package-lock.json
npm install
```

**"Expo Go can't load"**
```bash
# Assicurati che telefono e computer siano sulla stessa rete
npx expo start --tunnel
```

**"Build failed"**
```bash
# Pulisci cache
eas build --clear-cache --platform all
```

### Performance Tips
1. **Usa Wi-Fi veloce** per sync
2. **Chiudi app non necessarie** durante build
3. **Aggiorna Expo Go** all'ultima versione
4. **Testa su dispositivi fisici** non solo simulatori

## 📱 TESTING CHECKLIST

### Funzionalità da Testare
- [ ] Login con credenziali corriere
- [ ] Caricamento lista consegne  
- [ ] Navigazione tra schermate
- [ ] Mappa con marker consegne
- [ ] Cambio stato consegne
- [ ] Notifiche push
- [ ] Logout e riaccesso
- [ ] Funzionalità offline base

### Test su Dispositivi
- [ ] iPhone (iOS 13+)
- [ ] Android (API 21+)
- [ ] Tablet (opzionale)
- [ ] Orientamento portrait/landscape

## 🌐 CONFIGURAZIONE PRODUZIONE

### Aggiorna API URL
In `app.json`, cambia da:
```json
"extra": {
  "apiUrl": "http://localhost:8001/api"
}
```

A:
```json  
"extra": {
  "apiUrl": "https://farmygo.ch/api"
}
```

### Assets di Produzione
- Sostituisci **tutti** i placeholder
- Logo FarmyGo ad alta risoluzione
- Splash screen professionale
- Icone ottimizzate per store

## 🎯 FASE 3: PUBBLICAZIONE

### App Store (iOS)
1. **Account Apple Developer** ($99/anno)
2. **Build con EAS**: `eas build --platform ios`
3. **Submit**: `eas submit --platform ios`
4. **Review Apple**: 1-7 giorni

### Google Play (Android)  
1. **Account Google Play Console** ($25 one-time)
2. **Build con EAS**: `eas build --platform android`
3. **Submit**: `eas submit --platform android`
4. **Review Google**: 1-3 giorni

## ✅ RISULTATO FINALE

Alla fine di questa procedura avrai:
1. ✅ App funzionante in Expo Go
2. ✅ Build per testing interno
3. ✅ App pubblicata negli store (se desiderato)
4. ✅ Sistema di notifiche attivo
5. ✅ Branding FarmyGo completo

## 📞 SUPPORTO

**Problemi con setup?**
- Verifica la connessione internet
- Assicurati che il backend sia online
- Controlla i permessi dispositivo

**Expo non funziona?**
```bash
# Reset completo
expo logout
expo login
eas build --clear-cache
```

**Vuoi supporto diretto?**
Condividi il messaggio di errore e posso aiutarti a risolvere!

---

💡 **Tip Importante**: Una volta completato il setup, l'app sarà completamente indipendente e funzionerà con il tuo backend FarmyGo in produzione!