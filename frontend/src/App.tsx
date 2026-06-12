import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetails from './pages/ProductDetails';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Wishlist from './pages/Wishlist';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Admin from './pages/Admin';
import Chatbot from './pages/Chatbot';
import Orders from './pages/Orders';
import MainLayout from './layouts/MainLayout';
import { LoadingScreen } from './components/common/LoadingScreen';

// Protected Route Guard
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isAuthLoading } = useAuth();

  if (isAuthLoading) {
    return <LoadingScreen />;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

// Role Route Guard
const RoleRoute: React.FC<{ children: React.ReactNode; allowedRoles: string[] }> = ({ children, allowedRoles }) => {
  const { isAuthenticated, user, isAuthLoading } = useAuth();

  if (isAuthLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  return allowedRoles.includes(user.role) ? <>{children}</> : <Navigate to="/" replace />;
};

const App: React.FC = () => {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Main App Layout Routes */}
      <Route
        path="/"
        element={
          <MainLayout>
            <Home />
          </MainLayout>
        }
      />
      <Route
        path="/products"
        element={
          <MainLayout>
            <Products />
          </MainLayout>
        }
      />
      <Route
        path="/product/:id"
        element={
          <MainLayout>
            <ProductDetails />
          </MainLayout>
        }
      />

      {/* Protected Customer Routes */}
      <Route
        path="/cart"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Cart />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/checkout"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Checkout />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/wishlist"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Wishlist />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/orders"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Orders />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/chatbot"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Chatbot />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      {/* Protected Seller/Admin Routes */}
      <Route
        path="/dashboard"
        element={
          <RoleRoute allowedRoles={['seller', 'admin']}>
            <MainLayout>
              <Dashboard />
            </MainLayout>
          </RoleRoute>
        }
      />
      <Route
        path="/analytics"
        element={
          <RoleRoute allowedRoles={['seller', 'admin']}>
            <MainLayout>
              <Analytics />
            </MainLayout>
          </RoleRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <RoleRoute allowedRoles={['admin']}>
            <MainLayout>
              <Admin />
            </MainLayout>
          </RoleRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
