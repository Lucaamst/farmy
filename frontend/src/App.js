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
import { Truck, Package, Users, Building2, CheckCircle, Clock, User, LogOut, Shield, UserPlus, Plus, Globe, Key, Smartphone, MessageSquare, Lock } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState(localStorage.getItem('language') || 'it');
  const [securityRequired, setSecurityRequired] = useState(false);
  const [securitySetupRequired, setSecuritySetupRequired] = useState(false);
  const [t, setT] = useState(getTranslation(language));

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
        
        // User data loaded successfully
      } catch (e) {
        console.error('Error parsing stored data:', e);
        localStorage.clear();
      }
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    setT(getTranslation(language));
    localStorage.setItem('language', language);
  }, [language]);

  const login = async (token, userData, companyData = null) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    if (companyData) {
      localStorage.setItem('company', JSON.stringify(companyData));
      setCompany(companyData);
    }
    setUser(userData);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    // Login successful
    
    // Force navigation after login
    window.location.href = '/';
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('company');
    setUser(null);
    setCompany(null);
    setSecurityRequired(false);
    setSecuritySetupRequired(false);
    delete axios.defaults.headers.common['Authorization'];
  };

  const changeLanguage = (newLanguage) => {
    setLanguage(newLanguage);
  };

  const onSecuritySetupComplete = () => {
    setSecuritySetupRequired(false);
    setSecurityRequired(false);
  };

  const onSecurityVerificationComplete = () => {
    setSecurityRequired(false);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      company, 
      login, 
      logout, 
      loading, 
      language, 
      changeLanguage, 
      t,
      securityRequired,
      securitySetupRequired,
      onSecuritySetupComplete,
      onSecurityVerificationComplete
    }}>
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
      <div className="container mx-auto p-4 sm:p-6 max-w-7xl">
        {/* Header */}
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

        {/* Stats */}
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
                      <div className="flex-1 min-w-0 pr-0 sm:pr-4">
                        <h3 className="font-semibold text-gray-900 text-sm sm:text-base truncate">{delivery.customer_name}</h3>
                        <p className="text-gray-600 text-xs sm:text-sm break-words">{delivery.delivery_address}</p>
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

