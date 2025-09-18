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
                        {delivery.reference_number && (
                          <p className="text-gray-500 text-sm">📋 Rif: {delivery.reference_number}</p>
                        )}
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
  const [editingCompany, setEditingCompany] = useState(null);
  const [deletingCompany, setDeletingCompany] = useState(null);
  const [deletePassword, setDeletePassword] = useState('');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
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

// Company Admin Dashboard
function CompanyAdminDashboard() {
  const [couriers, setCouriers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showCreateCourier, setShowCreateCourier] = useState(false);
  const [showEditCourier, setShowEditCourier] = useState(false);
  const [editingCourier, setEditingCourier] = useState(null);
  const [showCreateOrder, setShowCreateOrder] = useState(false);
  const [showEditOrder, setShowEditOrder] = useState(false);
  const [showAssignOrder, setShowAssignOrder] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [editingOrder, setEditingOrder] = useState(null);
  const [newCourier, setNewCourier] = useState({ username: '', password: '' });
  const [newOrder, setNewOrder] = useState({ customer_name: '', delivery_address: '', phone_number: '', reference_number: '' });
  const [assignData, setAssignData] = useState({ order_id: '', courier_id: '' });
  const { user, company, logout, t } = useAuth();
  const { toast } = useToast();

  const fetchData = async () => {
    try {
      const [couriersRes, ordersRes] = await Promise.all([
        axios.get(`${API}/couriers`),
        axios.get(`${API}/orders`)
      ]);
      setCouriers(couriersRes.data);
      setOrders(ordersRes.data);
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

  const createCourier = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/couriers`, newCourier);
      toast({
        title: t.success,
        description: t.courierCreatedSuccessfully,
      });
      setNewCourier({ username: '', password: '' });
      setShowCreateCourier(false);
      fetchData();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToCreateCourier,
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
      fetchData();
    } catch (error) {
      toast({
        title: t.error,
        description: "Failed to update courier status",
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
      setShowEditCourier(false);
      fetchData();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToUpdateCourier,
        variant: "destructive",
      });
    }
  };

  const deleteCourier = async (courierId) => {
    if (!window.confirm('Sei sicuro di voler cancellare questo corriere?')) return;
    
    try {
      await axios.delete(`${API}/couriers/${courierId}`);
      toast({
        title: t.success,
        description: t.courierDeletedSuccessfully,
      });
      fetchData();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToDeleteCourier,
        variant: "destructive",
      });
    }
  };

  const createOrder = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/orders`, newOrder);
      toast({
        title: t.success,
        description: t.orderCreatedSuccessfully,
      });
      setNewOrder({ customer_name: '', delivery_address: '', phone_number: '', reference_number: '' });
      setShowCreateOrder(false);
      fetchData();
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
      const response = await axios.patch(`${API}/orders/${editingOrder.id}`, {
        customer_name: editingOrder.customer_name,
        delivery_address: editingOrder.delivery_address,
        phone_number: editingOrder.phone_number,
        reference_number: editingOrder.reference_number
      });
      
      if (response.data.suggest_reassignment) {
        toast({
          title: t.success,
          description: "Ordine aggiornato. Considera di riassegnare il corriere per il nuovo indirizzo.",
          duration: 5000,
        });
      } else {
        toast({
          title: t.success,
          description: "Ordine aggiornato con successo",
        });
      }
      
      setEditingOrder(null);
      setShowEditOrder(false);
      fetchData();
    } catch (error) {
      toast({
        title: t.error,
        description: "Impossibile aggiornare l'ordine",
        variant: "destructive",
      });
    }
  };

  const assignOrder = async (e) => {
    e.preventDefault();
    try {
      await axios.patch(`${API}/orders/assign`, assignData);
      toast({
        title: t.success,
        description: t.orderAssignedSuccessfully,
      });
      setAssignData({ order_id: '', courier_id: '' });
      setShowAssignOrder(false);
      setSelectedOrder(null);
      fetchData();
    } catch (error) {
      toast({
        title: t.error,
        description: error.response?.data?.detail || t.failedToAssignOrder,
        variant: "destructive",
      });
    }
  };

  const handleAssignClick = (order) => {
    setSelectedOrder(order);
    setAssignData({ ...assignData, order_id: order.id });
    setShowAssignOrder(true);
  };

  const handleEditClick = (order) => {
    setEditingOrder({...order});
    setShowEditOrder(true);
  };

  const handleEditCourierClick = (courier) => {
    setEditingCourier({...courier, password: ''});
    setShowEditCourier(true);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const activeCouriers = couriers.filter(c => c.is_active).length;
  const pendingOrders = orders.filter(o => o.status === 'pending').length;
  const deliveredOrders = orders.filter(o => o.status === 'delivered').length;
  const inProgressOrders = orders.filter(o => o.status === 'in_progress' || o.status === 'assigned').length;

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
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 truncate">{t.companyDashboard}</h1>
              <p className="text-sm sm:text-base text-gray-600 truncate">{company?.name} • {user.username}</p>
            </div>
          </div>
          <Button onClick={logout} variant="outline" size="sm" className="w-full sm:w-auto">
            <LogOut className="w-4 h-4 mr-2" />
            {t.logout}
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-3 sm:p-6">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.activeCouriers}</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">{activeCouriers}</p>
                </div>
                <Users className="w-5 h-5 sm:w-6 sm:w-8 text-orange-600 flex-shrink-0" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-3 sm:p-6">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.pending}</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">{pendingOrders}</p>
                </div>
                <Clock className="w-5 h-5 sm:w-6 sm:w-8 text-blue-600 flex-shrink-0" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-3 sm:p-6">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.inProgress}</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">{inProgressOrders}</p>
                </div>
                <Truck className="w-5 h-5 sm:w-6 sm:w-8 text-amber-600 flex-shrink-0" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white shadow-sm border-0">
            <CardContent className="p-3 sm:p-6">
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{t.delivered}</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">{deliveredOrders}</p>
                </div>
                <CheckCircle className="w-5 h-5 sm:w-6 sm:w-8 text-green-600 flex-shrink-0" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs Navigation */}
        <div className="flex flex-col sm:flex-row space-y-1 sm:space-y-0 sm:space-x-1 mb-6 bg-white p-1 rounded-lg shadow-sm border-0">
          <Button
            variant={activeTab === 'overview' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('overview')}
            className="flex-1 text-xs sm:text-sm"
          >
            {t.overview}
          </Button>
          <Button
            variant={activeTab === 'couriers' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('couriers')}
            className="flex-1 text-xs sm:text-sm"
          >
            {t.courierManagement}
          </Button>
          <Button
            variant={activeTab === 'orders' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('orders')}
            className="flex-1 text-xs sm:text-sm"
          >
            {t.orderManagement}
          </Button>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
            <Card className="bg-white shadow-sm border-0">
              <CardHeader className="p-4 sm:p-6">
                <CardTitle className="text-lg sm:text-xl">{t.recentOrders}</CardTitle>
              </CardHeader>
              <CardContent className="p-4 sm:p-6 pt-0">
                <div className="space-y-3">
                  {orders.slice(0, 5).map((order) => (
                    <div key={order.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div className="min-w-0 flex-1 pr-2">
                        <p className="font-medium text-sm truncate">{order.customer_name}</p>
                        <p className="text-xs text-gray-600 truncate">{order.delivery_address}</p>
                        {order.reference_number && (
                          <p className="text-xs text-gray-500">Rif: {order.reference_number}</p>
                        )}
                      </div>
                      <Badge variant={
                        order.status === 'delivered' ? 'default' : 
                        order.status === 'pending' ? 'secondary' : 'outline'
                      } className="text-xs shrink-0">
                        {order.status === 'delivered' ? t.delivered.toUpperCase() :
                         order.status === 'pending' ? t.pending.toUpperCase() :
                         order.status === 'assigned' ? t.assigned.toUpperCase() : t.inProgress.toUpperCase()}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white shadow-sm border-0">
              <CardHeader className="p-4 sm:p-6">
                <CardTitle className="text-lg sm:text-xl">{t.activeCouriers}</CardTitle>
              </CardHeader>
              <CardContent className="p-4 sm:p-6 pt-0">
                <div className="space-y-3">
                  {couriers.filter(c => c.is_active).slice(0, 5).map((courier) => (
                    <div key={courier.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3 min-w-0 flex-1">
                        <div className="w-6 h-6 sm:w-8 sm:h-8 bg-orange-600 rounded-full flex items-center justify-center flex-shrink-0">
                          <User className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                        </div>
                        <p className="font-medium text-sm truncate">{courier.username}</p>
                      </div>
                      <Badge variant="default" className="text-xs shrink-0">{t.active.toUpperCase()}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === 'couriers' && (
          <Card className="bg-white shadow-sm border-0">
            <CardHeader className="p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
                <div>
                  <CardTitle className="text-lg sm:text-xl">{t.courierManagement}</CardTitle>
                  <CardDescription className="text-sm">{t.manageYourCouriers}</CardDescription>
                </div>
                <Dialog open={showCreateCourier} onOpenChange={setShowCreateCourier}>
                  <DialogTrigger asChild>
                    <Button className="bg-orange-600 hover:bg-orange-700 w-full sm:w-auto text-sm">
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
                        <Label htmlFor="courierUsername" className="text-sm">{t.courierUsername}</Label>
                        <Input
                          id="courierUsername"
                          value={newCourier.username}
                          onChange={(e) => setNewCourier({ ...newCourier, username: e.target.value })}
                          placeholder={t.enterCourierUsername}
                          required
                          className="text-sm"
                        />
                      </div>
                      <div>
                        <Label htmlFor="courierPassword" className="text-sm">{t.courierPassword}</Label>
                        <Input
                          id="courierPassword"
                          type="password"
                          value={newCourier.password}
                          onChange={(e) => setNewCourier({ ...newCourier, password: e.target.value })}
                          placeholder={t.enterCourierPassword}
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
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
                  <p className="text-gray-500 mt-2 text-sm">{t.loading}</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="text-xs sm:text-sm">{t.username}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.status}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.created}</TableHead>
                        <TableHead className="text-xs sm:text-sm">{t.actions}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {couriers.map((courier) => (
                        <TableRow key={courier.id}>
                          <TableCell className="font-medium text-xs sm:text-sm">{courier.username}</TableCell>
                          <TableCell>
                            <Badge variant={courier.is_active ? 'default' : 'destructive'} className="text-xs">
                              {courier.is_active ? t.active : t.blocked}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-xs sm:text-sm">{new Date(courier.created_at).toLocaleDateString()}</TableCell>
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
                                onClick={() => deleteCourier(courier.id)}
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
        )}

        {/* Edit Courier Dialog */}
        <Dialog open={showEditCourier} onOpenChange={setShowEditCourier}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.editCourier}</DialogTitle>
              <DialogDescription className="text-sm">{t.editCourierDescription}</DialogDescription>
            </DialogHeader>
            {editingCourier && (
              <form onSubmit={updateCourier} className="space-y-4">
                <div>
                  <Label htmlFor="editCourierUsername" className="text-sm">{t.courierUsername}</Label>
                  <Input
                    id="editCourierUsername"
                    value={editingCourier.username}
                    onChange={(e) => setEditingCourier({ ...editingCourier, username: e.target.value })}
                    required
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="editCourierPassword" className="text-sm">{t.courierPassword}</Label>
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
                  <Button type="button" variant="outline" onClick={() => setShowEditCourier(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {activeTab === 'orders' && (
          <Card className="bg-white shadow-sm border-0">
            <CardHeader className="p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
                <div>
                  <CardTitle className="text-lg sm:text-xl">{t.orderManagement}</CardTitle>
                  <CardDescription className="text-sm">{t.manageDeliveryOrders}</CardDescription>
                </div>
                <Button 
                  onClick={() => setShowCreateOrder(true)}
                  className="bg-orange-600 hover:bg-orange-700 w-full sm:w-auto text-sm"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  {t.addOrder}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-4 sm:p-6">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
                  <p className="text-gray-500 mt-2 text-sm">{t.loading}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {orders.map((order) => (
                    <div key={order.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex flex-col sm:flex-row justify-between items-start mb-3 space-y-2 sm:space-y-0">
                        <div className="flex-1 min-w-0 pr-0 sm:pr-4">
                          <h3 className="font-semibold text-gray-900 text-sm sm:text-base truncate">{order.customer_name}</h3>
                          <p className="text-gray-600 text-xs sm:text-sm break-words">{order.delivery_address}</p>
                          <p className="text-gray-500 text-xs sm:text-sm">📞 {order.phone_number}</p>
                          {order.reference_number && (
                            <p className="text-gray-500 text-xs sm:text-sm">📋 Rif: {order.reference_number}</p>
                          )}
                          {order.courier_id && (
                            <p className="text-gray-500 text-xs sm:text-sm">
                              Corriere: {couriers.find(c => c.id === order.courier_id)?.username || 'Sconosciuto'}
                            </p>
                          )}
                        </div>
                        <Badge variant={
                          order.status === 'delivered' ? 'default' : 
                          order.status === 'pending' ? 'secondary' : 'outline'
                        } className="text-xs shrink-0">
                          {order.status === 'delivered' ? t.delivered.toUpperCase() :
                           order.status === 'pending' ? t.pending.toUpperCase() :
                           order.status === 'assigned' ? t.assigned.toUpperCase() : t.inProgress.toUpperCase()}
                        </Badge>
                      </div>
                      
                      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
                        <p className="text-xs text-gray-500">
                          {t.createdAt}: {new Date(order.created_at).toLocaleDateString()}
                        </p>
                        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 w-full sm:w-auto">
                          {(order.status === 'pending' || order.status === 'assigned') && (
                            <Button 
                              onClick={() => handleEditClick(order)}
                              size="sm"
                              variant="outline"
                              className="w-full sm:w-auto text-xs"
                            >
                              {t.edit}
                            </Button>
                          )}
                          {order.status === 'pending' && (
                            <Button 
                              onClick={() => handleAssignClick(order)}
                              size="sm"
                              variant="outline"
                              className="w-full sm:w-auto text-xs"
                            >
                              {t.assignCourier}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Create Order Dialog */}
        <Dialog open={showCreateOrder} onOpenChange={setShowCreateOrder}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.createNewOrder}</DialogTitle>
              <DialogDescription className="text-sm">{t.addNewOrderDescription}</DialogDescription>
            </DialogHeader>
            <form onSubmit={createOrder} className="space-y-4">
              <div>
                <Label htmlFor="customerName" className="text-sm">{t.customerName}</Label>
                <Input
                  id="customerName"
                  value={newOrder.customer_name}
                  onChange={(e) => setNewOrder({ ...newOrder, customer_name: e.target.value })}
                  placeholder={t.enterCustomerName}
                  required
                  className="text-sm"
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
                <Label htmlFor="phoneNumber" className="text-sm">{t.phoneNumber}</Label>
                <Input
                  id="phoneNumber"
                  value={newOrder.phone_number}
                  onChange={(e) => setNewOrder({ ...newOrder, phone_number: e.target.value })}
                  placeholder={t.enterPhoneNumber}
                  required
                  className="text-sm"
                />
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

        {/* Edit Order Dialog */}
        <Dialog open={showEditOrder} onOpenChange={setShowEditOrder}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">Modifica Ordine</DialogTitle>
              <DialogDescription className="text-sm">Modifica i dettagli dell'ordine di consegna</DialogDescription>
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
                    value={editingOrder.reference_number}
                    onChange={(e) => setEditingOrder({ ...editingOrder, reference_number: e.target.value })}
                    placeholder={t.enterReferenceNumber}
                    className="text-sm"
                  />
                </div>
                <div className="flex space-x-2">
                  <Button type="submit" className="flex-1 text-sm">Aggiorna Ordine</Button>
                  <Button type="button" variant="outline" onClick={() => setShowEditOrder(false)} className="flex-1 text-sm">
                    {t.cancel}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>

        {/* Assign Order Dialog */}
        <Dialog open={showAssignOrder} onOpenChange={setShowAssignOrder}>
          <DialogContent className="mx-4 sm:mx-0 max-w-sm sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="text-lg">{t.assignOrderToCourier}</DialogTitle>
              <DialogDescription className="text-sm">
                {t.selectCourier} {selectedOrder?.customer_name}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={assignOrder} className="space-y-4">
              <div>
                <Label htmlFor="courierSelect" className="text-sm">Seleziona Corriere</Label>
                <Select 
                  value={assignData.courier_id} 
                  onValueChange={(value) => setAssignData({ ...assignData, courier_id: value })}
                >
                  <SelectTrigger className="text-sm">
                    <SelectValue placeholder={t.chooseCourier} />
                  </SelectTrigger>
                  <SelectContent>
                    {couriers.filter(c => c.is_active).map((courier) => (
                      <SelectItem key={courier.id} value={courier.id} className="text-sm">
                        {courier.username}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" className="w-full text-sm" disabled={!assignData.courier_id}>
                {t.assignOrder}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
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