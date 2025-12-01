import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import AuthService from '../services/AuthService';
import { theme } from '../theme/colors';

export default function PINSetupScreen({ navigation, route }) {
  const [pin, setPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [loading, setLoading] = useState(false);
  const { userId } = route.params;

  const handleSetupPIN = async () => {
    if (pin.length !== 4 || !/^\d{4}$/.test(pin)) {
      Alert.alert('Errore', 'Il PIN deve essere di 4 cifre numeriche');
      return;
    }

    if (pin !== confirmPin) {
      Alert.alert('Errore', 'I PIN non corrispondono');
      return;
    }

    setLoading(true);
    try {
      await AuthService.setPIN(pin);
      await AsyncStorage.setItem(`courier_pin_enabled_${userId}`, 'true');
      
      Alert.alert(
        'Successo!',
        'PIN impostato correttamente',
        [
          {
            text: 'OK',
            onPress: () => navigation.replace('Main'),
          },
        ]
      );
    } catch (error) {
      Alert.alert('Errore', error.message || 'Impossibile impostare il PIN');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = async () => {
    await AsyncStorage.setItem(`courier_pin_enabled_${userId}`, 'skipped');
    navigation.replace('Main');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        <Text style={styles.title}>🔢 Imposta PIN Sicurezza</Text>
        <Text style={styles.subtitle}>
          Crea un PIN a 4 cifre per accessi rapidi futuri
        </Text>

        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            📱 <Text style={styles.infoBold}>Perché un PIN?</Text>
            {"\n"}
            La prossima volta che apri l'app, ti basterà inserire il PIN invece
            di fare login completo.
          </Text>
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Inserisci PIN (4 cifre)</Text>
          <TextInput
            style={styles.input}
            value={pin}
            onChangeText={(text) => setPin(text.replace(/\D/g, '').slice(0, 4))}
            keyboardType="numeric"
            secureTextEntry
            maxLength={4}
            placeholder="••••"
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Conferma PIN</Text>
          <TextInput
            style={styles.input}
            value={confirmPin}
            onChangeText={(text) =>
              setConfirmPin(text.replace(/\D/g, '').slice(0, 4))
            }
            keyboardType="numeric"
            secureTextEntry
            maxLength={4}
            placeholder="••••"
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.skipButton]}
            onPress={handleSkip}
            disabled={loading}
          >
            <Text style={styles.skipButtonText}>
              Salta (usa sempre login)
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.setupButton]}
            onPress={handleSetupPIN}
            disabled={loading}
          >
            <Text style={styles.setupButtonText}>
              {loading ? 'Impostazione...' : 'Imposta PIN'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.text,
    textAlign: 'center',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: theme.textSecondary,
    textAlign: 'center',
    marginBottom: 24,
  },
  infoBox: {
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    padding: 16,
    marginBottom: 32,
    borderWidth: 1,
    borderColor: '#90CAF9',
  },
  infoText: {
    fontSize: 14,
    color: '#1565C0',
    lineHeight: 20,
  },
  infoBold: {
    fontWeight: 'bold',
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 8,
  },
  input: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    fontSize: 24,
    textAlign: 'center',
    letterSpacing: 12,
    borderWidth: 1,
    borderColor: theme.border,
    color: theme.text,
  },
  buttonContainer: {
    marginTop: 32,
    gap: 12,
  },
  button: {
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  skipButton: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: theme.border,
  },
  skipButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.textSecondary,
  },
  setupButton: {
    backgroundColor: theme.primary,
  },
  setupButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
  },
});
