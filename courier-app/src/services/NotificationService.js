import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform, Alert } from 'react-native';

class NotificationServiceClass {
  constructor() {
    this.token = null;
  }

  async initialize() {
    try {
      // Check if device supports push notifications
      if (!Device.isDevice) {
        console.log('Push notifications are not supported on simulator/emulator');
        return null;
      }

      // Request permissions
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.log('Push notification permission denied');
        Alert.alert(
          'Permessi Notifiche',
          'Per ricevere notifiche sui nuovi ordini, attiva i permessi nelle impostazioni.',
          [{ text: 'OK' }]
        );
        return null;
      }

      // Get push token
      this.token = await this.getExpoPushToken();
      console.log('Expo push token:', this.token);

      // Configure notification channel for Android
      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('farmygo-deliveries', {
          name: 'FarmyGo Consegne',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#ea580c',
          sound: 'default',
        });
      }

      return this.token;
    } catch (error) {
      console.error('Notification initialization failed:', error);
      return null;
    }
  }

  async getExpoPushToken() {
    try {
      const projectId = Constants.expoConfig?.extra?.eas?.projectId;
      
      if (!projectId) {
        throw new Error('Project ID not found in app configuration');
      }

      const token = await Notifications.getExpoPushTokenAsync({
        projectId,
      });

      return token.data;
    } catch (error) {
      console.error('Error getting Expo push token:', error);
      throw error;
    }
  }

  async scheduleLocalNotification(title, body, data = {}) {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: 'default',
          priority: Notifications.AndroidNotificationPriority.HIGH,
        },
        trigger: null, // Show immediately
      });
    } catch (error) {
      console.error('Error scheduling local notification:', error);
    }
  }

  async cancelAllNotifications() {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
    } catch (error) {
      console.error('Error canceling notifications:', error);
    }
  }

  async getBadgeCount() {
    try {
      return await Notifications.getBadgeCountAsync();
    } catch (error) {
      console.error('Error getting badge count:', error);
      return 0;
    }
  }

  async setBadgeCount(count) {
    try {
      await Notifications.setBadgeCountAsync(count);
    } catch (error) {
      console.error('Error setting badge count:', error);
    }
  }

  async clearBadge() {
    try {
      await Notifications.setBadgeCountAsync(0);
    } catch (error) {
      console.error('Error clearing badge:', error);
    }
  }

  // Notification handlers
  addNotificationReceivedListener(handler) {
    return Notifications.addNotificationReceivedListener(handler);
  }

  addNotificationResponseReceivedListener(handler) {
    return Notifications.addNotificationResponseReceivedListener(handler);
  }

  removeNotificationSubscription(subscription) {
    if (subscription) {
      Notifications.removeNotificationSubscription(subscription);
    }
  }

  // Test notification (for development)
  async sendTestNotification() {
    try {
      await this.scheduleLocalNotification(
        'Test Notifica FarmyGo',
        'Questa è una notifica di test per verificare il funzionamento del sistema.',
        { type: 'test' }
      );
    } catch (error) {
      console.error('Error sending test notification:', error);
    }
  }
}

export const NotificationService = new NotificationServiceClass();