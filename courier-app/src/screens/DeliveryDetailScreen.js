import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Linking, Alert } from 'react-native';
import { 
  Text, 
  Card, 
  Button, 
  Chip, 
  Appbar,
  Divider,
  List,
  Badge,
  ActivityIndicator,
  Dialog,
  Portal,
  TextInput as PaperTextInput
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Toast from 'react-native-toast-message';
import { AuthService } from '../services/AuthService';
import { theme } from '../theme/theme';

export default function DeliveryDetailScreen({ navigation, route }) {
  const { delivery: initialDelivery } = route.params;
  const [delivery, setDelivery] = useState(initialDelivery);
  const [loading, setLoading] = useState(false);
  const [showCommentDialog, setShowCommentDialog] = useState(false);
  const [deliveryComment, setDeliveryComment] = useState('');

  useEffect(() => {
    navigation.setOptions({
      title: `Consegna ${delivery.id?.slice(-6) || 'N/A'}`,
    });
  }, [delivery]);

  const handleStartDelivery = async () => {
    setLoading(true);
    try {
      await AuthService.markDeliveryInProgress(delivery.id);
      setDelivery({ ...delivery, status: 'in_progress' });
      Toast.show({
        type: 'success',
        text1: 'Consegna Avviata',
        text2: 'La consegna è ora in corso',
      });
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

  const handleCompleteDelivery = () => {
    // Show comment dialog first
    setShowCommentDialog(true);
  };

  const confirmCompleteDelivery = async () => {
    setShowCommentDialog(false);
    
    // Check if signature is required
    if (delivery.requires_signature) {
      // Navigate to signature screen
      navigation.navigate('Signature', {
        delivery: delivery,
        comment: deliveryComment.trim() || null
      });
    } else {
      // Complete without signature
      Alert.alert(
        'Conferma Consegna',
        'Completare la consegna senza firma?',
        [
          { text: 'Annulla', style: 'cancel' },
          { 
            text: 'Conferma', 
            onPress: async () => {
              setLoading(true);
              try {
                await AuthService.markDeliveryCompleted(
                  delivery.id, 
                  deliveryComment.trim() || null
                );
                setDelivery({ ...delivery, status: 'delivered' });
                Toast.show({
                  type: 'success',
                  text1: 'Consegna Completata',
                  text2: 'Il cliente è stato notificato',
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
    }
  };

  const openMaps = () => {
    if (delivery.delivery_address) {
      const url = `https://maps.google.com/?q=${encodeURIComponent(delivery.delivery_address)}`;
      Linking.openURL(url).catch(() => {
        Toast.show({
          type: 'error',
          text1: 'Errore',
          text2: 'Impossibile aprire le mappe',
        });
      });
    }
  };

  const callCustomer = () => {
    if (delivery.phone_number) {
      const url = `tel:${delivery.phone_number}`;
      Linking.openURL(url).catch(() => {
        Toast.show({
          type: 'error',
          text1: 'Errore',
          text2: 'Impossibile effettuare la chiamata',
        });
      });
    } else {
      Toast.show({
        type: 'info',
        text1: 'Numero Non Disponibile',
        text2: 'Il cliente non ha fornito un numero di telefono',
      });
    }
  };

  const getStatusChip = (status) => {
    const statusConfig = {
      assigned: { 
        label: 'Assegnato', 
        icon: 'assignment',
        color: theme.colors.secondary 
      },
      in_progress: { 
        label: 'In Corso', 
        icon: 'local-shipping',
        color: theme.colors.tertiary 
      },
      delivered: { 
        label: 'Consegnato', 
        icon: 'check-circle',
        color: theme.colors.primary 
      }
    };

    const config = statusConfig[status] || statusConfig.assigned;
    
    return (
      <Chip 
        icon={config.icon} 
        style={{ backgroundColor: config.color + '20' }}
        textStyle={{ color: config.color }}
        mode="outlined"
      >
        {config.label}
      </Chip>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isAssigned = delivery.status === 'assigned';
  const isInProgress = delivery.status === 'in_progress';
  const isDelivered = delivery.status === 'delivered';

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollContainer}>
        {/* Status Card */}
        <Card style={styles.statusCard}>
          <Card.Content>
            <View style={styles.statusHeader}>
              <Text style={styles.deliveryId}>
                Consegna #{delivery.id?.slice(-8) || 'N/A'}
              </Text>
              {getStatusChip(delivery.status)}
            </View>
          </Card.Content>
        </Card>

        {/* Customer Info Card */}
        <Card style={styles.infoCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Informazioni Cliente</Text>
            
            <List.Item
              title={delivery.customer_name || 'Nome non disponibile'}
              description="Nome Cliente"
              left={props => <List.Icon {...props} icon="person" />}
            />
            
            <Divider />
            
            <List.Item
              title={delivery.delivery_address || 'Indirizzo non disponibile'}
              description="Indirizzo di Consegna"
              left={props => <List.Icon {...props} icon="location-on" />}
              right={props => (
                <Button 
                  mode="outlined" 
                  compact 
                  onPress={openMaps}
                  icon="map"
                >
                  Mappa
                </Button>
              )}
            />
            
            <Divider />
            
            <List.Item
              title={delivery.phone_number || 'Non fornito'}
              description="Numero di Telefono"
              left={props => <List.Icon {...props} icon="phone" />}
              right={props => (
                delivery.phone_number ? (
                  <Button 
                    mode="outlined" 
                    compact 
                    onPress={callCustomer}
                    icon="call"
                  >
                    Chiama
                  </Button>
                ) : null
              )}
            />
          </Card.Content>
        </Card>

        {/* Delivery Details Card */}
        <Card style={styles.infoCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Dettagli Consegna</Text>
            
            {delivery.reference_number && (
              <>
                <List.Item
                  title={delivery.reference_number}
                  description="Numero di Riferimento"
                  left={props => <List.Icon {...props} icon="assignment" />}
                />
                <Divider />
              </>
            )}
            
            <List.Item
              title={formatDate(delivery.created_at)}
              description="Data Creazione"
              left={props => <List.Icon {...props} icon="schedule" />}
            />
            
            {delivery.delivered_at && (
              <>
                <Divider />
                <List.Item
                  title={formatDate(delivery.delivered_at)}
                  description="Data Consegna"
                  left={props => <List.Icon {...props} icon="check-circle" />}
                />
              </>
            )}
            
            {delivery.notes && (
              <>
                <Divider />
                <List.Item
                  title={delivery.notes}
                  description="Note"
                  left={props => <List.Icon {...props} icon="note" />}
                />
              </>
            )}
          </Card.Content>
        </Card>

        {/* Quick Actions Card */}
        <Card style={styles.actionsCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Azioni Rapide</Text>
            
            <View style={styles.quickActions}>
              <Button
                mode="outlined"
                icon="map"
                onPress={openMaps}
                style={styles.quickActionButton}
              >
                Naviga
              </Button>
              
              {delivery.phone_number && (
                <Button
                  mode="outlined"
                  icon="call"
                  onPress={callCustomer}
                  style={styles.quickActionButton}
                >
                  Chiama
                </Button>
              )}
            </View>
          </Card.Content>
        </Card>
      </ScrollView>

      {/* Action Buttons */}
      <View style={styles.actionContainer}>
        {isAssigned && (
          <Button
            mode="contained"
            onPress={handleStartDelivery}
            style={styles.primaryButton}
            loading={loading}
            disabled={loading}
            icon="play-arrow"
          >
            {loading ? 'Avvio...' : 'Inizia Consegna'}
          </Button>
        )}

        {isInProgress && (
          <Button
            mode="contained"
            onPress={handleCompleteDelivery}
            style={[styles.primaryButton, { backgroundColor: theme.colors.tertiary }]}
            loading={loading}
            disabled={loading}
            icon="check-circle"
          >
            {loading ? 'Completamento...' : 'Consegna Completata'}
          </Button>
        )}

        {isDelivered && (
          <View style={styles.completedContainer}>
            <Icon name="check-circle" size={24} color={theme.colors.tertiary} />
            <Text style={styles.completedText}>Consegna Completata</Text>
          </View>
        )}
      </View>

      {/* Comment Dialog */}
      <Portal>
        <Dialog visible={showCommentDialog} onDismiss={() => setShowCommentDialog(false)}>
          <Dialog.Title>Commento Consegna</Dialog.Title>
          <Dialog.Content>
            <Text style={{ marginBottom: 12 }}>
              Vuoi aggiungere un commento per questa consegna? (Opzionale)
            </Text>
            <PaperTextInput
              label="Commento (opzionale)"
              value={deliveryComment}
              onChangeText={setDeliveryComment}
              mode="outlined"
              multiline
              numberOfLines={3}
              placeholder="Es: Consegnato al vicino, Lasciato in portineria..."
            />
            {delivery.requires_signature && (
              <View style={{ 
                marginTop: 12, 
                padding: 8, 
                backgroundColor: '#E3F2FD', 
                borderRadius: 4,
                flexDirection: 'row',
                alignItems: 'center'
              }}>
                <Icon name="gesture" size={20} color={theme.colors.primary} />
                <Text style={{ marginLeft: 8, color: theme.colors.primary, fontSize: 12 }}>
                  Questa consegna richiede una firma digitale
                </Text>
              </View>
            )}
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setShowCommentDialog(false)}>Annulla</Button>
            <Button onPress={confirmCompleteDelivery}>Continua</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
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
  statusCard: {
    margin: 16,
    elevation: 4,
  },
  statusHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  deliveryId: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.onSurface,
  },
  infoCard: {
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
  },
  actionsCard: {
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.onSurface,
    marginBottom: 8,
  },
  quickActions: {
    flexDirection: 'row',
    gap: 12,
  },
  quickActionButton: {
    flex: 1,
  },
  actionContainer: {
    padding: 16,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: theme.colors.outline,
    backgroundColor: theme.colors.surface,
  },
  primaryButton: {
    paddingVertical: 4,
  },
  completedContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 12,
  },
  completedText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.tertiary,
  },
});