import React, { useState, useEffect, useCallback } from 'react';
import { View, StyleSheet, FlatList, RefreshControl, Alert } from 'react-native';
import { 
  Text, 
  Card, 
  Button, 
  Chip, 
  FAB,
  Appbar,
  Badge,
  ActivityIndicator 
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Toast from 'react-native-toast-message';
import { AuthService } from '../services/AuthService';
import { theme } from '../theme/theme';

export default function DeliveriesScreen({ navigation, route }) {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    useCallback(() => {
      fetchDeliveries();
    }, [])
  );

  const fetchDeliveries = async () => {
    try {
      setLoading(true);
      const data = await AuthService.getDeliveries();
      setDeliveries(data);
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

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDeliveries();
    setRefreshing(false);
  };

  const handleStartDelivery = async (orderId) => {
    try {
      await AuthService.markDeliveryInProgress(orderId);
      Toast.show({
        type: 'success',
        text1: 'Consegna Avviata',
        text2: 'La consegna è ora in corso',
      });
      fetchDeliveries();
    } catch (error) {
      Toast.show({
        type: 'error',
        text1: 'Errore',
        text2: error.message,
      });
    }
  };

  const handleCompleteDelivery = async (orderId) => {
    Alert.alert(
      'Conferma Consegna',
      'Sei sicuro di voler segnare questa consegna come completata?',
      [
        { text: 'Annulla', style: 'cancel' },
        { 
          text: 'Conferma', 
          onPress: async () => {
            try {
              await AuthService.markDeliveryCompleted(orderId);
              Toast.show({
                type: 'success',
                text1: 'Consegna Completata',
                text2: 'Il cliente è stato notificato',
              });
              fetchDeliveries();
            } catch (error) {
              Toast.show({
                type: 'error',
                text1: 'Errore',
                text2: error.message,
              });
            }
          }
        }
      ]
    );
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
      >
        {config.label}
      </Chip>
    );
  };

  const renderDeliveryItem = ({ item }) => {
    const isAssigned = item.status === 'assigned';
    const isInProgress = item.status === 'in_progress';
    const isDelivered = item.status === 'delivered';

    return (
      <Card style={styles.deliveryCard} mode="outlined">
        <Card.Content>
          <View style={styles.cardHeader}>
            <Text style={styles.customerName}>{item.customer_name}</Text>
            {getStatusChip(item.status)}
          </View>

          <View style={styles.addressContainer}>
            <Icon name="location-on" size={16} color={theme.colors.onSurfaceVariant} />
            <Text style={styles.address}>{item.delivery_address}</Text>
          </View>

          {item.reference_number && (
            <View style={styles.referenceContainer}>
              <Icon name="assignment" size={16} color={theme.colors.onSurfaceVariant} />
              <Text style={styles.reference}>Rif: {item.reference_number}</Text>
            </View>
          )}

          <View style={styles.timeContainer}>
            <Icon name="access-time" size={16} color={theme.colors.onSurfaceVariant} />
            <Text style={styles.time}>
              Creato: {new Date(item.created_at).toLocaleString('it-IT')}
            </Text>
          </View>

          <View style={styles.actionContainer}>
            {isAssigned && (
              <Button
                mode="contained"
                onPress={() => handleStartDelivery(item.id)}
                style={styles.actionButton}
                icon="play-arrow"
              >
                Inizia Consegna
              </Button>
            )}

            {isInProgress && (
              <Button
                mode="contained"
                onPress={() => handleCompleteDelivery(item.id)}
                style={[styles.actionButton, { backgroundColor: theme.colors.tertiary }]}
                icon="check-circle"
              >
                Consegna Completata
              </Button>
            )}

            <Button
              mode="outlined"
              onPress={() => navigation.navigate('DeliveryDetail', { delivery: item })}
              style={styles.detailButton}
              icon="info"
            >
              Dettagli
            </Button>
          </View>
        </Card.Content>
      </Card>
    );
  };

  const activeCount = deliveries.filter(d => ['assigned', 'in_progress'].includes(d.status)).length;
  const completedCount = deliveries.filter(d => d.status === 'delivered').length;

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <Appbar.Header>
          <Appbar.Content title="Le Mie Consegne" />
        </Appbar.Header>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text style={styles.loadingText}>Caricamento consegne...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Le Mie Consegne" />
        {activeCount > 0 && (
          <Badge size={24} style={styles.badge}>{activeCount}</Badge>
        )}
      </Appbar.Header>

      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{activeCount}</Text>
          <Text style={styles.statLabel}>Attive</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{completedCount}</Text>
          <Text style={styles.statLabel}>Completate</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{deliveries.length}</Text>
          <Text style={styles.statLabel}>Totali</Text>
        </View>
      </View>

      <FlatList
        data={deliveries}
        renderItem={renderDeliveryItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[theme.colors.primary]}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="local-shipping" size={64} color={theme.colors.onSurfaceVariant} />
            <Text style={styles.emptyText}>Nessuna consegna disponibile</Text>
            <Text style={styles.emptySubtext}>
              Le nuove consegne appariranno qui quando ti verranno assegnate
            </Text>
          </View>
        }
      />

      <FAB
        style={styles.fab}
        icon="refresh"
        onPress={fetchDeliveries}
        label="Aggiorna"
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  loadingText: {
    color: theme.colors.onSurfaceVariant,
  },
  badge: {
    backgroundColor: theme.colors.tertiary,
    marginRight: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 16,
    paddingHorizontal: 20,
    backgroundColor: theme.colors.surface,
    elevation: 2,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginTop: 4,
  },
  listContainer: {
    padding: 16,
    paddingBottom: 80,
  },
  deliveryCard: {
    marginBottom: 12,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  customerName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.onSurface,
    flex: 1,
    marginRight: 12,
  },
  addressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  address: {
    marginLeft: 8,
    flex: 1,
    color: theme.colors.onSurface,
  },
  referenceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  reference: {
    marginLeft: 8,
    color: theme.colors.onSurfaceVariant,
    fontSize: 12,
  },
  timeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  time: {
    marginLeft: 8,
    color: theme.colors.onSurfaceVariant,
    fontSize: 12,
  },
  actionContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    flex: 1,
  },
  detailButton: {
    flex: 0.6,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.onSurfaceVariant,
    marginTop: 16,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
    marginTop: 8,
    textAlign: 'center',
    paddingHorizontal: 32,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: theme.colors.primary,
  },
});