import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Import translations
import { getTranslation } from './translations';

// Import UI components
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Label } from './components/ui/label';
import { Separator } from './components/ui/separator';
import { useToast } from './hooks/use-toast';
import { Toaster } from './components/ui/toaster';
import { Truck, Package, Users, Building2, CheckCircle, Clock, User, LogOut, Shield, UserPlus, Plus, Globe } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState(localStorage.getItem('language') || 'en');
  const [t, setT] = useState(getTranslation(language));

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    const companyData = localStorage.getItem('company');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
      if (companyData) {
        setCompany(JSON.parse(companyData));
      }
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    setT(getTranslation(language));
    localStorage.setItem('language', language);
  }, [language]);

  const login = (token, userData, companyData = null) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    if (companyData) {
      localStorage.setItem('company', JSON.stringify(companyData));
      setCompany(companyData);
    }
    setUser(userData);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    // Force navigation after login
    window.location.href = '/';
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('company');
    setUser(null);
    setCompany(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const changeLanguage = (newLanguage) => {
    setLanguage(newLanguage);
  };

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
        description: t.failedToFetchData,
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
        description: t.deliveryMarkedCompleted,
      });
      
      // Remove from list or refresh
      fetchDeliveries();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToMarkDelivery,
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchDeliveries();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-blue-50">
      <div className="container mx-auto p-4 sm:p-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 sm:mb-8 space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-emerald-600 rounded-full flex items-center justify-center">
              <Truck className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">{t.courierDashboard}</h1>
              <p className="text-sm sm:text-base text-gray-600">{t.welcomeBack}, {user.username}</p>
            </div>
          </div>
          <Button onClick={logout} variant="outline" size="sm">
            <LogOut className="w-4 h-4 mr-2" />
            {t.logout}
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm font-medium text-gray-600">{t.activeDeliveries}</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">{deliveries.length}</p>
                </div>
                <Package className="w-6 h-6 sm:w-8 sm:h-8 text-emerald-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm font-medium text-gray-600">{t.inProgress}</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">
                    {deliveries.filter(d => d.status === 'in_progress').length}
                  </p>
                </div>
                <Clock className="w-6 h-6 sm:w-8 sm:h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0 sm:col-span-2 lg:col-span-1">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm font-medium text-gray-600">{t.assigned}</p>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900">
                    {deliveries.filter(d => d.status === 'assigned').length}
                  </p>
                </div>
                <CheckCircle className="w-6 h-6 sm:w-8 sm:h-8 text-amber-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Deliveries List */}
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
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 truncate">{delivery.customer_name}</h3>
                        <p className="text-gray-600 text-sm break-words">{delivery.delivery_address}</p>
                        <p className="text-gray-500 text-sm">📞 {delivery.phone_number}</p>
                      </div>
                      <Badge variant={delivery.status === 'assigned' ? 'default' : 'secondary'} className="shrink-0">
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
                        className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white"
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

