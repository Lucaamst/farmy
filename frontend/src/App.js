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

// Complete translations
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
    success: "Success",
    addCompany: "Add Company",
    companiesManagement: "Companies Management",
    manageAllCompanies: "Manage all registered companies",
    companyName: "Company Name",
    totalDeliveries: "Total Deliveries",
    activeCouriers: "Active Couriers",
    status: "Status",
    created: "Created",
    actions: "Actions",
    active: "Active",
    disabled: "Disabled",
    enable: "Enable",
    disable: "Disable",
    edit: "Edit",
    delete: "Delete",
    yourDeliveries: "Your Deliveries",
    manageAssignedOrders: "Manage your assigned delivery orders",
    activeDeliveries: "Active Deliveries",
    assigned: "Assigned",
    inProgress: "In Progress",
    delivered: "Delivered",
    pending: "Pending",
    markAsDelivered: "Mark as Delivered",
    noActiveDeliveries: "No active deliveries at the moment",
    createdAt: "Created on"
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
    success: "Successo",
    addCompany: "Aggiungi Azienda",
    companiesManagement: "Gestione Aziende",
    manageAllCompanies: "Gestisci tutte le aziende registrate",
    companyName: "Nome Azienda",
    totalDeliveries: "Consegne Totali",
    activeCouriers: "Corrieri Attivi",
    status: "Stato",
    created: "Creato",
    actions: "Azioni",
    active: "Attivo",
    disabled: "Disabilitato",
    enable: "Abilita",
    disable: "Disabilita",
    edit: "Modifica",
    delete: "Cancella",
    yourDeliveries: "Le Tue Consegne",
    manageAssignedOrders: "Gestisci i tuoi ordini assegnati",
    activeDeliveries: "Consegne Attive",
    assigned: "Assegnato",
    inProgress: "In Corso",
    delivered: "Consegnato",
    pending: "In Attesa",
    markAsDelivered: "Segna come Consegnato",
    noActiveDeliveries: "Nessuna consegna attiva al momento",
    createdAt: "Creato il"
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