// Super Admin Dashboard (with all new features)
function SuperAdminDashboard() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newCompany, setNewCompany] = useState({ name: '', admin_username: '', admin_password: '' });
  const [editingCompany, setEditingCompany] = useState(null);
  const [deletingCompany, setDeletingCompany] = useState(null);
  const [resettingPasswordCompany, setResettingPasswordCompany] = useState(null);
  const [deletePassword, setDeletePassword] = useState('');
  const [resetPasswordData, setResetPasswordData] = useState({ admin_password: '', new_password: '' });
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showResetPasswordDialog, setShowResetPasswordDialog] = useState(false);
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

  const updateCompany = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`${API}/companies/${editingCompany.id}`, {
        name: editingCompany.name
      });
      toast({
        title: t.success,
        description: t.companyUpdatedSuccessfully,
      });
      setEditingCompany(null);
      setShowEditDialog(false);
      fetchCompanies();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToUpdateCompany,
        variant: "destructive",
      });
    }
  };

  const deleteCompany = async (e) => {
    e.preventDefault();
    try {
      await axios.delete(`${API}/companies/${deletingCompany.id}`, {
        data: { password: deletePassword }
      });
      toast({
        title: t.success,
        description: t.companyDeletedSuccessfully,
      });
      setDeletingCompany(null);
      setDeletePassword('');
      setShowDeleteDialog(false);
      fetchCompanies();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToDeleteCompany,
        variant: "destructive",
      });
    }
  };

  const resetCompanyPassword = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`${API}/companies/${resettingPasswordCompany.id}/reset-password`, {
        company_id: resettingPasswordCompany.id,
        new_password: resetPasswordData.new_password,
        admin_password: resetPasswordData.admin_password
      });
      toast({
        title: t.success,
        description: t.passwordResetSuccessfully,
      });
      setResettingPasswordCompany(null);
      setResetPasswordData({ admin_password: '', new_password: '' });
      setShowResetPasswordDialog(false);
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToResetPassword,
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

  const handleEditClick = (company) => {
    setEditingCompany({...company});
    setShowEditDialog(true);
  };

  const handleDeleteClick = (company) => {
    setDeletingCompany(company);
    setDeletePassword('');
    setShowDeleteDialog(true);
  };

  const handleResetPasswordClick = (company) => {
    setResettingPasswordCompany(company);
    setResetPasswordData({ admin_password: '', new_password: '' });
    setShowResetPasswordDialog(true);
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 to-indigo-50">
      <div className="container mx-auto p-4 sm:p-6 max-w-7xl">
        {/* Header */}
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
          <div className="flex items-center space-x-2 sm:space-x-4 w-full sm:w-auto">
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="bg-violet-600 hover:bg-violet-700 flex-1 sm:flex-none text-sm">
                  <Plus className="w-4 h-4 mr-2" />
                  {t.addCompany}
                </Button>
              </DialogTrigger>
              <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
                <DialogHeader>
                  <DialogTitle className="text-lg">{t.createNewCompany}</DialogTitle>
                  <DialogDescription className="text-sm">{t.addNewCompanyDescription}</DialogDescription>
                </DialogHeader>
                <form onSubmit={createCompany} className="space-y-4">
                  <div>
                    <Label htmlFor="companyName" className="text-sm">{t.companyName}</Label>
                    <Input
                      id="companyName"
                      value={newCompany.name}
                      onChange={(e) => setNewCompany({ ...newCompany, name: e.target.value })}
                      placeholder={t.enterCompanyName}
                      required
                      className="text-sm"
                    />
                  </div>
                  <div>
                    <Label htmlFor="adminUsername" className="text-sm">{t.adminUsername}</Label>
                    <Input
                      id="adminUsername"
                      value={newCompany.admin_username}
                      onChange={(e) => setNewCompany({ ...newCompany, admin_username: e.target.value })}
                      placeholder={t.enterAdminUsername}
                      required
                      className="text-sm"
                    />
                  </div>
                  <div>
                    <Label htmlFor="adminPassword" className="text-sm">{t.adminPassword}</Label>
                    <Input
                      id="adminPassword"
                      type="password"
                      value={newCompany.admin_password}
                      onChange={(e) => setNewCompany({ ...newCompany, admin_password: e.target.value })}
                      placeholder={t.enterAdminPassword}
                      required
                      className="text-sm"
                    />
                  </div>
                  <Button type="submit" className="w-full text-sm">{t.createCompany}</Button>
                </form>
              </DialogContent>
            </Dialog>
            <Button onClick={logout} variant="outline" size="sm" className="flex-1 sm:flex-none text-sm">
              <LogOut className="w-4 h-4 mr-2" />
              {t.logout}
            </Button>
          </div>
        </div>

        {/* Companies Table */}
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
                      <TableHead className="text-xs sm:text-sm">{t.actions}</TableHead>
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
                        <TableCell>
                          <div className="flex flex-col sm:flex-row space-y-1 sm:space-y-0 sm:space-x-1">
                            <Button
                              onClick={() => handleEditClick(company)}
                              variant="outline"
                              size="sm"
                              className="text-xs"
                            >
                              {t.edit}
                            </Button>
                            <Button
                              onClick={() => handleResetPasswordClick(company)}
                              variant="outline"
                              size="sm"
                              className="text-xs"
                            >
                              Reset Password
                            </Button>
                            <Button
                              onClick={() => toggleCompanyStatus(company.id)}
                              variant={company.is_active ? 'destructive' : 'default'}
                              size="sm"
                              className="text-xs"
                            >
                              {company.is_active ? t.disable : t.enable}
                            </Button>
                            <Button
                              onClick={() => handleDeleteClick(company)}
                              variant="destructive"
                              size="sm"
                              className="text-xs"
                            >
                              {t.delete}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* All dialogs for company management */}
        {/* Edit Company Dialog */}
        <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.editCompany}</DialogTitle>
              <DialogDescription className="text-sm">{t.editCompanyDescription}</DialogDescription>
            </DialogHeader>
            {editingCompany && (
              <form onSubmit={updateCompany} className="space-y-4">
                <div>
                  <Label htmlFor="editCompanyName" className="text-sm">{t.companyName}</Label>
                  <Input
                    id="editCompanyName"
                    value={editingCompany.name}
                    onChange={(e) => setEditingCompany({ ...editingCompany, name: e.target.value })}
                    required
                    className="text-sm"
                  />
                </div>
                <div className="flex space-x-2">
                  <Button type="submit" className="flex-1 text-sm">{t.updateCompany}</Button>
                  <Button type="button" variant="outline" onClick={() => setShowEditDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* Reset Password Dialog */}
        <Dialog open={showResetPasswordDialog} onOpenChange={setShowResetPasswordDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.resetCompanyPassword}</DialogTitle>
              <DialogDescription className="text-sm">{t.resetPasswordDescription}</DialogDescription>
            </DialogHeader>
            {resettingPasswordCompany && (
              <form onSubmit={resetCompanyPassword} className="space-y-4">
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    Reset password per: <strong>{resettingPasswordCompany.name}</strong>
                  </p>
                </div>
                <div>
                  <Label htmlFor="adminPasswordForReset" className="text-sm">{t.confirmPassword} (Super Admin)</Label>
                  <Input
                    id="adminPasswordForReset"
                    type="password"
                    value={resetPasswordData.admin_password}
                    onChange={(e) => setResetPasswordData({ ...resetPasswordData, admin_password: e.target.value })}
                    placeholder={t.enterPasswordToConfirm}
                    required
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="newPasswordForAdmin" className="text-sm">{t.newPasswordForAdmin}</Label>
                  <Input
                    id="newPasswordForAdmin"
                    type="password"
                    value={resetPasswordData.new_password}
                    onChange={(e) => setResetPasswordData({ ...resetPasswordData, new_password: e.target.value })}
                    placeholder={t.enterNewPasswordForAdmin}
                    required
                    className="text-sm"
                  />
                </div>
                <div className="flex space-x-2">
                  <Button type="submit" className="flex-1 text-sm">
                    Reimposta Password
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowResetPasswordDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* Delete Company Dialog */}
        <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.deleteCompany}</DialogTitle>
              <DialogDescription className="text-sm">{t.deleteCompanyDescription}</DialogDescription>
            </DialogHeader>
            {deletingCompany && (
              <form onSubmit={deleteCompany} className="space-y-4">
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800">
                    Stai per cancellare: <strong>{deletingCompany.name}</strong>
                  </p>
                  <p className="text-xs text-red-600 mt-1">
                    Questa azione cancellerà anche tutti gli ordini e corrieri associati.
                  </p>
                </div>
                <div>
                  <Label htmlFor="deletePassword" className="text-sm">{t.confirmPassword}</Label>
                  <Input
                    id="deletePassword"
                    type="password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    placeholder={t.enterPasswordToConfirm}
                    required
                    className="text-sm"
                  />
                </div>
                <div className="flex space-x-2">
                  <Button type="submit" variant="destructive" className="flex-1 text-sm">
                    Cancella Definitivamente
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowDeleteDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}

// PWA Registration and Setup
function SecuritySetup({ user, onSecurityComplete }) {
  const [currentStep, setCurrentStep] = useState('choose');
  const [securityStatus, setSecurityStatus] = useState({
    face_id_enabled: false,
    pin_enabled: false,
    sms_enabled: false,
    webauthn_credentials: 0
  });
  const [pin, setPin] = useState('');
  const [confirmPin, setConfirmPin] = useState('');
  const [smsCode, setSmsCode] = useState('');
  const [phoneNumber, setPhoneNumber] = useState(user.phone_number || '');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const { t } = useAuth();

  useEffect(() => {
    fetchSecurityStatus();
  }, []);

  const fetchSecurityStatus = async () => {
    try {
      const response = await axios.get(`${API}/security/status`);
      setSecurityStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch security status', error);
    }
  };

  const setupPin = async () => {
    if (pin.length !== 6 || !pin.match(/^\d+$/)) {
      toast({
        title: t.error,
        description: t.pin6Digits,
        variant: "destructive",
      });
      return;
    }

    if (pin !== confirmPin) {
      toast({
        title: t.error,
        description: t.pinMismatch,
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/security/setup-pin`, { pin });
      toast({
        title: t.success,
        description: t.pinEnabled,
      });
      setSecurityStatus(prev => ({ ...prev, pin_enabled: true }));
      setCurrentStep('choose');
      setPin('');
      setConfirmPin('');
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || "Failed to setup PIN",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const setupBiometric = async () => {
    if (!window.PublicKeyCredential) {
      toast({
        title: t.error,
        description: t.biometricNotSupported,
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      // Import WebAuthn library
      const { startRegistration } = await import('@simplewebauthn/browser');
      
      // Get registration options from backend
      const optionsResponse = await axios.post(`${API}/security/webauthn/generate-registration-options`);
      
      // Start WebAuthn registration
      const credential = await startRegistration(optionsResponse.data);
      
      // Verify registration with backend
      await axios.post(`${API}/security/webauthn/verify-registration`, { credential });
      
      toast({
        title: t.success,
        description: t.biometricEnabled,
      });
      setSecurityStatus(prev => ({ ...prev, face_id_enabled: true, webauthn_credentials: prev.webauthn_credentials + 1 }));
      setCurrentStep('choose');
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || "Failed to setup biometric authentication",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const sendSmsCode = async () => {
    if (!phoneNumber) {
      toast({
        title: t.error,
        description: "Phone number is required",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/security/send-sms-code`, { phone_number: phoneNumber });
      toast({
        title: t.success,
        description: t.smsCodeSent,
      });
      setCurrentStep('verify-sms');
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || "Failed to send SMS code",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const verifySmsCode = async () => {
    if (smsCode.length !== 6) {
      toast({
        title: t.error,
        description: "SMS code must be 6 digits",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/security/verify-sms-code`, { 
        phone_number: phoneNumber, 
        code: smsCode 
      });
      toast({
        title: t.success,
        description: "SMS verification enabled",
      });
      setSecurityStatus(prev => ({ ...prev, sms_enabled: true }));
      setCurrentStep('choose');
      setSmsCode('');
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || "Failed to verify SMS code",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const completeSetup = () => {
    if (securityStatus.pin_enabled || securityStatus.face_id_enabled || securityStatus.sms_enabled) {
      toast({
        title: t.success,
        description: t.securityUpgradeComplete,
      });
      onSecurityComplete();
    } else {
      toast({
        title: t.error,
        description: t.securitySetupRequired,
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-white shadow-lg border-0">
        <CardHeader className="text-center pb-4">
          <div className="w-16 h-16 bg-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-xl text-gray-900">{t.multiLevelSecurity}</CardTitle>
          <CardDescription className="text-sm text-gray-600">
            {currentStep === 'choose' ? t.chooseSecurity : t.setupSecurity}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {currentStep === 'choose' && (
            <div className="space-y-4">
              {/* Security Status */}
              <div className="space-y-2">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Key className="w-4 h-4 text-gray-600" />
                    <span className="text-sm">{t.pin}</span>
                  </div>
                  <Badge variant={securityStatus.pin_enabled ? 'default' : 'secondary'}>
                    {securityStatus.pin_enabled ? t.pinEnabled : 'Disabilitato'}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Smartphone className="w-4 h-4 text-gray-600" />
                    <span className="text-sm">{t.biometricAuth}</span>
                  </div>
                  <Badge variant={securityStatus.face_id_enabled ? 'default' : 'secondary'}>
                    {securityStatus.face_id_enabled ? t.biometricEnabled : t.biometricDisabled}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-2">
                    <MessageSquare className="w-4 h-4 text-gray-600" />
                    <span className="text-sm">{t.smsVerification}</span>
                  </div>
                  <Badge variant={securityStatus.sms_enabled ? 'default' : 'secondary'}>
                    {securityStatus.sms_enabled ? 'Attivo' : 'Disattivo'}
                  </Badge>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2">
                {!securityStatus.pin_enabled && (
                  <Button 
                    onClick={() => setCurrentStep('setup-pin')} 
                    className="w-full bg-orange-600 hover:bg-orange-700"
                    size="sm"
                  >
                    <Key className="w-4 h-4 mr-2" />
                    {t.setupPin}
                  </Button>
                )}
                
                {!securityStatus.face_id_enabled && (
                  <Button 
                    onClick={setupBiometric} 
                    variant="outline" 
                    className="w-full"
                    size="sm"
                    disabled={loading}
                  >
                    <Smartphone className="w-4 h-4 mr-2" />
                    {t.setupBiometric}
                  </Button>
                )}
                
                {!securityStatus.sms_enabled && (
                  <Button 
                    onClick={() => setCurrentStep('setup-sms')} 
                    variant="outline" 
                    className="w-full"
                    size="sm"
                  >
                    <MessageSquare className="w-4 h-4 mr-2" />
                    {t.smsVerification}
                  </Button>
                )}
              </div>

              {/* Complete Setup */}
              <Button 
                onClick={completeSetup} 
                className="w-full mt-6"
                variant={securityStatus.pin_enabled || securityStatus.face_id_enabled || securityStatus.sms_enabled ? 'default' : 'outline'}
              >
                {t.securityComplete}
              </Button>
            </div>
          )}

          {currentStep === 'setup-pin' && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="pin" className="text-sm">{t.enterPin}</Label>
                <Input
                  id="pin"
                  type="password"
                  maxLength={6}
                  value={pin}
                  onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="text-center text-lg tracking-widest"
                />
              </div>
              <div>
                <Label htmlFor="confirmPin" className="text-sm">{t.confirmPin}</Label>
                <Input
                  id="confirmPin"
                  type="password"
                  maxLength={6}
                  value={confirmPin}
                  onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="text-center text-lg tracking-widest"
                />
              </div>
              <div className="flex space-x-2">
                <Button onClick={setupPin} disabled={loading} className="flex-1">
                  {loading ? 'Configurazione...' : t.setupPin}
                </Button>
                <Button onClick={() => setCurrentStep('choose')} variant="outline" className="flex-1">
                  {t.cancel}
                </Button>
              </div>
            </div>
          )}

          {currentStep === 'setup-sms' && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="phoneNumber" className="text-sm">{t.phoneNumber}</Label>
                <Input
                  id="phoneNumber"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+39 333 1234567"
                />
              </div>
              <div className="flex space-x-2">
                <Button onClick={sendSmsCode} disabled={loading} className="flex-1">
                  {loading ? 'Invio...' : t.sendSmsCode}
                </Button>
                <Button onClick={() => setCurrentStep('choose')} variant="outline" className="flex-1">
                  {t.cancel}
                </Button>
              </div>
            </div>
          )}

          {currentStep === 'verify-sms' && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="smsCode" className="text-sm">{t.enterSmsCode}</Label>
                <Input
                  id="smsCode"
                  maxLength={6}
                  value={smsCode}
                  onChange={(e) => setSmsCode(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="text-center text-lg tracking-widest"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Codice inviato a {phoneNumber}
                </p>
              </div>
              <div className="flex space-x-2">
                <Button onClick={verifySmsCode} disabled={loading} className="flex-1">
                  {loading ? 'Verifica...' : t.verify}
                </Button>
                <Button onClick={() => setCurrentStep('setup-sms')} variant="outline" className="flex-1">
                  Indietro
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function SecurityVerification({ user, onVerificationComplete }) {
  const [currentMethod, setCurrentMethod] = useState('choose');
  const [pin, setPin] = useState('');
  const [smsCode, setSmsCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [securityStatus, setSecurityStatus] = useState({});
  const { toast } = useToast();
  const { t } = useAuth();

  useEffect(() => {
    fetchSecurityStatus();
  }, []);

  const fetchSecurityStatus = async () => {
    try {
      const response = await axios.get(`${API}/security/status`);
      setSecurityStatus(response.data);
      
      // Auto-select primary method
      if (response.data.face_id_enabled) {
        setCurrentMethod('biometric');
      } else if (response.data.pin_enabled) {
        setCurrentMethod('pin');
      } else if (response.data.sms_enabled) {
        setCurrentMethod('sms');
      }
    } catch (error) {
      console.error('Failed to fetch security status', error);
    }
  };

  const verifyBiometric = async () => {
    setLoading(true);
    try {
      const { startAuthentication } = await import('@simplewebauthn/browser');
      
      // Get authentication options
      const optionsResponse = await axios.post(`${API}/security/webauthn/generate-authentication-options`);
      
      // Start WebAuthn authentication
      const credential = await startAuthentication(optionsResponse.data);
      
      // Verify with backend
      await axios.post(`${API}/security/webauthn/verify-authentication`, { credential });
      
      toast({
        title: t.success,
        description: t.accessGranted,
      });
      onVerificationComplete();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.authenticationFailed,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const verifyPin = async () => {
    if (pin.length !== 6) {
      toast({
        title: t.error,
        description: t.pin6Digits,
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/security/verify-pin`, { pin });
      toast({
        title: t.success,
        description: t.accessGranted,
      });
      onVerificationComplete();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.authenticationFailed,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const sendSmsCode = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/security/send-sms-code`, { phone_number: user.phone_number });
      toast({
        title: t.success,
        description: t.smsCodeSent,
      });
      setCurrentMethod('verify-sms');
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || "Failed to send SMS",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const verifySmsCode = async () => {
    if (smsCode.length !== 6) {
      toast({
        title: t.error,
        description: "SMS code must be 6 digits",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/security/verify-sms-code`, { 
        phone_number: user.phone_number, 
        code: smsCode 
      });
      toast({
        title: t.success,
        description: t.accessGranted,
      });
      onVerificationComplete();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.authenticationFailed,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-white shadow-lg border-0">
        <CardHeader className="text-center pb-4">
          <div className="w-16 h-16 bg-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-xl text-gray-900">{t.securityRequired}</CardTitle>
          <CardDescription className="text-sm text-gray-600">
            Verifica la tua identità per accedere
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {currentMethod === 'choose' && (
            <div className="space-y-2">
              {securityStatus.face_id_enabled && (
                <Button onClick={() => setCurrentMethod('biometric')} className="w-full bg-orange-600 hover:bg-orange-700">
                  <Smartphone className="w-4 h-4 mr-2" />
                  {t.biometricAuth}
                </Button>
              )}
              
              {securityStatus.pin_enabled && (
                <Button onClick={() => setCurrentMethod('pin')} variant="outline" className="w-full">
                  <Key className="w-4 h-4 mr-2" />
                  {t.pin}
                </Button>
              )}
              
              {securityStatus.sms_enabled && (
                <Button onClick={sendSmsCode} variant="outline" className="w-full" disabled={loading}>
                  <MessageSquare className="w-4 h-4 mr-2" />
                  {t.smsVerification}
                </Button>
              )}
            </div>
          )}

          {currentMethod === 'biometric' && (
            <div className="space-y-4 text-center">
              <div className="py-8">
                <Smartphone className="w-16 h-16 text-orange-600 mx-auto mb-4" />
                <p className="text-sm text-gray-600">Usa Face ID o Touch ID per autenticarti</p>
              </div>
              <div className="flex space-x-2">
                <Button onClick={verifyBiometric} disabled={loading} className="flex-1">
                  {loading ? 'Verifica...' : t.authenticate}
                </Button>
                <Button onClick={() => setCurrentMethod('choose')} variant="outline" className="flex-1">
                  {t.useAlternative}
                </Button>
              </div>
            </div>
          )}

          {currentMethod === 'pin' && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="verifyPin" className="text-sm">{t.enterPin}</Label>
                <Input
                  id="verifyPin"
                  type="password"
                  maxLength={6}
                  value={pin}
                  onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="text-center text-lg tracking-widest"
                />
              </div>
              <div className="flex space-x-2">
                <Button onClick={verifyPin} disabled={loading} className="flex-1">
                  {loading ? 'Verifica...' : t.verify}
                </Button>
                <Button onClick={() => setCurrentMethod('choose')} variant="outline" className="flex-1">
                  Indietro
                </Button>
              </div>
            </div>
          )}

          {currentMethod === 'verify-sms' && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="verifySmsCode" className="text-sm">{t.enterSmsCode}</Label>
                <Input
                  id="verifySmsCode"
                  maxLength={6}
                  value={smsCode}
                  onChange={(e) => setSmsCode(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="text-center text-lg tracking-widest"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Codice inviato a {user.phone_number}
                </p>
              </div>
              <div className="flex space-x-2">
                <Button onClick={verifySmsCode} disabled={loading} className="flex-1">
                  {loading ? 'Verifica...' : t.verify}
                </Button>
                <Button onClick={() => setCurrentMethod('choose')} variant="outline" className="flex-1">
                  Indietro
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
function CompanyAdminDashboard() {
  const [couriers, setCouriers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Courier management states
  const [newCourier, setNewCourier] = useState({ username: '', password: '', full_name: '' });
  const [editingCourier, setEditingCourier] = useState(null);
  const [deletingCourier, setDeletingCourier] = useState(null);
  const [showCreateCourierDialog, setShowCreateCourierDialog] = useState(false);
  const [showEditCourierDialog, setShowEditCourierDialog] = useState(false);
  const [showDeleteCourierDialog, setShowDeleteCourierDialog] = useState(false);
  
  // Customer management states
  const [newCustomer, setNewCustomer] = useState({ name: '', phone_number: '', address: '', email: '', notes: '' });
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [deletingCustomer, setDeletingCustomer] = useState(null);
  const [viewingCustomer, setViewingCustomer] = useState(null);
  const [customerOrders, setCustomerOrders] = useState([]);
  const [showCreateCustomerDialog, setShowCreateCustomerDialog] = useState(false);
  const [showEditCustomerDialog, setShowEditCustomerDialog] = useState(false);
  const [showDeleteCustomerDialog, setShowDeleteCustomerDialog] = useState(false);
  const [showCustomerHistoryDialog, setShowCustomerHistoryDialog] = useState(false);
  
  // Order management states
  const [newOrder, setNewOrder] = useState({ customer_name: '', delivery_address: '', phone_number: '', reference_number: '', customer_id: '' });
  const [editingOrder, setEditingOrder] = useState(null);
  const [deletingOrder, setDeletingOrder] = useState(null);
  const [assigningOrder, setAssigningOrder] = useState(null);
  const [showCreateOrderDialog, setShowCreateOrderDialog] = useState(false);
  const [showEditOrderDialog, setShowEditOrderDialog] = useState(false);
  const [showDeleteOrderDialog, setShowDeleteOrderDialog] = useState(false);
  const [showAssignOrderDialog, setShowAssignOrderDialog] = useState(false);
  const [useExistingCustomer, setUseExistingCustomer] = useState(false);
  const [customerSearch, setCustomerSearch] = useState('');
  const [filteredCustomers, setFilteredCustomers] = useState([]);
  const [showCustomerDropdown, setShowCustomerDropdown] = useState(false);
  
  // Search and filter states
  const [searchFilters, setSearchFilters] = useState({
    customer_name: '',
    courier_id: '',
    status: '',
    date_from: '',
    date_to: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  
  const { user, company, logout, t } = useAuth();
  const { toast } = useToast();

  // Fetch data functions
  const fetchCouriers = async () => {
    try {
      const response = await axios.get(`${API}/couriers`);
      setCouriers(response.data);
    } catch (error) {
      toast({
        title: t.error,
        description: t.failedToFetchData,
        variant: "destructive",
      });
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers`);
      setCustomers(response.data);
    } catch (error) {
      toast({
        title: t.error,
        description: t.failedToFetchData,
        variant: "destructive",
      });
    }
  };

  const fetchOrders = async () => {
    try {
      let url = `${API}/orders`;
      const hasCustomFilters = Object.values(searchFilters).some(filter => filter && filter.trim() !== '');
      
      if (hasCustomFilters) {
        const params = new URLSearchParams();
        Object.entries(searchFilters).forEach(([key, value]) => {
          if (value && value.trim() !== '') {
            params.append(key, value);
          }
        });
        url = `${API}/orders/search?${params.toString()}`;
      }
      
      const response = await axios.get(url);
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToFetchData,
        variant: "destructive",
      });
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      await Promise.all([fetchCouriers(), fetchCustomers(), fetchOrders()]);
    } finally {
      setLoading(false);
    }
  };

  // Courier management functions
  const createCourier = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/couriers`, newCourier);
      toast({
        title: t.success,
        description: t.courierCreatedSuccessfully,
      });
      setNewCourier({ username: '', password: '', full_name: '' });
      setShowCreateCourierDialog(false);
      fetchCouriers();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToCreateCourier,
        variant: "destructive",
      });
    }
  };

  const updateCourier = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`${API}/couriers/${editingCourier.id}`, {
        username: editingCourier.username,
        password: editingCourier.password || undefined
      });
      toast({
        title: t.success,
        description: t.courierUpdatedSuccessfully,
      });
      setEditingCourier(null);
      setShowEditCourierDialog(false);
      fetchCouriers();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToUpdateCourier,
        variant: "destructive",
      });
    }
  };

  const deleteCourier = async () => {
    try {
      await axios.delete(`${API}/couriers/${deletingCourier.id}`);
      toast({
        title: t.success,
        description: t.courierDeletedSuccessfully,
      });
      setDeletingCourier(null);
      setShowDeleteCourierDialog(false);
      fetchCouriers();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToDeleteCourier,
        variant: "destructive",
      });
    }
  };

  const toggleCourierStatus = async (courierId) => {
    try {
      await axios.patch(`${API}/couriers/${courierId}/toggle`);
      toast({
        title: t.success,
        description: t.statusUpdated,
      });
      fetchCouriers();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || "Failed to update courier status",
        variant: "destructive",
      });
    }
  };

  // Customer management functions
  const createCustomer = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/customers`, newCustomer);
      toast({
        title: t.success,
        description: t.customerCreatedSuccessfully,
      });
      setNewCustomer({ name: '', phone_number: '', address: '', email: '', notes: '' });
      setShowCreateCustomerDialog(false);
      fetchCustomers();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToCreateCustomer,
        variant: "destructive",
      });
    }
  };

  const updateCustomer = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`${API}/customers/${editingCustomer.id}`, {
        name: editingCustomer.name,
        phone_number: editingCustomer.phone_number,
        address: editingCustomer.address,
        email: editingCustomer.email,
        notes: editingCustomer.notes
      });
      toast({
        title: t.success,
        description: t.customerUpdatedSuccessfully,
      });
      setEditingCustomer(null);
      setShowEditCustomerDialog(false);
      fetchCustomers();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToUpdateCustomer,
        variant: "destructive",
      });
    }
  };

  const deleteCustomer = async () => {
    try {
      await axios.delete(`${API}/customers/${deletingCustomer.id}`);
      toast({
        title: t.success,
        description: t.customerDeletedSuccessfully,
      });
      setDeletingCustomer(null);
      setShowDeleteCustomerDialog(false);
      fetchCustomers();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToDeleteCustomer,
        variant: "destructive",
      });
    }
  };

  const viewCustomerHistory = async (customer) => {
    try {
      const response = await axios.get(`${API}/customers/${customer.id}/orders`);
      setCustomerOrders(response.data);
      setViewingCustomer(customer);
      setShowCustomerHistoryDialog(true);
    } catch (error) {
      toast({
        title: t.error,
        description: t.failedToFetchData,
        variant: "destructive",
      });
    }
  };

  // Order management functions
  const createOrder = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/orders`, newOrder);
      toast({
        title: t.success,
        description: t.orderCreatedSuccessfully,
      });
      setNewOrder({ customer_name: '', delivery_address: '', phone_number: '', reference_number: '', customer_id: '' });
      setCustomerSearch('');
      setUseExistingCustomer(false);
      setShowCustomerDropdown(false);
      setShowCreateOrderDialog(false);
      fetchOrders();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToCreateOrder,
        variant: "destructive",
      });
    }
  };

  const updateOrder = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`${API}/orders/${editingOrder.id}`, {
        customer_name: editingOrder.customer_name,
        delivery_address: editingOrder.delivery_address,
        phone_number: editingOrder.phone_number,
        reference_number: editingOrder.reference_number
      });
      toast({
        title: t.success,
        description: t.orderUpdatedSuccessfully,
      });
      setEditingOrder(null);
      setShowEditOrderDialog(false);
      fetchOrders();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToUpdateOrder,
        variant: "destructive",
      });
    }
  };

  const deleteOrder = async () => {
    try {
      await axios.delete(`${API}/orders/${deletingOrder.id}`);
      toast({
        title: t.success,
        description: t.orderDeletedSuccessfully,
      });
      setDeletingOrder(null);
      setShowDeleteOrderDialog(false);
      fetchOrders();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToDeleteOrder,
        variant: "destructive",
      });
    }
  };

  const assignOrder = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`${API}/orders/assign`, {
        order_id: assigningOrder.orderId,
        courier_id: assigningOrder.courierId
      });
      toast({
        title: t.success,
        description: t.orderAssignedSuccessfully,
      });
      setAssigningOrder(null);
      setShowAssignOrderDialog(false);
      fetchOrders();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToAssignOrder,
        variant: "destructive",
      });
    }
  };

  const exportOrders = async (format = 'excel') => {
    try {
      const params = new URLSearchParams();
      Object.entries(searchFilters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      params.append('format', format);
      
      const response = await axios.get(`${API}/orders/export?${params.toString()}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ordini.${format === 'excel' ? 'xlsx' : 'csv'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast({
        title: t.success,
        description: `Orders exported to ${format.toUpperCase()}`,
      });
    } catch (error) {
      toast({
        title: t.error,
        description: "Failed to export orders",
        variant: "destructive",
      });
    }
  };

  const applyFilters = () => {
    fetchOrders();
    setShowFilters(false);
  };

  const clearFilters = () => {
    setSearchFilters({
      customer_name: '',
      courier_id: '',
      status: '',
      date_from: '',
      date_to: ''
    });
    fetchOrders();
  };

  const handleEditCourierClick = (courier) => {
    setEditingCourier({...courier, password: ''});
    setShowEditCourierDialog(true);
  };

  const handleDeleteCourierClick = (courier) => {
    setDeletingCourier(courier);
    setShowDeleteCourierDialog(true);
  };

  const handleEditCustomerClick = (customer) => {
    setEditingCustomer({...customer});
    setShowEditCustomerDialog(true);
  };

  const handleDeleteCustomerClick = (customer) => {
    setDeletingCustomer(customer);
    setShowDeleteCustomerDialog(true);
  };

  const handleEditOrderClick = (order) => {
    setEditingOrder({...order});
    setShowEditOrderDialog(true);
  };

  const handleDeleteOrderClick = (order) => {
    setDeletingOrder(order);
    setShowDeleteOrderDialog(true);
  };

  const handleAssignOrderClick = (order) => {
    setAssigningOrder({ orderId: order.id, courierId: '' });
    setShowAssignOrderDialog(true);
  };

  // Customer search functions
  const searchCustomers = (query) => {
    setCustomerSearch(query);
    if (query.length > 0) {
      const filtered = customers.filter(customer =>
        customer.name.toLowerCase().includes(query.toLowerCase()) ||
        customer.phone_number.includes(query)
      );
      setFilteredCustomers(filtered);
      setShowCustomerDropdown(true);
    } else {
      setFilteredCustomers([]);
      setShowCustomerDropdown(false);
    }
  };

  const selectCustomer = (customer) => {
    setNewOrder({
      ...newOrder,
      customer_id: customer.id,
      customer_name: customer.name,
      delivery_address: customer.address,
      phone_number: customer.phone_number
    });
    setCustomerSearch(customer.name);
    setShowCustomerDropdown(false);
    setUseExistingCustomer(true);
  };

  const clearCustomerSelection = () => {
    setNewOrder({
      ...newOrder,
      customer_id: '',
      customer_name: '',
      delivery_address: '',
      phone_number: ''
    });
    setCustomerSearch('');
    setUseExistingCustomer(false);
    setShowCustomerDropdown(false);
  };

  const getOrderStatusBadge = (status) => {
    const statusConfig = {
      pending: { variant: 'secondary', color: 'bg-gray-100 text-gray-800', text: t.pending },
      assigned: { variant: 'default', color: 'bg-blue-100 text-blue-800', text: t.assigned },
      in_progress: { variant: 'default', color: 'bg-yellow-100 text-yellow-800', text: t.inProgress },
      delivered: { variant: 'default', color: 'bg-green-100 text-green-800', text: t.delivered }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    return <Badge className={config.color}>{config.text}</Badge>;
  };

  const getCourierName = (courierId) => {
    const courier = couriers.find(c => c.id === courierId);
    return courier ? (courier.full_name || courier.username) : t.unassigned;
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (searchFilters.customer_name || searchFilters.courier_id || searchFilters.status || searchFilters.date_from || searchFilters.date_to) {
      fetchOrders();
    }
  }, [searchFilters]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
      <div className="container mx-auto p-4 sm:p-6 max-w-7xl">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 sm:mb-8 space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-orange-600 rounded-full flex items-center justify-center flex-shrink-0">
              <Building2 className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 truncate">
                Dashboard {company?.name}
              </h1>
              <p className="text-sm sm:text-base text-gray-600 truncate">{company?.name} • {user.username}</p>
            </div>
          </div>
          <Button onClick={logout} variant="outline" size="sm" className="w-full sm:w-auto">
            <LogOut className="w-4 h-4 mr-2" />
            {t.logout}
          </Button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mb-6">
          <Button
            variant={activeTab === 'overview' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('overview')}
            className="text-xs sm:text-sm"
          >
            {t.overview}
          </Button>
          <Button
            variant={activeTab === 'customers' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('customers')}
            className="text-xs sm:text-sm"
          >
            {t.customers}
          </Button>
          <Button
            variant={activeTab === 'couriers' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('couriers')}
            className="text-xs sm:text-sm"
          >
            {t.couriers}
          </Button>
          <Button
            variant={activeTab === 'orders' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab('orders')}
            className="text-xs sm:text-sm"
          >
            {t.orders}
          </Button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
              <Card className="bg-white shadow-sm border-0">
                <CardContent className="p-4 sm:p-6">
                  <div className="flex items-center justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.totalCustomers}</p>
                      <p className="text-2xl sm:text-3xl font-bold text-gray-900">{customers.length}</p>
                    </div>
                    <User className="w-6 h-6 sm:w-8 sm:h-8 text-purple-600 flex-shrink-0" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white shadow-sm border-0">
                <CardContent className="p-4 sm:p-6">
                  <div className="flex items-center justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.totalCouriers}</p>
                      <p className="text-2xl sm:text-3xl font-bold text-gray-900">{couriers.length}</p>
                    </div>
                    <Users className="w-6 h-6 sm:w-8 sm:h-8 text-orange-600 flex-shrink-0" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-white shadow-sm border-0">
                <CardContent className="p-4 sm:p-6">
                  <div className="flex items-center justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.activeCouriers}</p>
                      <p className="text-2xl sm:text-3xl font-bold text-gray-900">
                        {couriers.filter(c => c.is_active).length}
                      </p>
                    </div>
                    <CheckCircle className="w-6 h-6 sm:w-8 sm:h-8 text-green-600 flex-shrink-0" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-white shadow-sm border-0">
                <CardContent className="p-4 sm:p-6">
                  <div className="flex items-center justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.totalOrders}</p>
                      <p className="text-2xl sm:text-3xl font-bold text-gray-900">{orders.length}</p>
                    </div>
                    <Package className="w-6 h-6 sm:w-8 sm:h-8 text-blue-600 flex-shrink-0" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Orders */}
            <Card className="bg-white shadow-sm border-0">
              <CardHeader className="p-4 sm:p-6">
                <CardTitle className="text-lg sm:text-xl">{t.recentOrders}</CardTitle>
                <CardDescription className="text-sm">{t.latestOrderActivity}</CardDescription>
              </CardHeader>
              <CardContent className="p-4 sm:p-6">
                <div className="space-y-4">
                  {orders.slice(0, 5).map((order) => (
                    <div key={order.id} className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-3 border rounded-lg space-y-2 sm:space-y-0">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm sm:text-base truncate">{order.customer_name}</p>
                        <p className="text-xs sm:text-sm text-gray-600 truncate">{order.delivery_address}</p>
                        <p className="text-xs text-gray-500">{getCourierName(order.courier_id)}</p>
                      </div>
                      <div className="flex items-center space-x-2 w-full sm:w-auto justify-between sm:justify-end">
                        {getOrderStatusBadge(order.status)}
                        <p className="text-xs text-gray-500">
                          {new Date(order.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Customers Tab */}
        {activeTab === 'customers' && (
          <Card className="bg-white shadow-sm border-0">
            <CardHeader className="p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
                <div>
                  <CardTitle className="text-lg sm:text-xl">{t.customerManagement}</CardTitle>
                  <CardDescription className="text-sm">{t.manageAllCustomers}</CardDescription>
                </div>
                <Dialog open={showCreateCustomerDialog} onOpenChange={setShowCreateCustomerDialog}>
                  <DialogTrigger asChild>
                    <Button className="bg-orange-600 hover:bg-orange-700 text-sm w-full sm:w-auto">
                      <UserPlus className="w-4 h-4 mr-2" />
                      {t.addCustomer}
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
                    <DialogHeader>
                      <DialogTitle className="text-lg">{t.createNewCustomer}</DialogTitle>
                      <DialogDescription className="text-sm">{t.addNewCustomerDescription}</DialogDescription>
                    </DialogHeader>
                    <form onSubmit={createCustomer} className="space-y-4">
                      <div>
                        <Label htmlFor="customerName" className="text-sm">{t.customerName}</Label>
                        <Input
                          id="customerName"
                          value={newCustomer.name}
                          onChange={(e) => setNewCustomer({ ...newCustomer, name: e.target.value })}
                          placeholder={t.enterCustomerName}
                          required
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label htmlFor="customerPhone" className="text-sm">{t.phoneNumber}</Label>
                        <Input
                          id="customerPhone"
                          value={newCustomer.phone_number}
                          onChange={(e) => setNewCustomer({ ...newCustomer, phone_number: e.target.value })}
                          placeholder={t.enterPhoneNumber}
                          required
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label htmlFor="customerAddress" className="text-sm">{t.address}</Label>
                        <Input
                          id="customerAddress"
                          value={newCustomer.address}
                          onChange={(e) => setNewCustomer({ ...newCustomer, address: e.target.value })}
                          placeholder={t.enterDeliveryAddress}
                          required
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label htmlFor="customerEmail" className="text-sm">{t.email} ({t.optional})</Label>
                        <Input
                          id="customerEmail"
                          type="email"
                          value={newCustomer.email}
                          onChange={(e) => setNewCustomer({ ...newCustomer, email: e.target.value })}
                          placeholder={t.enterEmail}
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label htmlFor="customerNotes" className="text-sm">{t.notes} ({t.optional})</Label>
                        <Input
                          id="customerNotes"
                          value={newCustomer.notes}
                          onChange={(e) => setNewCustomer({ ...newCustomer, notes: e.target.value })}
                          placeholder={t.enterNotes}
                          className="text-sm"
                        />
                      </div>
                      <Button type="submit" className="w-full text-sm">{t.createCustomer}</Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent className="p-4 sm:p-6">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-xs sm:text-sm">{t.customerName}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.phoneNumber}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.address}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.totalOrders}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.lastOrder}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.actions}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {customers.map((customer) => (
                      <TableRow key={customer.id}>
                        <TableCell className="font-medium text-xs sm:text-sm">{customer.name}</TableCell>
                        <TableCell className="text-xs sm:text-sm">{customer.phone_number}</TableCell>
                        <TableCell className="text-xs sm:text-sm max-w-32 truncate">{customer.address}</TableCell>
                        <TableCell className="text-xs sm:text-sm">{customer.total_orders || 0}</TableCell>
                        <TableCell className="text-xs sm:text-sm">
                          {customer.last_order_date ? new Date(customer.last_order_date).toLocaleDateString() : t.never}
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-col sm:flex-row space-y-1 sm:space-y-0 sm:space-x-1">
                            <Button
                              onClick={() => viewCustomerHistory(customer)}
                              variant="outline"
                              size="sm"
                              className="text-xs"
                            >
                              {t.customerHistory}
                            </Button>
                            <Button
                              onClick={() => handleEditCustomerClick(customer)}
                              variant="outline"
                              size="sm"
                              className="text-xs"
                            >
                              {t.edit}
                            </Button>
                            <Button
                              onClick={() => handleDeleteCustomerClick(customer)}
                              variant="destructive"
                              size="sm"
                              className="text-xs"
                            >
                              {t.delete}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Add all dialogs and additional content here - continuing in next part due to length */}

        {/* Couriers Tab */}
        {activeTab === 'couriers' && (
          <Card className="bg-white shadow-sm border-0">
            <CardHeader className="p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
                <div>
                  <CardTitle className="text-lg sm:text-xl">{t.couriersManagement}</CardTitle>
                  <CardDescription className="text-sm">{t.manageAllCouriers}</CardDescription>
                </div>
                <Dialog open={showCreateCourierDialog} onOpenChange={setShowCreateCourierDialog}>
                  <DialogTrigger asChild>
                    <Button className="bg-orange-600 hover:bg-orange-700 text-sm w-full sm:w-auto">
                      <UserPlus className="w-4 h-4 mr-2" />
                      {t.addCourier}
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
                    <DialogHeader>
                      <DialogTitle className="text-lg">{t.createNewCourier}</DialogTitle>
                      <DialogDescription className="text-sm">{t.addNewCourierDescription}</DialogDescription>
                    </DialogHeader>
                    <form onSubmit={createCourier} className="space-y-4">
                      <div>
                        <Label htmlFor="courierFullName" className="text-sm">{t.fullName}</Label>
                        <Input
                          id="courierFullName"
                          value={newCourier.full_name}
                          onChange={(e) => setNewCourier({ ...newCourier, full_name: e.target.value })}
                          placeholder={t.enterFullName}
                          required
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label htmlFor="courierUsername" className="text-sm">{t.username}</Label>
                        <Input
                          id="courierUsername"
                          value={newCourier.username}
                          onChange={(e) => setNewCourier({ ...newCourier, username: e.target.value })}
                          placeholder={t.enterUsername}
                          required
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label htmlFor="courierPassword" className="text-sm">{t.password}</Label>
                        <Input
                          id="courierPassword"
                          type="password"
                          value={newCourier.password}
                          onChange={(e) => setNewCourier({ ...newCourier, password: e.target.value })}
                          placeholder={t.enterPassword}
                          required
                          className="text-sm"
                        />
                      </div>
                      <Button type="submit" className="w-full text-sm">{t.createCourier}</Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent className="p-4 sm:p-6">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-xs sm:text-sm">{t.fullName}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.username}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.status}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.activeDeliveries}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.created}</TableHead>
                      <TableHead className="text-xs sm:text-sm">{t.actions}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {couriers.map((courier) => (
                      <TableRow key={courier.id}>
                        <TableCell className="font-medium text-xs sm:text-sm">{courier.full_name || courier.username}</TableCell>
                        <TableCell className="text-xs sm:text-sm">{courier.username}</TableCell>
                        <TableCell>
                          <Badge variant={courier.is_active ? 'default' : 'destructive'} className="text-xs">
                            {courier.is_active ? t.active : t.blocked}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs sm:text-sm">
                          {orders.filter(o => o.courier_id === courier.id && ['assigned', 'in_progress'].includes(o.status)).length}
                        </TableCell>
                        <TableCell className="text-xs sm:text-sm">
                          {new Date(courier.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-col sm:flex-row space-y-1 sm:space-y-0 sm:space-x-1">
                            <Button
                              onClick={() => handleEditCourierClick(courier)}
                              variant="outline"
                              size="sm"
                              className="text-xs"
                            >
                              {t.edit}
                            </Button>
                            <Button
                              onClick={() => toggleCourierStatus(courier.id)}
                              variant={courier.is_active ? 'destructive' : 'default'}
                              size="sm"
                              className="text-xs"
                            >
                              {courier.is_active ? t.block : t.activate}
                            </Button>
                            <Button
                              onClick={() => handleDeleteCourierClick(courier)}
                              variant="destructive"
                              size="sm"
                              className="text-xs"
                            >
                              {t.delete}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Orders Tab */}
        {activeTab === 'orders' && (
          <div className="space-y-6">
            {/* Orders Header with Actions */}
            <Card className="bg-white shadow-sm border-0">
              <CardHeader className="p-4 sm:p-6">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
                  <div>
                    <CardTitle className="text-lg sm:text-xl">{t.ordersManagement}</CardTitle>
                    <CardDescription className="text-sm">{t.manageAllOrders}</CardDescription>
                  </div>
                  <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 w-full sm:w-auto">
                    <Dialog open={showCreateOrderDialog} onOpenChange={setShowCreateOrderDialog}>
                      <DialogTrigger asChild>
                        <Button className="bg-orange-600 hover:bg-orange-700 text-sm">
                          <Plus className="w-4 h-4 mr-2" />
                          {t.addOrder}
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
                        <DialogHeader>
                          <DialogTitle className="text-lg">{t.createNewOrder}</DialogTitle>
                          <DialogDescription className="text-sm">{t.addNewOrderDescription}</DialogDescription>
                        </DialogHeader>
                        <form onSubmit={createOrder} className="space-y-4">
                          {/* Customer Selection */}
                          <div className="space-y-3">
                            <div className="flex items-center space-x-4">
                              <label className="flex items-center space-x-2">
                                <input
                                  type="radio"
                                  checked={!useExistingCustomer}
                                  onChange={() => {
                                    clearCustomerSelection();
                                    setUseExistingCustomer(false);
                                  }}
                                  className="text-orange-600"
                                />
                                <span className="text-sm">{t.newCustomer}</span>
                              </label>
                              <label className="flex items-center space-x-2">
                                <input
                                  type="radio"
                                  checked={useExistingCustomer}
                                  onChange={() => setUseExistingCustomer(true)}
                                  className="text-orange-600"
                                />
                                <span className="text-sm">{t.existingCustomer}</span>
                              </label>
                            </div>

                            {/* Customer Search */}
                            {useExistingCustomer && (
                              <div className="relative">
                                <Label htmlFor="customerSearch" className="text-sm">{t.searchCustomers}</Label>
                                <Input
                                  id="customerSearch"
                                  value={customerSearch}
                                  onChange={(e) => searchCustomers(e.target.value)}
                                  placeholder={t.searchCustomers}
                                  className="text-sm"
                                  onFocus={() => {
                                    if (customerSearch.length > 0) setShowCustomerDropdown(true);
                                  }}
                                />
                                
                                {/* Customer Dropdown */}
                                {showCustomerDropdown && filteredCustomers.length > 0 && (
                                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                                    {filteredCustomers.map((customer) => (
                                      <div
                                        key={customer.id}
                                        className="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100"
                                        onClick={() => selectCustomer(customer)}
                                      >
                                        <div className="flex justify-between items-center">
                                          <div>
                                            <p className="text-sm font-medium text-gray-900">{customer.name}</p>
                                            <p className="text-xs text-gray-600">{customer.phone_number}</p>
                                          </div>
                                          <div className="text-right">
                                            <p className="text-xs text-gray-500">{customer.total_orders || 0} ordini</p>
                                          </div>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                                
                                {useExistingCustomer && customerSearch.length > 0 && filteredCustomers.length === 0 && (
                                  <p className="text-xs text-gray-500 mt-1">{t.noCustomersFound}</p>
                                )}
                              </div>
                            )}
                          </div>

                          <div>
                            <Label htmlFor="customerName" className="text-sm">{t.customerName}</Label>
                            <Input
                              id="customerName"
                              value={newOrder.customer_name}
                              onChange={(e) => setNewOrder({ ...newOrder, customer_name: e.target.value })}
                              placeholder={t.enterCustomerName}
                              required
                              className="text-sm"
                              disabled={useExistingCustomer && newOrder.customer_id}
                            />
                          </div>
                          <div>
                            <Label htmlFor="deliveryAddress" className="text-sm">{t.deliveryAddress}</Label>
                            <Input
                              id="deliveryAddress"
                              value={newOrder.delivery_address}
                              onChange={(e) => setNewOrder({ ...newOrder, delivery_address: e.target.value })}
                              placeholder={t.enterDeliveryAddress}
                              required
                              className="text-sm"
                            />
                          </div>
                          <div>
                            <Label htmlFor="phoneNumber" className="text-sm">{t.phoneNumber} ({t.optional})</Label>
                            <Input
                              id="phoneNumber"
                              value={newOrder.phone_number}
                              onChange={(e) => setNewOrder({ ...newOrder, phone_number: e.target.value })}
                              placeholder={t.enterPhoneNumber}
                              className="text-sm"
                              disabled={useExistingCustomer && newOrder.customer_id}
                            />
                            <p className="text-xs text-gray-500 mt-1">
                              {t.phoneOptionalNote}
                            </p>
                          </div>
                          <div>
                            <Label htmlFor="referenceNumber" className="text-sm">{t.referenceNumber}</Label>
                            <Input
                              id="referenceNumber"
                              value={newOrder.reference_number}
                              onChange={(e) => setNewOrder({ ...newOrder, reference_number: e.target.value })}
                              placeholder={t.enterReferenceNumber}
                              className="text-sm"
                            />
                          </div>
                          <Button type="submit" className="w-full text-sm">{t.createOrder}</Button>
                        </form>
                      </DialogContent>
                    </Dialog>
                    
                    <Button
                      onClick={() => setShowFilters(!showFilters)}
                      variant="outline"
                      size="sm"
                      className="text-sm"
                    >
                      🔍 {t.filters}
                    </Button>
                    
                    <div className="flex space-x-1">
                      <Button
                        onClick={() => exportOrders('excel')}
                        variant="outline"
                        size="sm"
                        className="text-sm"
                      >
                        📊 Excel
                      </Button>
                      <Button
                        onClick={() => exportOrders('csv')}
                        variant="outline"
                        size="sm"
                        className="text-sm"
                      >
                        📄 CSV
                      </Button>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              {/* Filters */}
              {showFilters && (
                <CardContent className="p-4 sm:p-6 border-t">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="filterCustomer" className="text-sm">{t.customerName}</Label>
                      <Input
                        id="filterCustomer"
                        value={searchFilters.customer_name}
                        onChange={(e) => setSearchFilters({ ...searchFilters, customer_name: e.target.value })}
                        placeholder={t.searchByCustomer}
                        className="text-sm"
                      />
                    </div>
                    <div>
                      <Label htmlFor="filterCourier" className="text-sm">{t.courier}</Label>
                      <Select
                        value={searchFilters.courier_id}
                        onValueChange={(value) => setSearchFilters({ ...searchFilters, courier_id: value })}
                      >
                        <SelectTrigger className="text-sm">
                          <SelectValue placeholder={t.selectCourier} />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">{t.allCouriers}</SelectItem>
                          {couriers.map((courier) => (
                            <SelectItem key={courier.id} value={courier.id}>
                              {courier.username}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="filterStatus" className="text-sm">{t.status}</Label>
                      <Select
                        value={searchFilters.status}
                        onValueChange={(value) => setSearchFilters({ ...searchFilters, status: value })}
                      >
                        <SelectTrigger className="text-sm">
                          <SelectValue placeholder={t.selectStatus} />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">{t.allStatuses}</SelectItem>
                          <SelectItem value="pending">{t.pending}</SelectItem>
                          <SelectItem value="assigned">{t.assigned}</SelectItem>
                          <SelectItem value="in_progress">{t.inProgress}</SelectItem>
                          <SelectItem value="delivered">{t.delivered}</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="filterDateFrom" className="text-sm">{t.dateFrom}</Label>
                      <Input
                        id="filterDateFrom"
                        type="date"
                        value={searchFilters.date_from}
                        onChange={(e) => setSearchFilters({ ...searchFilters, date_from: e.target.value })}
                        className="text-sm"
                      />
                    </div>
                    <div>
                      <Label htmlFor="filterDateTo" className="text-sm">{t.dateTo}</Label>
                      <Input
                        id="filterDateTo"
                        type="date"
                        value={searchFilters.date_to}
                        onChange={(e) => setSearchFilters({ ...searchFilters, date_to: e.target.value })}
                        className="text-sm"
                      />
                    </div>
                    <div className="flex items-end space-x-2">
                      <Button onClick={applyFilters} size="sm" className="text-sm">
                        {t.applyFilters}
                      </Button>
                      <Button onClick={clearFilters} variant="outline" size="sm" className="text-sm">
                        {t.clearFilters}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>

            {/* Orders Table */}
            <Card className="bg-white shadow-sm border-0">
              <CardContent className="p-4 sm:p-6">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="text-xs sm:text-sm">{t.customer}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.address}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.phone}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.reference}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.courier}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.status}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.created}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.actions}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {orders.map((order) => (
                        <TableRow key={order.id}>
                          <TableCell className="font-medium text-xs sm:text-sm">{order.customer_name}</TableCell>
                          <TableCell className="text-xs sm:text-sm max-w-32 truncate">{order.delivery_address}</TableCell>
                          <TableCell className="text-xs sm:text-sm">{order.phone_number}</TableCell>
                          <TableCell className="text-xs sm:text-sm">{order.reference_number || '-'}</TableCell>
                          <TableCell className="text-xs sm:text-sm">{getCourierName(order.courier_id)}</TableCell>
                          <TableCell>{getOrderStatusBadge(order.status)}</TableCell>
                          <TableCell className="text-xs sm:text-sm">
                            {new Date(order.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <div className="flex flex-col sm:flex-row space-y-1 sm:space-y-0 sm:space-x-1">
                              <Button
                                onClick={() => handleEditOrderClick(order)}
                                variant="outline"
                                size="sm"
                                className="text-xs"
                                disabled={order.status === 'delivered'}
                              >
                                {t.edit}
                              </Button>
                              <Button
                                onClick={() => handleAssignOrderClick(order)}
                                variant="outline"
                                size="sm"
                                className="text-xs"
                                disabled={order.status === 'delivered'}
                              >
                                {order.courier_id ? t.reassign : t.assign}
                              </Button>
                              <Button
                                onClick={() => handleDeleteOrderClick(order)}
                                variant="destructive"
                                size="sm"
                                className="text-xs"
                                disabled={order.status === 'delivered'}
                              >
                                {t.delete}
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* All Dialog Components */}
        {/* Edit Courier Dialog */}
        <Dialog open={showEditCourierDialog} onOpenChange={setShowEditCourierDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.editCourier}</DialogTitle>
              <DialogDescription className="text-sm">{t.editCourierDescription}</DialogDescription>
            </DialogHeader>
            {editingCourier && (
              <form onSubmit={updateCourier} className="space-y-4">
                <div>
                  <Label htmlFor="editCourierFullName" className="text-sm">{t.fullName}</Label>
                  <Input
                    id="editCourierFullName"
                    value={editingCourier.full_name || ''}
                    onChange={(e) => setEditingCourier({ ...editingCourier, full_name: e.target.value })}
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editCourierUsername" className="text-sm">{t.username}</Label>
                  <Input
                    id="editCourierUsername"
                    value={editingCourier.username}
                    onChange={(e) => setEditingCourier({ ...editingCourier, username: e.target.value })}
                    required
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editCourierPassword" className="text-sm">{t.newPassword} ({t.optional})</Label>
                  <Input
                    id="editCourierPassword"
                    type="password"
                    value={editingCourier.password}
                    onChange={(e) => setEditingCourier({ ...editingCourier, password: e.target.value })}
                    placeholder={t.leaveEmptyToKeepCurrent}
                    className="text-sm"
                  />
                </div>
                <div className="flex space-x-2">
                  <Button type="submit" className="flex-1 text-sm">{t.updateCourier}</Button>
                  <Button type="button" variant="outline" onClick={() => setShowEditCourierDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* Delete Courier Dialog */}
        <Dialog open={showDeleteCourierDialog} onOpenChange={setShowDeleteCourierDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.deleteCourier}</DialogTitle>
              <DialogDescription className="text-sm">{t.deleteCourierDescription}</DialogDescription>
            </DialogHeader>
            {deletingCourier && (
              <div className="space-y-4">
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800">
                    {t.confirmDeleteCourier}: <strong>{deletingCourier.username}</strong>
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button onClick={deleteCourier} variant="destructive" className="flex-1 text-sm">
                    {t.deleteConfirm}
                  </Button>
                  <Button variant="outline" onClick={() => setShowDeleteCourierDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Edit Order Dialog */}
        <Dialog open={showEditOrderDialog} onOpenChange={setShowEditOrderDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.editOrder}</DialogTitle>
              <DialogDescription className="text-sm">{t.editOrderDescription}</DialogDescription>
            </DialogHeader>
            {editingOrder && (
              <form onSubmit={updateOrder} className="space-y-4">
                <div>
                  <Label htmlFor="editCustomerName" className="text-sm">{t.customerName}</Label>
                  <Input
                    id="editCustomerName"
                    value={editingOrder.customer_name}
                    onChange={(e) => setEditingOrder({ ...editingOrder, customer_name: e.target.value })}
                    required
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editDeliveryAddress" className="text-sm">{t.deliveryAddress}</Label>
                  <Input
                    id="editDeliveryAddress"
                    value={editingOrder.delivery_address}
                    onChange={(e) => setEditingOrder({ ...editingOrder, delivery_address: e.target.value })}
                    required
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editPhoneNumber" className="text-sm">{t.phoneNumber}</Label>
                  <Input
                    id="editPhoneNumber"
                    value={editingOrder.phone_number}
                    onChange={(e) => setEditingOrder({ ...editingOrder, phone_number: e.target.value })}
                    required
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editReferenceNumber" className="text-sm">{t.referenceNumber}</Label>
                  <Input
                    id="editReferenceNumber"
                    value={editingOrder.reference_number || ''}
                    onChange={(e) => setEditingOrder({ ...editingOrder, reference_number: e.target.value })}
                    className="text-sm"
                  />
                </div>
                <div className="flex space-x-2">
                  <Button type="submit" className="flex-1 text-sm">{t.updateOrder}</Button>
                  <Button type="button" variant="outline" onClick={() => setShowEditOrderDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* Delete Order Dialog */}
        <Dialog open={showDeleteOrderDialog} onOpenChange={setShowDeleteOrderDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.deleteOrder}</DialogTitle>
              <DialogDescription className="text-sm">{t.deleteOrderDescription}</DialogDescription>
            </DialogHeader>
            {deletingOrder && (
              <div className="space-y-4">
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800">
                    {t.confirmDeleteOrder}: <strong>{deletingOrder.customer_name}</strong>
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button onClick={deleteOrder} variant="destructive" className="flex-1 text-sm">
                    {t.deleteConfirm}
                  </Button>
                  <Button variant="outline" onClick={() => setShowDeleteOrderDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Assign Order Dialog */}
        <Dialog open={showAssignOrderDialog} onOpenChange={setShowAssignOrderDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.assignOrder}</DialogTitle>
              <DialogDescription className="text-sm">{t.assignOrderDescription}</DialogDescription>
            </DialogHeader>
            {assigningOrder && (
              <form onSubmit={assignOrder} className="space-y-4">
                <div>
                  <Label htmlFor="assignCourier" className="text-sm">{t.selectCourier}</Label>
                  <Select
                    value={assigningOrder.courierId}
                    onValueChange={(value) => setAssigningOrder({ ...assigningOrder, courierId: value })}
                    required
                  >
                    <SelectTrigger className="text-sm">
                      <SelectValue placeholder={t.selectCourier} />
                    </SelectTrigger>
                    <SelectContent>
                      {couriers.filter(c => c.is_active).map((courier) => (
                        <SelectItem key={courier.id} value={courier.id}>
                          {courier.username} ({orders.filter(o => o.courier_id === courier.id && ['assigned', 'in_progress'].includes(o.status)).length} {t.activeDeliveries})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex space-x-2">
                  <Button type="submit" className="flex-1 text-sm">{t.assignOrder}</Button>
                  <Button type="button" variant="outline" onClick={() => setShowAssignOrderDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* Customer Management Dialogs */}
        {/* Edit Customer Dialog */}
        <Dialog open={showEditCustomerDialog} onOpenChange={setShowEditCustomerDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.editCustomer}</DialogTitle>
              <DialogDescription className="text-sm">{t.editCustomerDescription}</DialogDescription>
            </DialogHeader>
            {editingCustomer && (
              <form onSubmit={updateCustomer} className="space-y-4">
                <div>
                  <Label htmlFor="editCustomerName" className="text-sm">{t.customerName}</Label>
                  <Input
                    id="editCustomerName"
                    value={editingCustomer.name}
                    onChange={(e) => setEditingCustomer({ ...editingCustomer, name: e.target.value })}
                    required
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editCustomerPhone" className="text-sm">{t.phoneNumber}</Label>
                  <Input
                    id="editCustomerPhone"
                    value={editingCustomer.phone_number}
                    onChange={(e) => setEditingCustomer({ ...editingCustomer, phone_number: e.target.value })}
                    required
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editCustomerAddress" className="text-sm">{t.address}</Label>
                  <Input
                    id="editCustomerAddress"
                    value={editingCustomer.address}
                    onChange={(e) => setEditingCustomer({ ...editingCustomer, address: e.target.value })}
                    required
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editCustomerEmail" className="text-sm">{t.email} ({t.optional})</Label>
                  <Input
                    id="editCustomerEmail"
                    type="email"
                    value={editingCustomer.email || ''}
                    onChange={(e) => setEditingCustomer({ ...editingCustomer, email: e.target.value })}
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editCustomerNotes" className="text-sm">{t.notes} ({t.optional})</Label>
                  <Input
                    id="editCustomerNotes"
                    value={editingCustomer.notes || ''}
                    onChange={(e) => setEditingCustomer({ ...editingCustomer, notes: e.target.value })}
                    className="text-sm"
                  />
                </div>
                <div className="flex space-x-2">
                  <Button type="submit" className="flex-1 text-sm">{t.updateCustomer}</Button>
                  <Button type="button" variant="outline" onClick={() => setShowEditCustomerDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* Delete Customer Dialog */}
        <Dialog open={showDeleteCustomerDialog} onOpenChange={setShowDeleteCustomerDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.deleteCustomer}</DialogTitle>
              <DialogDescription className="text-sm">{t.deleteCustomerDescription}</DialogDescription>
            </DialogHeader>
            {deletingCustomer && (
              <div className="space-y-4">
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800">
                    {t.confirmDeleteCustomer}: <strong>{deletingCustomer.name}</strong>
                  </p>
                  <p className="text-xs text-red-600 mt-1">
                    {deletingCustomer.total_orders > 0 
                      ? `Cliente ha ${deletingCustomer.total_orders} ordini.`
                      : "Cliente non ha ordini."
                    }
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button onClick={deleteCustomer} variant="destructive" className="flex-1 text-sm">
                    {t.deleteConfirm}
                  </Button>
                  <Button variant="outline" onClick={() => setShowDeleteCustomerDialog(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Customer History Dialog */}
        <Dialog open={showCustomerHistoryDialog} onOpenChange={setShowCustomerHistoryDialog}>
          <DialogContent className="mx-4 sm:mx-0 max-w-2xl sm:max-w-4xl">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.customerHistory}</DialogTitle>
              <DialogDescription className="text-sm">
                {viewingCustomer && `${t.customerOrders} - ${viewingCustomer.name}`}
              </DialogDescription>
            </DialogHeader>
            {viewingCustomer && (
              <div className="space-y-4">
                {/* Customer Summary */}
                <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-700">{t.customerName}</p>
                      <p className="text-base">{viewingCustomer.name}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">{t.phoneNumber}</p>
                      <p className="text-base">{viewingCustomer.phone_number}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">{t.totalOrders}</p>
                      <p className="text-base">{customerOrders.length}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">{t.lastOrder}</p>
                      <p className="text-base">
                        {customerOrders.length > 0 
                          ? new Date(customerOrders[0].created_at).toLocaleDateString()
                          : t.never
                        }
                      </p>
                    </div>
                  </div>
                </div>

                {/* Orders History */}
                <div className="max-h-96 overflow-y-auto">
                  {customerOrders.length === 0 ? (
                    <div className="text-center py-8">
                      <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500 text-sm">{t.noOrdersFound}</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {customerOrders.map((order) => (
                        <div key={order.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex flex-col sm:flex-row justify-between items-start mb-2 space-y-2 sm:space-y-0">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm text-gray-600 truncate">{order.delivery_address}</p>
                              {order.reference_number && (
                                <p className="text-xs text-gray-500">Rif: {order.reference_number}</p>
                              )}
                              {order.phone_number && (
                                <p className="text-xs text-gray-500">📱 {order.phone_number}</p>
                              )}
                            </div>
                            {getOrderStatusBadge(order.status)}
                          </div>
                          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center text-xs text-gray-500 space-y-1 sm:space-y-0">
                            <div className="flex flex-col space-y-1">
                              <span>📅 Ordinato: {new Date(order.created_at).toLocaleDateString()} alle {new Date(order.created_at).toLocaleTimeString()}</span>
                              {order.delivered_at && (
                                <span className="text-green-600">
                                  ✅ Consegnato: {new Date(order.delivered_at).toLocaleDateString()} alle {new Date(order.delivered_at).toLocaleTimeString()}
                                </span>
                              )}
                            </div>
                            <span>{getCourierName(order.courier_id)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex justify-end">
                  <Button variant="outline" onClick={() => setShowCustomerHistoryDialog(false)} className="text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}

// Dashboard Router
function DashboardRouter() {
  const { user, securityRequired, securitySetupRequired, onSecuritySetupComplete, onSecurityVerificationComplete } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  // Show security setup if required
  if (securitySetupRequired) {
    return <SecuritySetup user={user} onSecurityComplete={onSecuritySetupComplete} />;
  }

  // Show security verification if required
  if (securityRequired) {
    return <SecurityVerification user={user} onVerificationComplete={onSecurityVerificationComplete} />;
  }

  // Main app content based on user role
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
            <Route path="/unauthorized" element={
              <div className="min-h-screen flex items-center justify-center">
                <Card>
                  <CardContent className="p-6 text-center">
                    <h2 className="text-xl font-bold mb-2">Accesso Negato</h2>
                    <p>Non hai il permesso di accedere a questa pagina.</p>
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