// Super Admin Dashboard
function SuperAdminDashboard() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newCompany, setNewCompany] = useState({ name: '', admin_username: '', admin_password: '' });
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const { user, logout, t } = useAuth();
  const { toast } = useToast();

  const fetchCompanies = async () => {
    try {
      const response = await axios.get(`${API}/companies`);
      setCompanies(response.data);
    } catch (error) {
      toast({
        title: t.error,
        description: t.failedToFetchData,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createCompany = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/companies`, newCompany);
      toast({
        title: t.success,
        description: t.companyCreatedSuccessfully,
      });
      setNewCompany({ name: '', admin_username: '', admin_password: '' });
      setShowCreateDialog(false);
      fetchCompanies();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToCreateCompany,
        variant: "destructive",
      });
    }
  };

  const toggleCompanyStatus = async (companyId) => {
    try {
      await axios.patch(`${API}/companies/${companyId}/toggle`);
      toast({
        title: t.success,
        description: t.statusUpdated,
      });
      fetchCompanies();
    } catch (error) {
      toast({
        title: t.error,
        description: "Failed to update company status",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 to-indigo-50">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-violet-600 rounded-full flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{t.superAdminTitle}</h1>
              <p className="text-gray-600">{t.systemManagement}</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="bg-violet-600 hover:bg-violet-700">
                  <Plus className="w-4 h-4 mr-2" />
                  {t.addCompany}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{t.createNewCompany}</DialogTitle>
                  <DialogDescription>{t.addNewCompanyDescription}</DialogDescription>
                </DialogHeader>
                <form onSubmit={createCompany} className="space-y-4">
                  <div>
                    <Label htmlFor="companyName">{t.companyName}</Label>
                    <Input
                      id="companyName"
                      value={newCompany.name}
                      onChange={(e) => setNewCompany({ ...newCompany, name: e.target.value })}
                      placeholder={t.enterCompanyName}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="adminUsername">{t.adminUsername}</Label>
                    <Input
                      id="adminUsername"
                      value={newCompany.admin_username}
                      onChange={(e) => setNewCompany({ ...newCompany, admin_username: e.target.value })}
                      placeholder={t.enterAdminUsername}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="adminPassword">{t.adminPassword}</Label>
                    <Input
                      id="adminPassword"
                      type="password"
                      value={newCompany.admin_password}
                      onChange={(e) => setNewCompany({ ...newCompany, admin_password: e.target.value })}
                      placeholder={t.enterAdminPassword}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full">{t.createCompany}</Button>
                </form>
              </DialogContent>
            </Dialog>
            <Button onClick={logout} variant="outline" size="sm">
              <LogOut className="w-4 h-4 mr-2" />
              {t.logout}
            </Button>
          </div>
        </div>

        {/* Companies Table */}
        <Card className="bg-white shadow-sm border-0">
          <CardHeader>
            <CardTitle>{t.companiesManagement}</CardTitle>
            <CardDescription>{t.manageAllCompanies}</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600 mx-auto"></div>
                <p className="text-gray-500 mt-2">{t.loading}</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t.companyName}</TableHead>
                    <TableHead>{t.totalDeliveries}</TableHead>
                    <TableHead>{t.activeCouriers}</TableHead>
                    <TableHead>{t.status}</TableHead>
                    <TableHead>{t.created}</TableHead>
                    <TableHead>{t.actions}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {companies.map((company) => (
                    <TableRow key={company.id}>
                      <TableCell className="font-medium">{company.name}</TableCell>
                      <TableCell>{company.total_deliveries}</TableCell>
                      <TableCell>{company.active_couriers}</TableCell>
                      <TableCell>
                        <Badge variant={company.is_active ? 'default' : 'destructive'}>
                          {company.is_active ? t.active : t.disabled}
                        </Badge>
                      </TableCell>
                      <TableCell>{new Date(company.created_at).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <Button
                          onClick={() => toggleCompanyStatus(company.id)}
                          variant={company.is_active ? 'destructive' : 'default'}
                          size="sm"
                        >
                          {company.is_active ? t.disable : t.enable}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Company Admin Dashboard
function CompanyAdminDashboard() {
  const [couriers, setCouriers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateCourier, setShowCreateCourier] = useState(false);
  const [showCreateOrder, setShowCreateOrder] = useState(false);
  const [newCourier, setNewCourier] = useState({ username: '', password: '' });
  const [newOrder, setNewOrder] = useState({ customer_name: '', delivery_address: '', phone_number: '' });
  const { user, company, logout } = useAuth();
  const { toast } = useToast();

  const fetchCouriers = async () => {
    try {
      const response = await axios.get(`${API}/couriers`);
      setCouriers(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch couriers",
        variant: "destructive",
      });
    }
  };

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch orders",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createCourier = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/couriers`, newCourier);
      toast({
        title: "Success",
        description: "Courier created successfully",
      });
      setNewCourier({ username: '', password: '' });
      setShowCreateCourier(false);
      fetchCouriers();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create courier",
        variant: "destructive",
      });
    }
  };

  const createOrder = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/orders`, newOrder);
      toast({
        title: "Success",
        description: "Order created successfully",
      });
      setNewOrder({ customer_name: '', delivery_address: '', phone_number: '' });
      setShowCreateOrder(false);
      fetchOrders();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create order",
        variant: "destructive",
      });
    }
  };

  const assignOrder = async (orderId, courierId) => {
    try {
      await axios.patch(`${API}/orders/assign`, {
        order_id: orderId,
        courier_id: courierId
      });
      toast({
        title: "Success",
        description: "Order assigned successfully",
      });
      fetchOrders();
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to assign order",
        variant: "destructive",
      });
    }
  };

  const toggleCourierStatus = async (courierId) => {
    try {
      await axios.patch(`${API}/couriers/${courierId}/toggle`);
      toast({
        title: "Success",
        description: "Courier status updated",
      });
      fetchCouriers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update courier status",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchCouriers();
    fetchOrders();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Company Admin</h1>
              <p className="text-gray-600">{company?.name || 'Company Dashboard'}</p>
            </div>
          </div>
          <Button onClick={logout} variant="outline" size="sm">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Orders</p>
                  <p className="text-3xl font-bold text-gray-900">{orders.length}</p>
                </div>
                <Package className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Couriers</p>
                  <p className="text-3xl font-bold text-gray-900">{couriers.filter(c => c.is_active).length}</p>
                </div>
                <Users className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Pending Orders</p>
                  <p className="text-3xl font-bold text-gray-900">{orders.filter(o => o.status === 'pending').length}</p>
                </div>
                <Clock className="w-8 h-8 text-amber-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Delivered</p>
                  <p className="text-3xl font-bold text-gray-900">{orders.filter(o => o.status === 'delivered').length}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-emerald-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Couriers Management */}
          <Card className="bg-white shadow-sm border-0">
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="text-xl font-semibold">Couriers</CardTitle>
                  <CardDescription>Manage your delivery couriers</CardDescription>
                </div>
                <Dialog open={showCreateCourier} onOpenChange={setShowCreateCourier}>
                  <DialogTrigger asChild>
                    <Button className="bg-blue-600 hover:bg-blue-700">
                      <UserPlus className="w-4 h-4 mr-2" />
                      Add Courier
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New Courier</DialogTitle>
                      <DialogDescription>Add a new courier to your team</DialogDescription>
                    </DialogHeader>
                    <form onSubmit={createCourier} className="space-y-4">
                      <div>
                        <Label htmlFor="courierUsername">Username</Label>
                        <Input
                          id="courierUsername"
                          value={newCourier.username}
                          onChange={(e) => setNewCourier({ ...newCourier, username: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="courierPassword">Password</Label>
                        <Input
                          id="courierPassword"
                          type="password"
                          value={newCourier.password}
                          onChange={(e) => setNewCourier({ ...newCourier, password: e.target.value })}
                          required
                        />
                      </div>
                      <Button type="submit" className="w-full">Create Courier</Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                </div>
              ) : couriers.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No couriers yet</p>
              ) : (
                <div className="space-y-3">
                  {couriers.map((courier) => (
                    <div key={courier.id} className="flex justify-between items-center p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{courier.username}</p>
                        <p className="text-sm text-gray-500">
                          Created: {new Date(courier.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={courier.is_active ? 'default' : 'destructive'}>
                          {courier.is_active ? 'Active' : 'Blocked'}
                        </Badge>
                        <Button
                          onClick={() => toggleCourierStatus(courier.id)}
                          variant={courier.is_active ? 'destructive' : 'default'}
                          size="sm"
                        >
                          {courier.is_active ? 'Block' : 'Activate'}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Orders Management */}
          <Card className="bg-white shadow-sm border-0">
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="text-xl font-semibold">Orders</CardTitle>
                  <CardDescription>Manage delivery orders</CardDescription>
                </div>
                <Dialog open={showCreateOrder} onOpenChange={setShowCreateOrder}>
                  <DialogTrigger asChild>
                    <Button className="bg-green-600 hover:bg-green-700">
                      <Plus className="w-4 h-4 mr-2" />
                      Create Order
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New Order</DialogTitle>
                      <DialogDescription>Create a new delivery order</DialogDescription>
                    </DialogHeader>
                    <form onSubmit={createOrder} className="space-y-4">
                      <div>
                        <Label htmlFor="customerName">Customer Name</Label>
                        <Input
                          id="customerName"
                          value={newOrder.customer_name}
                          onChange={(e) => setNewOrder({ ...newOrder, customer_name: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="deliveryAddress">Delivery Address</Label>
                        <Input
                          id="deliveryAddress"
                          value={newOrder.delivery_address}
                          onChange={(e) => setNewOrder({ ...newOrder, delivery_address: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="phoneNumber">Phone Number</Label>
                        <Input
                          id="phoneNumber"
                          value={newOrder.phone_number}
                          onChange={(e) => setNewOrder({ ...newOrder, phone_number: e.target.value })}
                          required
                        />
                      </div>
                      <Button type="submit" className="w-full">Create Order</Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto"></div>
                </div>
              ) : orders.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No orders yet</p>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {orders.map((order) => (
                    <div key={order.id} className="border rounded-lg p-3">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1">
                          <p className="font-medium">{order.customer_name}</p>
                          <p className="text-sm text-gray-600">{order.delivery_address}</p>
                          <p className="text-sm text-gray-500">📞 {order.phone_number}</p>
                        </div>
                        <Badge variant={
                          order.status === 'delivered' ? 'default' :
                          order.status === 'assigned' || order.status === 'in_progress' ? 'secondary' :
                          'outline'
                        }>
                          {order.status.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </div>
                      
                      {order.status === 'pending' && couriers.filter(c => c.is_active).length > 0 && (
                        <div className="mt-2">
                          <Select onValueChange={(courierId) => assignOrder(order.id, courierId)}>
                            <SelectTrigger className="w-full">
                              <SelectValue placeholder="Assign to courier" />
                            </SelectTrigger>
                            <SelectContent>
                              {couriers.filter(c => c.is_active).map((courier) => (
                                <SelectItem key={courier.id} value={courier.id}>
                                  {courier.username}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      )}
                      
                      <p className="text-xs text-gray-500 mt-2">
                        Created: {new Date(order.created_at).toLocaleDateString()}
                        {order.delivered_at && (
                          <span> • Delivered: {new Date(order.delivered_at).toLocaleDateString()}</span>
                        )}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

// Protected Route Component
function ProtectedRoute({ children, allowedRoles }) {
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

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
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
            <Route path="/unauthorized" element={
              <div className="min-h-screen flex items-center justify-center">
                <Card>
                  <CardContent className="p-6 text-center">
                    <h2 className="text-xl font-bold mb-2">Access Denied</h2>
                    <p>You don't have permission to access this page.</p>
                  </CardContent>
                </Card>
              </div>
            } />
          </Routes>
          <Toaster />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;