// Super Admin Dashboard
function SuperAdminDashboard() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logout, t } = useAuth();
  const { toast } = useToast();

  const fetchCompanies = async () => {
    try {
      const response = await axios.get(`${API}/companies`);
      setCompanies(response.data);
    } catch (error) {
      toast({
        title: t.error,
        description: "Failed to fetch companies",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 to-indigo-50">
      <div className="container mx-auto p-4 sm:p-6 max-w-7xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 sm:mb-8 space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-violet-600 rounded-full flex items-center justify-center flex-shrink-0">
              <Shield className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 truncate">{t.superAdminTitle}</h1>
              <p className="text-sm sm:text-base text-gray-600">{t.systemManagement}</p>
            </div>
          </div>
          <Button onClick={logout} variant="outline" size="sm" className="w-full sm:w-auto">
            <LogOut className="w-4 h-4 mr-2" />
            {t.logout}
          </Button>
        </div>

        <Card className="bg-white shadow-sm border-0">
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="text-lg sm:text-xl">{t.companiesManagement}</CardTitle>
            <CardDescription className="text-sm">{t.manageAllCompanies}</CardDescription>
          </CardHeader>
          <CardContent className="p-4 sm:p-6">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600 mx-auto"></div>
                <p className="text-gray-500 mt-2 text-sm">{t.loading}</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-xs sm:text-sm">{t.companyName}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.totalDeliveries}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.activeCouriers}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.status}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.created}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {companies.map((company) => (
                      <TableRow key={company.id}>
                        <TableCell className="font-medium text-xs sm:text-sm">{company.name}</TableCell>
                        <TableCell className="text-xs sm:text-sm">{company.total_deliveries}</TableCell>
                        <TableCell className="text-xs sm:text-sm">{company.active_couriers}</TableCell>
                        <TableCell>
                          <Badge variant={company.is_active ? 'default' : 'destructive'} className="text-xs">
                            {company.is_active ? t.active : t.disabled}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs sm:text-sm">{new Date(company.created_at).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Courier Dashboard
function CourierDashboard() {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logout, t } = useAuth();
  const { toast } = useToast();

  const fetchDeliveries = async () => {
    try {
      const response = await axios.get(`${API}/courier/deliveries`);
      setDeliveries(response.data);
    } catch (error) {
      toast({
        title: t.error,
        description: "Failed to fetch deliveries",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const markAsDelivered = async (orderId) => {
    try {
      await axios.patch(`${API}/courier/deliveries/mark-delivered`, {
        order_id: orderId
      });
      
      toast({
        title: t.success,
        description: "Delivery marked as completed and customer notified!",
      });
      
      fetchDeliveries();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || "Failed to mark delivery",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchDeliveries();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-blue-50">
      <div className="container mx-auto p-4 sm:p-6 max-w-7xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 sm:mb-8 space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-emerald-600 rounded-full flex items-center justify-center flex-shrink-0">
              <Truck className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 truncate">{t.courierDashboard}</h1>
              <p className="text-sm sm:text-base text-gray-600 truncate">{t.welcomeBack}, {user.username}</p>
            </div>
          </div>
          <Button onClick={logout} variant="outline" size="sm" className="w-full sm:w-auto">
            <LogOut className="w-4 h-4 mr-2" />
            {t.logout}
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.activeDeliveries}</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">{deliveries.length}</p>
                </div>
                <Package className="w-6 h-6 sm:w-8 sm:h-8 text-emerald-600 flex-shrink-0" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.inProgress}</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">
                    {deliveries.filter(d => d.status === 'in_progress').length}
                  </p>
                </div>
                <Clock className="w-6 h-6 sm:w-8 sm:h-8 text-blue-600 flex-shrink-0" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0 sm:col-span-2 lg:col-span-1">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.assigned}</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">
                    {deliveries.filter(d => d.status === 'assigned').length}
                  </p>
                </div>
                <CheckCircle className="w-6 h-6 sm:w-8 sm:h-8 text-amber-600 flex-shrink-0" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="bg-white shadow-sm border-0">
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="text-lg sm:text-xl font-semibold">{t.yourDeliveries}</CardTitle>
            <CardDescription className="text-sm">{t.manageAssignedOrders}</CardDescription>
          </CardHeader>
          <CardContent className="p-4 sm:p-6">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto"></div>
                <p className="text-gray-500 mt-2 text-sm">{t.loading}</p>
              </div>
            ) : deliveries.length === 0 ? (
              <div className="text-center py-8">
                <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 text-sm">{t.noActiveDeliveries}</p>
              </div>
            ) : (
              <div className="space-y-4">
                {deliveries.map((delivery) => (
                  <div key={delivery.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex flex-col sm:flex-row justify-between items-start mb-3 space-y-2 sm:space-y-0">
                      <div className="flex-1 min-w-0 pr-0 sm:pr-4">
                        <h3 className="font-semibold text-gray-900 text-sm sm:text-base truncate">{delivery.customer_name}</h3>
                        <p className="text-gray-600 text-xs sm:text-sm break-words">{delivery.delivery_address}</p>
                        <p className="text-gray-500 text-xs sm:text-sm">📞 {delivery.phone_number}</p>
                        {delivery.reference_number && (
                          <p className="text-gray-500 text-xs sm:text-sm">📋 Rif: {delivery.reference_number}</p>
                        )}
                      </div>
                      <Badge variant={delivery.status === 'assigned' ? 'default' : 'secondary'} className="shrink-0 text-xs">
                        {delivery.status === 'assigned' ? t.assigned.toUpperCase() : t.inProgress.toUpperCase()}
                      </Badge>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
                      <p className="text-xs text-gray-500">
                        {t.createdAt}: {new Date(delivery.created_at).toLocaleDateString()}
                      </p>
                      <Button 
                        onClick={() => markAsDelivered(delivery.id)}
                        size="sm"
                        className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white text-xs sm:text-sm"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        {t.markAsDelivered}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Company Admin Dashboard Placeholder
function CompanyAdminDashboard() {
  const { user, company, logout, t } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
      <div className="container mx-auto p-4 sm:p-6 max-w-7xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 sm:mb-8 space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-orange-600 rounded-full flex items-center justify-center flex-shrink-0">
              <Building2 className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 truncate">{t.companyDashboard}</h1>
              <p className="text-sm sm:text-base text-gray-600 truncate">{company?.name} • {user.username}</p>
            </div>
          </div>
          <Button onClick={logout} variant="outline" size="sm" className="w-full sm:w-auto">
            <LogOut className="w-4 h-4 mr-2" />
            {t.logout}
          </Button>
        </div>

        <Card className="bg-white shadow-sm border-0">
          <CardHeader>
            <CardTitle>Dashboard Aziendale</CardTitle>
            <CardDescription>Gestione completa per amministratori azienda - Funzionalità in sviluppo</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <Building2 className="w-16 h-16 text-orange-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Dashboard Azienda Funzionante</h2>
              <p className="text-gray-600 mb-4">
                Login completato con successo per: <Badge>{company?.name}</Badge>
              </p>
              <p className="text-sm text-gray-500">
                Funzionalità complete in arrivo: gestione corrieri, ordini, filtri e export
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Dashboard Router
function DashboardRouter() {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  switch (user.role) {
    case 'super_admin':
      return <SuperAdminDashboard />;
    case 'company_admin':
      return <CompanyAdminDashboard />;
    case 'courier':
      return <CourierDashboard />;
    default:
      return <Navigate to="/login" replace />;
  }
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
                <DashboardRouter />
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