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

export default function PINVerifyScreen({ navigation }) {
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);

  const handleVerifyPIN = async () => {
    if (pin.length !== 4) {
      Alert.alert('Errore', 'Inserisci il PIN a 4 cifre');
      return;
    }

    setLoading(true);
    try {
      const response = await AuthService.verifyPIN(pin);
      if (response.verified) {
        // PIN verified, navigate to main
        navigation.replace('Main');
      } else {
        Alert.alert('Errore', 'PIN non valido');
        setPin('');
      }
    } catch (error) {
      Alert.alert('Errore', error.message || 'PIN non valido');
      setPin('');
    } finally {
      setLoading(false);
    }
  };

  const handleUseFullLogin = async () => {
    // Clear user data and go to login
    await AsyncStorage.removeItem('user');
    await AsyncStorage.removeItem('token');
    navigation.replace('Login');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        <Text style={styles.title}>🔒 Inserisci PIN</Text>
        <Text style={styles.subtitle}>
          Inserisci il tuo PIN di sicurezza per continuare
        </Text>

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={pin}
            onChangeText={(text) => {
              const newPin = text.replace(/\D/g, '').slice(0, 4);
              setPin(newPin);
              // Auto-verify when 4 digits entered
              if (newPin.length === 4) {
                setTimeout(() => handleVerifyPIN(), 300);
              }
            }}
            keyboardType="numeric"
            secureTextEntry
            maxLength={4}
            placeholder="••••"
            placeholderTextColor="#999"
            autoFocus
          />
        </View>

        <TouchableOpacity
          style={styles.alternativeButton}
          onPress={handleUseFullLogin}
          disabled={loading}
        >
          <Text style={styles.alternativeText}>
            Usa login completo invece
          </Text>
        </TouchableOpacity>

        {loading && (
          <Text style={styles.loadingText}>Verifica in corso...</Text>
        )}
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
    marginBottom: 48,
  },
  inputContainer: {
    marginBottom: 32,
  },
  input: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    fontSize: 32,
    textAlign: 'center',
    letterSpacing: 16,
    borderWidth: 2,
    borderColor: theme.primary,
    color: theme.text,
  },
  alternativeButton: {
    padding: 16,
    alignItems: 'center',
  },
  alternativeText: {
    fontSize: 14,
    color: theme.primary,
    textDecorationLine: 'underline',
  },
  loadingText: {
    textAlign: 'center',
    color: theme.textSecondary,
    marginTop: 16,
    fontSize: 14,
  },
});
