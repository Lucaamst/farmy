import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Import UI components
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Label } from './components/ui/label';
import { useToast } from './hooks/use-toast';
import { Toaster } from './components/ui/toaster';
import { Truck, Package, Users, Building2, CheckCircle, Clock, User, LogOut, Shield, UserPlus, Plus, Globe } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Simplified translations
const translations = {
  en: {
    appTitle: "FarmyGo",
    signInToAccount: "Sign in to your account",
    username: "Username",
    password: "Password",
    signIn: "Sign In",
    signingIn: "Signing in...",
    enterUsername: "Enter your username",
    enterPassword: "Enter your password",
    demoCredentials: "Demo Credentials:",
    superAdmin: "Super Admin",
    logout: "Logout",
    loginSuccessful: "Login Successful",
    welcomeBackMessage: "Welcome back",
    loginFailed: "Login Failed",
    invalidCredentials: "Invalid credentials",
    superAdminTitle: "Super Admin",
    systemManagement: "System Management Dashboard",
    companyDashboard: "Company Dashboard",
    courierDashboard: "Courier Dashboard",
    welcomeBack: "Welcome back",
    loading: "Loading...",
    error: "Error",
    success: "Success"
  },
  it: {
    appTitle: "FarmyGo",
    signInToAccount: "Accedi al tuo account",
    username: "Nome utente",
    password: "Password",
    signIn: "Accedi",
    signingIn: "Accesso in corso...",
    enterUsername: "Inserisci il nome utente",
    enterPassword: "Inserisci la password",
    demoCredentials: "Credenziali Demo:",
    superAdmin: "Super Admin",
    logout: "Esci",
    loginSuccessful: "Accesso Riuscito",
    welcomeBackMessage: "Bentornato",
    loginFailed: "Accesso Fallito",
    invalidCredentials: "Credenziali non valide",
    superAdminTitle: "Super Amministratore",
    systemManagement: "Dashboard di Gestione Sistema",
    companyDashboard: "Dashboard Azienda",
    courierDashboard: "Dashboard Corriere",
    welcomeBack: "Bentornato",
    loading: "Caricamento...",
    error: "Errore",
    success: "Successo"
  }
};

// Auth Context
const AuthContext = React.createContext();

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState('it');

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    const companyData = localStorage.getItem('company');
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
        if (companyData) {
          setCompany(JSON.parse(companyData));
        }
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } catch (e) {
        console.error('Error parsing stored data:', e);
        localStorage.clear();
      }
    }
    setLoading(false);
  }, []);

  const login = (token, userData, companyData = null) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    if (companyData) {
      localStorage.setItem('company', JSON.stringify(companyData));
      setCompany(companyData);
    }
    setUser(userData);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    window.location.href = '/';
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
    setCompany(null);
    delete axios.defaults.headers.common['Authorization'];
    window.location.href = '/';
  };

  const changeLanguage = (newLanguage) => {
    setLanguage(newLanguage);
  };

  const t = translations[language] || translations.en;

  return (
    <AuthContext.Provider value={{ user, company, login, logout, loading, language, changeLanguage, t }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  return React.useContext(AuthContext);
}

// Login Component
function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, language, changeLanguage, t } = useAuth();
  const { toast } = useToast();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, {
        username,
        password
      });

      const { access_token, user, company } = response.data;
      login(access_token, user, company);
      
      toast({
        title: t.loginSuccessful,
        description: `${t.welcomeBackMessage}, ${user.username}!`,
      });
    } catch (error) {
      toast({
        title: t.loginFailed,
        description: error.response?.data?.detail || t.invalidCredentials,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iNCIvPjwvZz48L2c+PC9zdmc+')] opacity-20"></div>
      
      {/* Language Switcher */}
      <div className="absolute top-4 right-4">
        <Select value={language} onValueChange={changeLanguage}>
          <SelectTrigger className="w-20 bg-white/10 border-white/20 text-white">
            <Globe className="w-4 h-4 mr-1" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="en">EN</SelectItem>
            <SelectItem value="it">IT</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card className="w-full max-w-md backdrop-blur-sm bg-white/10 border-white/20">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
            <Truck className="w-8 h-8 text-white" />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold text-white">{t.appTitle}</CardTitle>
            <CardDescription className="text-blue-100">{t.signInToAccount}</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username" className="text-white">{t.username}</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="bg-white/10 border-white/20 text-white placeholder:text-white/60"
                placeholder={t.enterUsername}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-white">{t.password}</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-white/10 border-white/20 text-white placeholder:text-white/60"
                placeholder={t.enterPassword}
              />
            </div>
            <Button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5"
              disabled={loading}
            >
              {loading ? t.signingIn : t.signIn}
            </Button>
          </form>
          
          <div className="mt-6 p-4 bg-blue-950/30 rounded-lg border border-blue-800/30">
            <p className="text-xs text-blue-200 mb-2 font-medium">{t.demoCredentials}</p>
            <p className="text-xs text-blue-300">{t.superAdmin}: superadmin / admin123</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Simple Dashboard Component
function Dashboard() {
  const { user, logout, t } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="container mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {user.role === 'super_admin' ? t.superAdminTitle : 
               user.role === 'company_admin' ? t.companyDashboard : 
               t.courierDashboard}
            </h1>
            <p className="text-gray-600">{t.welcomeBack}, {user.username}</p>
          </div>
          <Button onClick={logout} variant="outline">
            <LogOut className="w-4 h-4 mr-2" />
            {t.logout}
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Dashboard Semplificata</CardTitle>
            <CardDescription>Applicazione in modalità sicura - tutte le funzionalità saranno ripristinate</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">FarmyGo Funziona!</h2>
              <p className="text-gray-600">
                Login completato con successo. Ruolo: <Badge>{user.role}</Badge>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Protected Route Component
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// Main App Component
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
          </Routes>
          <Toaster />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;