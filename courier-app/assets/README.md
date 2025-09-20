# 📁 FarmyGo Courier App - Assets

Questa cartella contiene tutti gli asset necessari per l'app FarmyGo Courier.

## 🎨 Asset Richiesti

### Icone Principali
- **icon.png** (1024x1024 px)
  - Icona principale dell'app
  - Formato: PNG con trasparenza
  - Uso: App Store, Google Play, launcher

- **adaptive-icon.png** (1024x1024 px)  
  - Icona adattiva per Android
  - Formato: PNG con trasparenza
  - Deve funzionare in cerchi, quadrati, squircle

### Splash Screen
- **splash.png** (1284x2778 px)
  - Schermata di caricamento
  - Formato: PNG
  - Proporzioni: iPhone 12 Pro Max
  - Background color: #ea580c (FarmyGo Orange)

### Notifiche
- **notification-icon.png** (96x96 px)
  - Icona per notifiche push
  - Formato: PNG con trasparenza
  - Colore: Bianco/Trasparente su background colorato

### Favicon Web
- **favicon.png** (32x32 px)
  - Icona per versione web
  - Formato: PNG
  - Semplice e riconoscibile

### Audio
- **notification.wav**
  - Suono per notifiche personalizzate
  - Formato: WAV, MP3, M4A
  - Durata: 1-3 secondi

## 🎨 Linee Guida Design

### Colori FarmyGo
- **Primario**: #ea580c (Arancione)
- **Secondario**: #dc2626 (Rosso)
- **Accent**: #059669 (Verde)
- **Background**: #fff7ed (Crema)

### Stile Icone
- Design moderno e pulito
- Bordi arrotondati
- Buon contrasto
- Leggibili a tutte le dimensioni

### Brand Identity
- Logo FarmyGo prominente
- Elementi delivery/trasporto
- Colori aziendali consistenti
- Font leggibile e professionale

## 📱 Specifiche Tecniche

### Formati Supportati
- **Immagini**: PNG (preferito), JPG
- **Audio**: WAV, MP3, M4A
- **Vettoriali**: SVG (convertiti in PNG per Expo)

### Risoluzione
- Tutte le immagini ad alta risoluzione
- Supporto display Retina/high-DPI
- Ottimizzazione dimensioni file

### Compatibilità
- iOS 13.0+
- Android API 21+
- Supporto dark/light mode

## 🔧 Come Aggiornare

1. **Sostituisci i file** in questa cartella
2. **Mantieni i nomi** esatti dei file
3. **Rispetta le dimensioni** specificate
4. **Testa su dispositivi** diversi
5. **Rebuilda l'app** per vedere i cambiamenti

```bash
# Dopo aver aggiornato gli asset
eas build --clear-cache --platform all
```

## ✅ Checklist Assets

- [ ] icon.png (1024x1024)
- [ ] adaptive-icon.png (1024x1024)  
- [ ] splash.png (1284x2778)
- [ ] notification-icon.png (96x96)
- [ ] favicon.png (32x32)
- [ ] notification.wav (opzionale)

## 🎯 Asset di Produzione

Per la pubblicazione negli store è essenziale avere:
- Icone in alta qualità
- Splash screen professionale
- Branding coerente
- Ottimizzazione dimensioni

## 📞 Supporto

Per assistenza con gli asset:
- **Email**: design@farmygo.ch
- **Formato richieste**: Specifica device e use case
- **Timeline**: Aggiornamenti entro 1-2 giorni lavorativi

---

**Nota**: Attualmente questa cartella contiene solo placeholder. Sostituisci con gli asset FarmyGo ufficiali prima del rilascio in produzione.