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
{
  "expo": {
    "name": "FarmyGo Courier",
    "slug": "farmygo-courier",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ea580c"
    },
    "assetBundlePatterns": ["**/*"],
    "ios": {
      "supportsTablet": false,
      "bundleIdentifier": "ch.farmygo.courier"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ea580c"
      },
      "package": "ch.farmygo.courier"
    },
    "web": {
      "favicon": "./assets/favicon.png"
    },
    "plugins": [
      "expo-location",
      "expo-notifications",
      "expo-camera"
    ],
    "extra": {
      "apiUrl": "https://farmygo.ch/api",
      "eas": {
        "projectId": "2f53e315-043e-4bce-b8a3-0bffba91dad3"
      }
    }
  }
}
```

### STEP 4: Installa Dipendenze
```bash
npm install
```

### STEP 5: Avvia l'App
```bash
npx expo start
```

### STEP 6: Test su Dispositivo
1. Installa **Expo Go** sul tuo telefono
2. Scansiona il QR code che appare nel terminale
3. L'app si caricherà sul tuo dispositivo

## 🔧 CREARE I FILES MANCANTI

Devi creare la cartella `src/` con questi file:

### src/theme/theme.js
```javascript
import { MD3LightTheme } from 'react-native-paper';

export const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#ea580c',
    primaryContainer: '#fed7aa',
    secondary: '#dc2626',
    background: '#fff7ed',
  },
};
```

### src/services/AuthService.js
```javascript
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.apiUrl || 'https://farmygo.ch/api';

class AuthServiceClass {
  constructor() {
    this.apiClient = axios.create({
      baseURL: API_URL,
      timeout: 10000,
    });
  }

  async login(username, password) {
    try {
      const response = await this.apiClient.post('/auth/login', {
        username,
        password,
      });

      const { access_token, user } = response.data;

      if (user.role !== 'courier') {
        throw new Error('Accesso negato. Solo i corrieri possono utilizzare questa app.');
      }

      await SecureStore.setItemAsync('farmygo_token', access_token);
      return user;
    } catch (error) {
      throw new Error(
        error.response?.data?.detail || 
        'Login fallito. Controlla le credenziali.'
      );
    }
  }

  async validateToken(token) {
    try {
      const response = await this.apiClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data.user;
    } catch (error) {
      return null;
    }
  }
}

export const AuthService = new AuthServiceClass();
```

### src/screens/LoginScreen.js
```javascript
import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Text, TextInput, Button, Card, Title } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AuthService } from '../services/AuthService';
import { theme } from '../theme/theme';

export default function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Errore', 'Inserisci username e password');
      return;
    }

    setLoading(true);
    try {
      const user = await AuthService.login(username.trim(), password);
      onLogin(user);
    } catch (error) {
      Alert.alert('Errore di Login', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <Title style={styles.title}>FarmyGo Courier</Title>
      <Card style={styles.card}>
        <Card.Content>
          <TextInput
            label="Username"
            value={username}
            onChangeText={setUsername}
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            secureTextEntry
            style={styles.input}
          />
          <Button
            mode="contained"
            onPress={handleLogin}
            loading={loading}
            style={styles.button}
          >
            Accedi
          </Button>
        </Card.Content>
      </Card>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: theme.colors.background,
  },
  title: {
    textAlign: 'center',
    marginBottom: 30,
    fontSize: 28,
    color: theme.colors.primary,
  },
  card: {
    padding: 20,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 16,
  },
});
```

### src/screens/DeliveriesScreen.js (placeholder)
```javascript
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Button } from 'react-native-paper';

export default function DeliveriesScreen() {
  return (
    <View style={styles.container}>
      <Text variant="headlineMedium">Le Mie Consegne</Text>
      <Text>Coming soon...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
```

Crea anche MapScreen.js e ProfileScreen.js allo stesso modo.

## 🚀 RISULTATO ATTESO

Dopo questi passaggi:
1. ✅ Vedrai l'app nel tuo dashboard Expo
2. ✅ Potrai testarla sul tuo telefono
3. ✅ Sarai pronto per build e deploy

## ❓ PROBLEMI COMUNI

**"Command not found: expo"**
```bash
npm install -g @expo/cli
```

**"Project not found in dashboard"**
- Assicurati di aver fatto `eas login`
- Verifica che il projectId sia corretto

**App non si carica sul telefono**
- Controlla che telefono e computer siano sulla stessa rete WiFi
- Prova `npx expo start --tunnel`

---

💡 **Vuoi che ti guidi passo-passo in questa procedura?**