# 🚀 FARMYGO COURIER - QUICK START

## ⚡ SETUP RAPIDO (5 minuti)

### 1. Sul TUO computer:
```bash
npm install -g @expo/cli eas-cli
npx create-expo-app FarmyGoCourier
cd FarmyGoCourier
eas init --id 2f53e315-043e-4bce-b8a3-0bffba91dad3
```

### 2. Sostituisci i file generati con questi:

**App.js** → Copia il codice dalla guida completa
**package.json** → Aggiorna le dipendenze
**app.json** → Configura con projectId

### 3. Avvia:
```bash
npm install
npx expo start
```

### 4. Test:
- Installa Expo Go sul telefono
- Scansiona QR code
- Testa login corriere

## 🔍 VERIFICA FUNZIONAMENTO

✅ Login con credenziali corriere  
✅ Dashboard consegne visibile  
✅ App responsive  
✅ Navigazione funzionante  

## 📱 BUILD PRODUZIONE

```bash
eas build --platform all --profile production
```

---

**Nota**: Il codice completo è nella guida EXPO_SETUP_GUIDE.md