import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, Alert, Dimensions } from 'react-native';
import { 
  Text, 
  Card, 
  Button, 
  Chip, 
  Appbar,
  ActivityIndicator,
  FAB 
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import * as Location from 'expo-location';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Toast from 'react-native-toast-message';
import { AuthService } from '../services/AuthService';
import { theme } from '../theme/theme';

const { width, height } = Dimensions.get('window');

export default function MapScreen({ navigation }) {
  const [location, setLocation] = useState(null);
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [trackingUser, setTrackingUser] = useState(false);
  const mapRef = useRef(null);

  useEffect(() => {
    requestLocationPermission();
    fetchDeliveries();
  }, []);

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(
          'Permesso Richiesto',
          'FarmyGo ha bisogno dell\'accesso alla posizione per mostrarti le consegne sulla mappa.',
          [{ text: 'OK' }]
        );
        return;
      }

      getCurrentLocation();
    } catch (error) {
      console.error('Location permission error:', error);
    }
  };

  const getCurrentLocation = async () => {
    try {
      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });
      setLocation(currentLocation.coords);
    } catch (error) {
      console.error('Get location error:', error);
      Toast.show({
        type: 'error',
        text1: 'Errore GPS',
        text2: 'Impossibile ottenere la posizione attuale',
      });
    }
  };

  const fetchDeliveries = async () => {
    try {
      setLoading(true);
      const data = await AuthService.getDeliveries();
      // Filtra solo consegne attive (assegnate e in corso)
      const activeDeliveries = data.filter(d => 
        ['assigned', 'in_progress'].includes(d.status)
      );
      setDeliveries(activeDeliveries);
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

  const centerOnUser = () => {
    if (location && mapRef.current) {
      mapRef.current.animateToRegion({
        latitude: location.latitude,
        longitude: location.longitude,
        latitudeDelta: 0.005,
        longitudeDelta: 0.005,
      }, 1000);
      setTrackingUser(true);
    }
  };

  const centerOnDeliveries = () => {
    if (deliveries.length > 0 && mapRef.current) {
      // Calcola i bounds per includere tutte le consegne
      let minLat = deliveries[0].latitude || 41.9028;
      let maxLat = deliveries[0].latitude || 41.9028;
      let minLng = deliveries[0].longitude || 12.4964;
      let maxLng = deliveries[0].longitude || 12.4964;

      deliveries.forEach(delivery => {
        if (delivery.latitude && delivery.longitude) {
          minLat = Math.min(minLat, delivery.latitude);
          maxLat = Math.max(maxLat, delivery.latitude);
          minLng = Math.min(minLng, delivery.longitude);
          maxLng = Math.max(maxLng, delivery.longitude);
        }
      });

      mapRef.current.animateToRegion({
        latitude: (minLat + maxLat) / 2,
        longitude: (minLng + maxLng) / 2,
        latitudeDelta: (maxLat - minLat) * 1.2,
        longitudeDelta: (maxLng - minLng) * 1.2,
      }, 1000);
    }
  };

  const getMarkerColor = (status) => {
    switch (status) {
      case 'assigned': return '#dc2626'; // Rosso
      case 'in_progress': return '#059669'; // Verde
      default: return '#ea580c'; // Arancione
    }
  };

  const handleMarkerPress = (delivery) => {
    navigation.navigate('DeliveryDetail', { delivery });
  };

  const initialRegion = location ? {
    latitude: location.latitude,
    longitude: location.longitude,
    latitudeDelta: 0.01,
    longitudeDelta: 0.01,
  } : {
    // Default: Roma centro
    latitude: 41.9028,
    longitude: 12.4964,
    latitudeDelta: 0.1,
    longitudeDelta: 0.1,
  };

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Mappa Consegne" />
        <Appbar.Action 
          icon="my-location" 
          onPress={centerOnUser}
          disabled={!location}
        />
        <Appbar.Action 
          icon="zoom-out-map" 
          onPress={centerOnDeliveries}
          disabled={deliveries.length === 0}
        />
      </Appbar.Header>

      <View style={styles.mapContainer}>
        <MapView
          ref={mapRef}
          style={styles.map}
          provider={PROVIDER_GOOGLE}
          initialRegion={initialRegion}
          showsUserLocation={true}
          showsMyLocationButton={false}
          showsCompass={true}
          showsScale={true}
          onRegionChangeComplete={() => setTrackingUser(false)}
        >
          {deliveries.map((delivery) => {
            // Usa coordinate mock se non disponibili
            const latitude = delivery.latitude || (41.9028 + Math.random() * 0.01);
            const longitude = delivery.longitude || (12.4964 + Math.random() * 0.01);
            
            return (
              <Marker
                key={delivery.id}
                coordinate={{ latitude, longitude }}
                title={delivery.customer_name}
                description={delivery.delivery_address}
                pinColor={getMarkerColor(delivery.status)}
                onPress={() => handleMarkerPress(delivery)}
              />
            );
          })}
        </MapView>

        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={styles.loadingText}>Caricamento consegne...</Text>
          </View>
        )}
      </View>

      <View style={styles.legend}>
        <Card style={styles.legendCard}>
          <Card.Content style={styles.legendContent}>
            <Text style={styles.legendTitle}>Legenda</Text>
            <View style={styles.legendItems}>
              <View style={styles.legendItem}>
                <View style={[styles.legendDot, { backgroundColor: '#dc2626' }]} />
                <Text style={styles.legendText}>Assegnato</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendDot, { backgroundColor: '#059669' }]} />
                <Text style={styles.legendText}>In Corso</Text>
              </View>
            </View>
          </Card.Content>
        </Card>
      </View>

      <FAB
        style={styles.fab}
        icon="refresh"
        onPress={fetchDeliveries}
        small
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  mapContainer: {
    flex: 1,
    position: 'relative',
  },
  map: {
    width: width,
    height: '100%',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  loadingText: {
    color: theme.colors.onSurfaceVariant,
  },
  legend: {
    position: 'absolute',
    top: 16,
    right: 16,
  },
  legendCard: {
    elevation: 4,
  },
  legendContent: {
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  legendTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 8,
    color: theme.colors.onSurface,
  },
  legendItems: {
    gap: 4,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  legendText: {
    fontSize: 11,
    color: theme.colors.onSurfaceVariant,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: theme.colors.primary,
  },
});