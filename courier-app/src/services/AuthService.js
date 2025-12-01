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

    // Add request interceptor to include auth token
    this.apiClient.interceptors.request.use(async (config) => {
      const token = await SecureStore.getItemAsync('farmygo_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  async login(username, password) {
    try {
      const response = await this.apiClient.post('/auth/login', {
        username,
        password,
      });

      const { access_token, user } = response.data;

      // Only allow courier role
      if (user.role !== 'courier') {
        throw new Error('Accesso negato. Solo i corrieri possono utilizzare questa app.');
      }

      // Store token securely
      await SecureStore.setItemAsync('farmygo_token', access_token);

      return user;
    } catch (error) {
      console.error('Login failed:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
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
      console.error('Token validation failed:', error);
      return null;
    }
  }

  async logout() {
    try {
      await SecureStore.deleteItemAsync('farmygo_token');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }

  async getDeliveries() {
    try {
      const response = await this.apiClient.get('/courier/deliveries');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch deliveries:', error);
      throw new Error('Impossibile caricare le consegne');
    }
  }

  async markDeliveryInProgress(orderId) {
    try {
      const response = await this.apiClient.patch('/courier/deliveries/start', {
        order_id: orderId
      });
      return response.data;
    } catch (error) {
      console.error('Failed to mark in progress:', error);
      throw new Error('Impossibile avviare la consegna');
    }
  }

  async markDeliveryCompleted(orderId, deliveryComment = null, signatureData = null, signedByName = null, signatureSkipped = false) {
    try {
      const requestBody = {
        order_id: orderId,
        delivery_comment: deliveryComment,
        signature_data: signatureData,
        signed_by_name: signedByName,
        signature_skipped: signatureSkipped
      };

      const response = await this.apiClient.patch('/courier/deliveries/mark-delivered', requestBody);
      return response.data;
    } catch (error) {
      console.error('Failed to mark completed:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Impossibile completare la consegna'
      );
    }
  }

  async setPIN(pinCode) {
    try {
      const response = await this.apiClient.post('/courier/set-pin', {
        pin_code: pinCode
      });
      return response.data;
    } catch (error) {
      console.error('Failed to set PIN:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Impossibile impostare il PIN'
      );
    }
  }

  async verifyPIN(pinCode) {
    try {
      const response = await this.apiClient.post('/courier/verify-pin', {
        pin_code: pinCode
      });
      return response.data;
    } catch (error) {
      console.error('Failed to verify PIN:', error);
      throw new Error(
        error.response?.data?.detail || 
        'PIN non valido'
      );
    }
  }
}

export const AuthService = new AuthServiceClass();
export default AuthService;