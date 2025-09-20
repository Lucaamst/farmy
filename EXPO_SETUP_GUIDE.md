# 📱 GUIDA SETUP EXPO FARMYGO COURIER

## 🚨 SITUAZIONE ATTUALE
- ✅ Ho preparato tutto il codice nel container
- ❌ L'app non è ancora nel TUO account Expo
- 🎯 Devi creare l'app sul TUO computer

## 🔧 PROCEDURA CORRETTA

### STEP 1: Installa Expo CLI (Sul tuo computer)
```bash
npm install -g @expo/cli
npm install -g eas-cli
```

### STEP 2: Crea l'App Expo
```bash
npx create-expo-app FarmyGoCourier
cd FarmyGoCourier
eas init --id 2f53e315-043e-4bce-b8a3-0bffba91dad3
```

### STEP 3: Copia il Codice FarmyGo
Sostituisci i file generati con quelli che ho preparato:

**App.js**
```javascript
import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import * as SecureStore from 'expo-secure-store';
import * as Notifications from 'expo-notifications';
import Toast from 'react-native-toast-message';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import DeliveriesScreen from './src/screens/DeliveriesScreen';
import MapScreen from './src/screens/MapScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import DeliveryDetailScreen from './src/screens/DeliveryDetailScreen';

// Services
import { AuthService } from './src/services/AuthService';
import { NotificationService } from './src/services/NotificationService';

// Theme
import { theme } from './src/theme/theme';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Consegne') {
            iconName = 'local-shipping';
          } else if (route.name === 'Mappa') {
            iconName = 'map';
          } else if (route.name === 'Profilo') {
            iconName = 'person';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen name="Consegne" component={DeliveriesScreen} />
      <Tab.Screen name="Mappa" component={MapScreen} />
      <Tab.Screen name="Profilo" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuthStatus();
    initializeNotifications();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await SecureStore.getItemAsync('farmygo_token');
      if (token) {
        const userData = await AuthService.validateToken(token);
        if (userData && userData.role === 'courier') {
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          await SecureStore.deleteItemAsync('farmygo_token');
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      await SecureStore.deleteItemAsync('farmygo_token');
    } finally {
      setIsLoading(false);
    }
  };

  const initializeNotifications = async () => {
    try {
      await NotificationService.initialize();
      
      // Handle notification received while app is running
      Notifications.addNotificationReceivedListener(notification => {
        console.log('Notification received:', notification);
        Toast.show({
          type: 'info',
          text1: 'Nuova Consegna',
          text2: notification.request.content.body,
          visibilityTime: 4000,
        });
      });

      // Handle notification response (when user taps notification)
      Notifications.addNotificationResponseReceivedListener(response => {
        console.log('Notification response:', response);
      });
    } catch (error) {
      console.error('Notification initialization failed:', error);
    }
  };

  const handleLogin = async (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    try {
      await SecureStore.deleteItemAsync('farmygo_token');
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (isLoading) {
    return null; // Or loading screen
  }

  return (
    <PaperProvider theme={theme}>
      <NavigationContainer>
        <StatusBar style="light" backgroundColor={theme.colors.primary} />
        {isAuthenticated ? (
          <Stack.Navigator>
            <Stack.Screen 
              name="Main" 
              options={{ headerShown: false }}
            >
              {(props) => <TabNavigator {...props} user={user} onLogout={handleLogout} />}
            </Stack.Screen>
            <Stack.Screen 
              name="DeliveryDetail" 
              component={DeliveryDetailScreen} 
              options={{
                title: 'Dettaglio Consegna',
                headerStyle: { backgroundColor: theme.colors.primary },
                headerTintColor: '#fff',
              }}
            />
          </Stack.Navigator>
        ) : (
          <Stack.Navigator>
            <Stack.Screen 
              name="Login" 
              options={{ headerShown: false }}
            >
              {(props) => <LoginScreen {...props} onLogin={handleLogin} />}
            </Stack.Screen>
          </Stack.Navigator>
        )}
      </NavigationContainer>
      <Toast />
    </PaperProvider>
  );
}
```

**package.json**
```json
{
  "name": "farmygo-courier",
  "version": "1.0.0",
  "main": "expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/native-stack": "^6.9.17",
    "@react-navigation/bottom-tabs": "^6.5.11",
    "expo": "~49.0.21",
    "expo-location": "~16.5.5",
    "expo-notifications": "~0.23.2",
    "expo-camera": "~13.6.0",
    "expo-status-bar": "~1.6.0",
    "expo-constants": "~14.4.2",
    "expo-secure-store": "~12.5.0",
    "expo-splash-screen": "~0.20.5",
    "react": "18.2.0",
    "react-native": "0.72.6",
    "react-native-paper": "^5.11.1",
    "react-native-vector-icons": "^10.0.2",
    "react-native-maps": "1.8.0",
    "react-native-safe-area-context": "4.7.4",
    "react-native-screens": "~3.27.0",
    "axios": "^1.6.0",
    "react-native-toast-message": "^2.1.7"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0"
  }
}
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