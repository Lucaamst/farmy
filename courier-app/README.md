# FarmyGo Courier App

App mobile nativa per i corrieri FarmyGo costruita con React Native e Expo.

## 📱 Caratteristiche

### ✅ Implementate
- **Login sicuro** per corrieri
- **Dashboard consegne** con statistiche in tempo reale
- **Gestione stato consegne** (Assegnato → In Corso → Completato)
- **Notifiche push** per nuove consegne
- **Design nativo** ottimizzato per iOS e Android
- **Offline support** per funzionalità base
- **Sicurezza** con SecureStore per token

### 🚧 Da Completare
- **Mappa integrata** con navigazione GPS
- **Fotocamera** per prove di consegna
- **Geolocalizzazione** per tracking in tempo reale
- **Profilo corriere** con impostazioni

## 🛠 Setup e Deploy

### Prerequisiti
- Node.js 18+
- Expo CLI (`npm install -g @expo/cli`)
- Account Google Play Console ($25)
- Account Apple Developer ($99/anno)

### Installazione
```bash
cd /app/courier-app
npm install
```

### Sviluppo
```bash
# Avvia in modalità development
expo start

# Test su dispositivo Android
expo start --android

# Test su dispositivo iOS
expo start --ios
```

### Build per Produzione
```bash
# Build Android (APK/AAB)
eas build --platform android

# Build iOS (IPA)
eas build --platform ios

# Build entrambe le piattaforme
eas build --platform all
```

### Pubblicazione Store
```bash
# Pubblica su Google Play Store
eas submit --platform android

# Pubblica su Apple App Store
eas submit --platform ios
```

## 📋 API Integration

L'app si connette alle stesse API backend di FarmyGo:

- **Base URL**: `https://farmygo.ch/api`
- **Authentication**: JWT Bearer Token
- **Endpoints usati**:
  - `POST /auth/login` - Login corriere
  - `GET /auth/me` - Validazione token
  - `GET /courier/deliveries` - Lista consegne
  - `PATCH /courier/deliveries/start` - Avvia consegna
  - `PATCH /courier/deliveries/mark-delivered` - Completa consegna

## 🎨 Design System

### Colori Tema
- **Primary**: `#ea580c` (Arancione FarmyGo)
- **Secondary**: `#dc2626` (Rosso)
- **Success**: `#059669` (Verde)
- **Background**: `#fff7ed` (Crema)

### Componenti
- **React Native Paper** per UI components
- **React Navigation** per navigazione
- **Vector Icons** per icone
- **Toast Messages** per notifiche

## 📱 Funzionalità Future

### Fase 4 - Miglioramenti
1. **Mappa Interattiva**
   - Visualizzazione consegne su mappa
   - Navigazione turn-by-turn
   - Ottimizzazione percorsi

2. **Fotocamera e Media**
   - Foto prova consegna
   - Upload automatico al server
   - Galleria consegne completate

3. **Tracking GPS**
   - Posizione corriere in tempo reale
   - Cronologia percorsi
   - ETA dinamico per clienti

4. **Notifiche Avanzate**
   - Push personalizzate
   - Suoni custom per urgenze
   - Badge con contatori

## 🔧 Configurazione

### Environment Variables
```javascript
// app.json - extra config
{
  "extra": {
    "apiUrl": "https://farmygo.ch/api",
    "eas": {
      "projectId": "farmygo-courier-ch"
    }
  }
}
```

### Permissions
- **Location**: Per tracking e navigazione
- **Camera**: Per foto prove consegna
- **Notifications**: Per alert nuove consegne
- **Network**: Per sincronizzazione dati

## 📊 Store Listing

### App Store / Google Play
- **Nome**: "FarmyGo Courier"
- **Categoria**: Business / Productivity
- **Rating**: 4+ (Suitable for all ages)
- **Keywords**: delivery, courier, logistics, farmygo

### Screenshot Richiesti
- Login screen (5.5" e 6.5")
- Dashboard consegne
- Dettaglio consegna
- Mappa (quando implementata)

## 🚀 Deploy Checklist

### Pre-Deploy
- [ ] Test completo su dispositivi fisici
- [ ] Validazione API endpoints
- [ ] Test notifiche push
- [ ] Ottimizzazione icone e splash screen
- [ ] Test login/logout flow

### Store Submission
- [ ] Build produzione firmato
- [ ] Screenshot app store
- [ ] Descrizione app in italiano/inglese
- [ ] Privacy policy e termini
- [ ] Test review guidelines

### Post-Deploy
- [ ] Monitoring crash reports
- [ ] Analytics implementate
- [ ] Feedback utenti
- [ ] Updates incrementali

## 📞 Support

Per supporto tecnico durante deploy:
- Documentazione Expo: https://docs.expo.dev/
- React Native Paper: https://callstack.github.io/react-native-paper/
- Google Play Console: https://play.google.com/console
- Apple Developer: https://developer.apple.com/

---

**FarmyGo Courier App v1.0.0**  
Sviluppata per iOS e Android  
farmygo.ch