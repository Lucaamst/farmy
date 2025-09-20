# 📱 FarmyGo Courier Mobile App

L'app mobile dedicata ai corrieri FarmyGo per gestire le consegne in modo efficiente e professionale.

## ✨ Caratteristiche

### 🔐 Autenticazione Sicura
- Login con credenziali corriere
- Token JWT per sessioni sicure
- Archiviazione sicura con Expo SecureStore

### 📦 Gestione Consegne
- Lista consegne assegnate in tempo reale
- Stati: Assegnato → In Corso → Consegnato
- Dettagli completi per ogni consegna
- Aggiornamenti in tempo reale

### 🗺️ Navigazione Integrata
- Mappa interattiva con posizioni consegne
- Navigazione diretta a Google Maps
- Tracking GPS del corriere
- Visualizzazione ottimizzata per mobile

### 👤 Profilo Corriere
- Informazioni personali
- Statistiche consegne
- Impostazioni app
- Centro assistenza

### 🔔 Notifiche Push
- Notifiche per nuove consegne
- Aggiornamenti stato ordini
- Comunicazioni urgenti

## 🛠️ Stack Tecnologico

- **Framework**: React Native con Expo
- **UI Components**: React Native Paper
- **Navigazione**: React Navigation v6
- **Mappe**: React Native Maps (Google Maps)
- **Notifiche**: Expo Notifications
- **Storage**: Expo SecureStore
- **HTTP Client**: Axios
- **Icone**: React Native Vector Icons

## 📱 Compatibilità

- **iOS**: 13.0+
- **Android**: API Level 21+ (Android 5.0+)
- **Supporto**: Smartphone e tablet

## 🚀 Setup Locale

### Prerequisiti
```bash
node >= 16.0.0
npm >= 8.0.0
expo-cli >= 6.0.0
```

### Installazione Rapida
```bash
# Clone e installa dipendenze
git clone [repository]
cd courier-app
npm install

# Installa Expo CLI e EAS CLI
npm install -g @expo/cli eas-cli

# Avvia sviluppo
npx expo start
```

### Setup Automatico
```bash
# Esegui script di setup
chmod +x setup.sh
./setup.sh
```

## 📋 Configurazione

### 1. API Endpoint
Aggiorna l'URL del backend in `app.json`:
```json
{
  "expo": {
    "extra": {
      "apiUrl": "https://farmygo.ch/api"
    }
  }
}
```

### 2. Assets Branding
Sostituisci i placeholder con gli asset FarmyGo:
- `assets/icon.png` - Icona app (1024x1024)
- `assets/splash.png` - Splash screen (1284x2778)
- `assets/adaptive-icon.png` - Icona adattiva Android (1024x1024)

### 3. Notifiche Push
Configurazione automatica con Expo Push Service tramite il Project ID.

## 🔨 Build e Deploy

### Build di Sviluppo
```bash
# Build per testing interno
eas build --profile development --platform all
```

### Build di Produzione
```bash
# Build per stores
eas build --profile production --platform all
```

### Pubblicazione Store
```bash
# Submit to App Store e Google Play
eas submit --profile production --platform all
```

## 📱 Testing

### Device Testing
1. Installa **Expo Go** dal tuo app store
2. Avvia `npx expo start`
3. Scansiona il QR code con Expo Go (Android) o Camera (iOS)

### Simulatori
```bash
# iOS Simulator
npx expo start --ios

# Android Emulator  
npx expo start --android
```

## 🔧 Sviluppo

### Struttura Progetto
```
courier-app/
├── App.js                 # App principale
├── app.json              # Configurazione Expo
├── package.json          # Dipendenze
├── eas.json             # Configurazione build
├── src/
│   ├── screens/         # Schermate app
│   │   ├── LoginScreen.js
│   │   ├── DeliveriesScreen.js
│   │   ├── MapScreen.js
│   │   └── ProfileScreen.js
│   ├── services/        # Servizi API
│   │   ├── AuthService.js
│   │   └── NotificationService.js
│   └── theme/          # Tema e stili
│       └── theme.js
└── assets/             # Assets e risorse
    └── [icons, splash, etc.]
```

### Hot Reload
L'app supporta hot reload automatico durante lo sviluppo. Salva un file e vedi i cambiamenti istantaneamente.

### Debug
```bash
# Debug con Flipper
npx expo start --dev-client

# Logs in tempo reale
npx expo logs
```

## 🌐 API Integration

### Endpoints Principali
- `POST /auth/login` - Autenticazione corriere
- `GET /courier/deliveries` - Lista consegne
- `PATCH /courier/deliveries/start` - Avvia consegna
- `PATCH /courier/deliveries/mark-delivered` - Completa consegna

### Error Handling
L'app gestisce automaticamente:
- Errori di rete
- Token scaduti
- Errori API
- Stati offline

## 🔐 Sicurezza

- Archiviazione sicura token con encrypting
- Validazione input lato client
- Timeout richieste API
- Gestione permessi device

## 📞 Supporto

Per assistenza tecnica:
- **Email**: support@farmygo.ch
- **Documentazione**: Vedi EXPO_SETUP_GUIDE.md
- **Issues**: Contatta il team di sviluppo

## 📝 Note di Rilascio

### v1.0.0 (Attuale)
- ✅ Autenticazione corrieri
- ✅ Gestione consegne completa  
- ✅ Navigazione con mappe
- ✅ Notifiche push
- ✅ Interfaccia in italiano
- ✅ Design responsive

### Prossime Funzionalità
- 📸 Foto di conferma consegna
- 📊 Statistiche avanzate
- 🌙 Modalità scura
- 🔄 Sync offline
- 📱 Widget iOS/Android

---

**Sviluppato per FarmyGo** 🚚  
*Sistema di Gestione Consegne Professionale*