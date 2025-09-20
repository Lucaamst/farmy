import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { 
  Text, 
  Card, 
  Button, 
  Avatar, 
  List,
  Divider,
  Switch,
  Appbar,
  Dialog,
  Portal,
  Paragraph 
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as SecureStore from 'expo-secure-store';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Toast from 'react-native-toast-message';
import { AuthService } from '../services/AuthService';
import { theme } from '../theme/theme';

export default function ProfileScreen({ navigation, route }) {
  const [user, setUser] = useState(null);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [locationEnabled, setLocationEnabled] = useState(true);
  const [logoutDialogVisible, setLogoutDialogVisible] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUserData();
    loadSettings();
  }, []);

  const loadUserData = async () => {
    try {
      const token = await SecureStore.getItemAsync('farmygo_token');
      if (token) {
        const userData = await AuthService.validateToken(token);
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  };

  const loadSettings = async () => {
    try {
      const notifications = await SecureStore.getItemAsync('notifications_enabled');
      const location = await SecureStore.getItemAsync('location_enabled');
      
      setNotificationsEnabled(notifications !== 'false');
      setLocationEnabled(location !== 'false');
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handleNotificationToggle = async () => {
    const newValue = !notificationsEnabled;
    setNotificationsEnabled(newValue);
    
    try {
      await SecureStore.setItemAsync('notifications_enabled', newValue.toString());
      Toast.show({
        type: 'success',
        text1: 'Impostazioni Aggiornate',
        text2: `Notifiche ${newValue ? 'attivate' : 'disattivate'}`,
      });
    } catch (error) {
      console.error('Failed to save notification setting:', error);
      setNotificationsEnabled(!newValue); // Revert on error
    }
  };

  const handleLocationToggle = async () => {
    const newValue = !locationEnabled;
    setLocationEnabled(newValue);
    
    try {
      await SecureStore.setItemAsync('location_enabled', newValue.toString());
      Toast.show({
        type: 'success',
        text1: 'Impostazioni Aggiornate',
        text2: `Localizzazione ${newValue ? 'attivata' : 'disattivata'}`,
      });
    } catch (error) {
      console.error('Failed to save location setting:', error);
      setLocationEnabled(!newValue); // Revert on error
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await AuthService.logout();
      // Navigation will be handled by App.js auth state change
    } catch (error) {
      console.error('Logout failed:', error);
      Toast.show({
        type: 'error',
        text1: 'Errore Logout',
        text2: 'Si è verificato un errore durante il logout',
      });
    } finally {
      setLoading(false);
      setLogoutDialogVisible(false);
    }
  };

  const showLogoutDialog = () => {
    setLogoutDialogVisible(true);
  };

  const hideLogoutDialog = () => {
    setLogoutDialogVisible(false);
  };

  const getInitials = (name) => {
    if (!name) return 'C';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  if (!user) {
    return (
      <SafeAreaView style={styles.container}>
        <Appbar.Header>
          <Appbar.Content title="Profilo" />
        </Appbar.Header>
        <View style={styles.loadingContainer}>
          <Text>Caricamento profilo...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Profilo" />
      </Appbar.Header>

      <ScrollView style={styles.scrollContainer}>
        {/* User Info Section */}
        <Card style={styles.profileCard}>
          <Card.Content style={styles.profileContent}>
            <Avatar.Text 
              size={80} 
              label={getInitials(user.full_name || user.username)} 
              style={styles.avatar}
            />
            <Text style={styles.userName}>
              {user.full_name || user.username}
            </Text>
            <Text style={styles.userRole}>Corriere FarmyGo</Text>
            <Text style={styles.userEmail}>{user.email}</Text>
          </Card.Content>
        </Card>

        {/* Stats Section */}
        <Card style={styles.statsCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Statistiche</Text>
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Icon name="local-shipping" size={24} color={theme.colors.primary} />
                <Text style={styles.statNumber}>--</Text>
                <Text style={styles.statLabel}>Consegne Totali</Text>
              </View>
              <View style={styles.statItem}>
                <Icon name="check-circle" size={24} color={theme.colors.tertiary} />
                <Text style={styles.statNumber}>--</Text>
                <Text style={styles.statLabel}>Questo Mese</Text>
              </View>
              <View style={styles.statItem}>
                <Icon name="star" size={24} color="#fbbf24" />
                <Text style={styles.statNumber}>5.0</Text>
                <Text style={styles.statLabel}>Valutazione</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Settings Section */}
        <Card style={styles.settingsCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Impostazioni</Text>
            
            <List.Item
              title="Notifiche Push"
              description="Ricevi notifiche per nuove consegne"
              left={props => <List.Icon {...props} icon="notifications" />}
              right={() => (
                <Switch
                  value={notificationsEnabled}
                  onValueChange={handleNotificationToggle}
                />
              )}
            />
            
            <Divider />
            
            <List.Item
              title="Localizzazione"
              description="Condividi la tua posizione per le consegne"
              left={props => <List.Icon {...props} icon="location-on" />}
              right={() => (
                <Switch
                  value={locationEnabled}
                  onValueChange={handleLocationToggle}
                />
              )}
            />
          </Card.Content>
        </Card>

        {/* Actions Section */}
        <Card style={styles.actionsCard}>
          <Card.Content>
            <Text style={styles.sectionTitle}>Azioni</Text>
            
            <List.Item
              title="Centro Assistenza"
              description="Ottieni aiuto e supporto"
              left={props => <List.Icon {...props} icon="help" />}
              right={props => <List.Icon {...props} icon="chevron-right" />}
              onPress={() => {
                Toast.show({
                  type: 'info',
                  text1: 'Centro Assistenza',
                  text2: 'Contatta: support@farmygo.ch',
                });
              }}
            />
            
            <Divider />
            
            <List.Item
              title="Informazioni App"
              description="Versione 1.0.0"
              left={props => <List.Icon {...props} icon="info" />}
              right={props => <List.Icon {...props} icon="chevron-right" />}
            />
            
            <Divider />
            
            <List.Item
              title="Logout"
              description="Esci dall'applicazione"
              left={props => <List.Icon {...props} icon="logout" color={theme.colors.error} />}
              titleStyle={{ color: theme.colors.error }}
              onPress={showLogoutDialog}
            />
          </Card.Content>
        </Card>

        <View style={styles.footer}>
          <Text style={styles.footerText}>FarmyGo Courier App</Text>
          <Text style={styles.footerVersion}>Versione 1.0.0</Text>
        </View>
      </ScrollView>

      {/* Logout Confirmation Dialog */}
      <Portal>
        <Dialog visible={logoutDialogVisible} onDismiss={hideLogoutDialog}>
          <Dialog.Icon icon="logout" />
          <Dialog.Title>Conferma Logout</Dialog.Title>
          <Dialog.Content>
            <Paragraph>
              Sei sicuro di voler uscire dall'applicazione? 
              Dovrai effettuare nuovamente il login per accedere.
            </Paragraph>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={hideLogoutDialog}>Annulla</Button>
            <Button 
              onPress={handleLogout} 
              loading={loading}
              disabled={loading}
            >
              Logout
            </Button>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileCard: {
    margin: 16,
    elevation: 4,
  },
  profileContent: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  avatar: {
    backgroundColor: theme.colors.primary,
    marginBottom: 16,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.onSurface,
    marginBottom: 4,
  },
  userRole: {
    fontSize: 16,
    color: theme.colors.primary,
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
  },
  statsCard: {
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.onSurface,
    marginBottom: 16,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
    gap: 8,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.onSurface,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
  },
  settingsCard: {
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
  },
  actionsCard: {
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
  },
  footer: {
    alignItems: 'center',
    padding: 24,
    gap: 4,
  },
  footerText: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
    fontWeight: '500',
  },
  footerVersion: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
  },
});