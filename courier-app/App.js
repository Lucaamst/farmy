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
        // Navigate to deliveries screen
        // navigationRef.current?.navigate('Consegne');
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