import React, { useRef, useState } from 'react';
import { View, StyleSheet, Alert, ScrollView } from 'react-native';
import { 
  Text, 
  Button, 
  Appbar,
  Card,
  TextInput,
  Divider
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import SignatureCanvas from 'react-native-signature-canvas';
import Toast from 'react-native-toast-message';
import { AuthService } from '../services/AuthService';
import { theme } from '../theme/theme';

export default function SignatureScreen({ navigation, route }) {
  const { delivery, comment } = route.params;
  const signatureRef = useRef();
  const [signedBy, setSignedBy] = useState(delivery.customer_name || '');
  const [signatureData, setSignatureData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSignature = (signature) => {
    setSignatureData(signature);
  };

  const handleClear = () => {
    signatureRef.current?.clearSignature();
    setSignatureData(null);
  };

  const handleSave = async () => {
    if (!signatureData) {
      Alert.alert('Firma Mancante', 'Per favore, fai firmare il cliente prima di procedere.');
      return;
    }

    if (!signedBy.trim()) {
      Alert.alert('Nome Mancante', 'Per favore, inserisci il nome di chi firma.');
      return;
    }

    setLoading(true);
    try {
      await AuthService.markDeliveryCompleted(
        delivery.id,
        comment,
        signatureData,
        signedBy.trim()
      );

      Toast.show({
        type: 'success',
        text1: 'Consegna Completata',
        text2: 'Firma registrata con successo',
      });

      // Navigate back to deliveries list
      navigation.navigate('Deliveries', { refresh: true });
    } catch (error) {
      Toast.show({
        type: 'error',
        text1: 'Errore',
        text2: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    Alert.alert(
      'Salta Firma',
      'Sei sicuro di voler completare la consegna senza firma? Questa azione è irreversibile.',
      [
        { text: 'Annulla', style: 'cancel' },
        { 
          text: 'Conferma', 
          style: 'destructive',
          onPress: async () => {
            setLoading(true);
            try {
              await AuthService.markDeliveryCompleted(
                delivery.id,
                comment,
                null,
                null,
                true // signature skipped
              );

              Toast.show({
                type: 'info',
                text1: 'Consegna Completata',
                text2: 'Completata senza firma',
              });

              navigation.navigate('Deliveries', { refresh: true });
            } catch (error) {
              Toast.show({
                type: 'error',
                text1: 'Errore',
                text2: error.message,
              });
            } finally {
              setLoading(false);
            }
          }
        }
      ]
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Firma Digitale" />
      </Appbar.Header>

      <ScrollView style={styles.scrollContainer}>
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.title}>Raccogli Firma del Cliente</Text>
            <Text style={styles.subtitle}>
              Cliente: {delivery.customer_name}
            </Text>
            <Text style={styles.subtitle}>
              Indirizzo: {delivery.delivery_address}
            </Text>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <TextInput
              label="Nome di chi firma"
              value={signedBy}
              onChangeText={setSignedBy}
              mode="outlined"
              style={styles.input}
              left={<TextInput.Icon icon="account" />}
            />
          </Card.Content>
        </Card>

        <Card style={styles.signatureCard}>
          <Card.Content>
            <Text style={styles.signatureTitle}>Firma sul quadro sottostante</Text>
            <View style={styles.signatureContainer}>
              <SignatureCanvas
                ref={signatureRef}
                onOK={handleSignature}
                descriptionText=""
                clearText="Cancella"
                confirmText="Salva"
                webStyle={`
                  .m-signature-pad {
                    box-shadow: none;
                    border: 2px solid ${theme.colors.outline};
                    border-radius: 8px;
                  }
                  .m-signature-pad--body {
                    border: none;
                  }
                  .m-signature-pad--footer {
                    display: none;
                  }
                `}
              />
            </View>
          </Card.Content>
        </Card>

        <View style={styles.actionButtons}>
          <Button
            mode="outlined"
            onPress={handleClear}
            style={styles.clearButton}
            icon="eraser"
          >
            Cancella Firma
          </Button>
        </View>
      </ScrollView>

      <View style={styles.bottomActions}>
        <Button
          mode="outlined"
          onPress={handleSkip}
          style={styles.skipButton}
          disabled={loading}
          textColor={theme.colors.error}
        >
          Salta Firma
        </Button>
        <Button
          mode="contained"
          onPress={handleSave}
          style={styles.saveButton}
          loading={loading}
          disabled={loading}
          icon="check"
        >
          Conferma e Completa
        </Button>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContainer: {
    flex: 1,
  },
  card: {
    margin: 16,
    marginBottom: 8,
    elevation: 2,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.onSurface,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
    marginBottom: 4,
  },
  input: {
    marginBottom: 8,
  },
  signatureCard: {
    margin: 16,
    marginTop: 8,
    elevation: 2,
  },
  signatureTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.onSurface,
    marginBottom: 12,
  },
  signatureContainer: {
    height: 300,
    borderRadius: 8,
    overflow: 'hidden',
  },
  actionButtons: {
    padding: 16,
    paddingTop: 0,
  },
  clearButton: {
    marginBottom: 8,
  },
  bottomActions: {
    flexDirection: 'row',
    padding: 16,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: theme.colors.outline,
    backgroundColor: theme.colors.surface,
    gap: 12,
  },
  skipButton: {
    flex: 1,
  },
  saveButton: {
    flex: 2,
  },
});
