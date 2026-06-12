import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useQuery } from '@tanstack/react-query';
import { cartService } from '../services/cart';
import { wishlistService } from '../services/wishlist';
import { searchService } from '../services/search';
import {
  ShoppingBag,
  Heart,
  User,
  LogOut,
  Search,
  MessageSquareCode,
  LayoutDashboard,
  Settings,
  Menu,
  X,
  Sparkles,
  ChevronDown
} from 'lucide-react';

const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Cart query
  const { data: cartItems = [] } = useQuery({
    queryKey: ['cart'],
    queryFn: cartService.getCart,
    enabled: isAuthenticated
  });

  // Wishlist query
  const { data: wishlistItems = [] } = useQuery({
    queryKey: ['wishlist'],
    queryFn: wishlistService.getWishlist,
    enabled: isAuthenticated
  });

  // Auto-complete suggestion query handler
  const handleSearchChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearchQuery(val);
    if (val.trim().length > 1) {
      try {
        const data = await searchService.getAutocomplete(val);
        setSuggestions(data.slice(0, 5));
        setShowSuggestions(true);
      } catch {
        setSuggestions([]);
      }
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setShowSuggestions(false);
      navigate(`/products?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleSuggestionClick = (sug: string) => {
    setSearchQuery(sug);
    setShowSuggestions(false);
    navigate(`/products?q=${encodeURIComponent(sug)}`);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-blue-600 selection:text-white">
      {/* Sticky Header */}
      <header className="sticky top-0 z-40 w-full glass shadow-sm transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-4">
            
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <Sparkles className="h-6 w-6 text-blue-600 animate-pulse" />
                <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  XE-Commerce
                </span>
              </Link>
            </div>

            {/* Search Bar */}
            <div className="hidden md:flex flex-1 max-w-md relative">
              <form onSubmit={handleSearchSubmit} className="w-full relative">
                <div className="relative w-full">
                  <input
                    type="text"
                    placeholder="Search premium electronics, brands..."
                    value={searchQuery}
                    onChange={handleSearchChange}
                    onFocus={() => setShowSuggestions(true)}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                    className="w-full px-4 py-2 pl-10 pr-4 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent bg-white/50 text-sm transition-all"
                  />
                  <Search className="absolute left-3 top-2.5 h-4.5 w-4.5 text-slate-400" />
                </div>
              </form>

              {/* Search Suggestions */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute top-11 left-0 right-0 bg-white border border-slate-100 rounded-xl shadow-xl z-50 overflow-hidden divide-y divide-slate-50">
                  {suggestions.map((sug, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(sug)}
                      className="w-full text-left px-4 py-2.5 text-sm hover:bg-slate-50 text-slate-700 flex items-center gap-2"
                    >
                      <Search className="h-3.5 w-3.5 text-slate-400" />
                      {sug}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Right Navigation Controls */}
            <nav className="hidden md:flex items-center space-x-6">
              <Link
                to="/products"
                className={`text-sm font-medium hover:text-blue-600 transition-colors ${
                  location.pathname === '/products' ? 'text-blue-600' : 'text-slate-600'
                }`}
              >
                Products
              </Link>
              <Link
                to="/chatbot"
                className={`text-sm font-medium hover:text-blue-600 flex items-center gap-1.5 transition-colors ${
                  location.pathname === '/chatbot' ? 'text-blue-600' : 'text-slate-600'
                }`}
              >
                <MessageSquareCode className="h-4 w-4" />
                AI Assistant
              </Link>

              {/* Wishlist */}
              {isAuthenticated && (
                <Link to="/wishlist" className="relative p-1 text-slate-600 hover:text-blue-600 transition-colors">
                  <Heart className="h-5.5 w-5.5" />
                  {wishlistItems.length > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full text-[10px] font-bold h-4 w-4 flex items-center justify-center">
                      {wishlistItems.length}
                    </span>
                  )}
                </Link>
              )}

              {/* Cart */}
              {isAuthenticated && (
                <Link to="/cart" className="relative p-1 text-slate-600 hover:text-blue-600 transition-colors">
                  <ShoppingBag className="h-5.5 w-5.5" />
                  {cartItems.length > 0 && (
                    <span className="absolute -top-1 -right-1 bg-blue-600 text-white rounded-full text-[10px] font-bold h-4 w-4 flex items-center justify-center">
                      {cartItems.length}
                    </span>
                  )}
                </Link>
              )}

              {/* User Dropdown */}
              {isAuthenticated && user ? (
                <div className="relative">
                  <button
                    onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                    onBlur={() => setTimeout(() => setProfileDropdownOpen(false), 200)}
                    className="flex items-center space-x-1.5 text-sm font-medium text-slate-700 hover:text-blue-600 focus:outline-none transition-colors"
                  >
                    <div className="h-7 w-7 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-xs uppercase border border-blue-200">
                      {user.username ? user.username.substring(0, 2) : 'US'}
                    </div>
                    <span className="max-w-[100px] truncate">{user.username}</span>
                    <ChevronDown className="h-4 w-4" />
                  </button>

                  {profileDropdownOpen && (
                    <div className="absolute right-0 mt-2.5 w-56 bg-white border border-slate-100 rounded-xl shadow-xl py-1.5 z-50 divide-y divide-slate-100">
                      <div className="px-4 py-2.5">
                        <p className="text-xs text-slate-400">Signed in as</p>
                        <p className="text-sm font-semibold text-slate-800 truncate">{user.email}</p>
                        <span className="inline-block mt-1 px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-blue-50 text-blue-600 border border-blue-100">
                          {user.role}
                        </span>
                      </div>

                      <div className="py-1">
                        {/* Custom Role navigation */}
                        {user.role === 'admin' && (
                          <Link to="/admin" className="flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 gap-2">
                            <Settings className="h-4 w-4 text-slate-400" />
                            Admin Panel
                          </Link>
                        )}
                        {(user.role === 'seller' || user.role === 'admin') && (
                          <>
                            <Link to="/dashboard" className="flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 gap-2">
                              <LayoutDashboard className="h-4 w-4 text-slate-400" />
                              Seller Dashboard
                            </Link>
                            <Link to="/analytics" className="flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 gap-2">
                              <Sparkles className="h-4 w-4 text-slate-400" />
                              Analytics Overview
                            </Link>
                          </>
                        )}
                        <Link to="/orders" className="flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 gap-2">
                          <ShoppingBag className="h-4 w-4 text-slate-400" />
                          My Orders
                        </Link>
                        <Link to="/wishlist" className="flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 gap-2">
                          <Heart className="h-4 w-4 text-slate-400" />
                          My Wishlist
                        </Link>
                      </div>

                      <div className="py-1">
                        <button
                          onClick={logout}
                          className="w-full text-left flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 gap-2"
                        >
                          <LogOut className="h-4 w-4" />
                          Log Out
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center space-x-3">
                  <Link
                    to="/login"
                    className="text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    className="text-sm font-medium px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 shadow-sm transition-all"
                  >
                    Sign Up
                  </Link>
                </div>
              )}
            </nav>

            {/* Mobile Menu Icon */}
            <div className="flex items-center md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-slate-600 p-1 hover:text-blue-600 focus:outline-none"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>

          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-100 bg-white/95 backdrop-blur-md px-4 pt-2 pb-6 space-y-3">
            {/* Search Input for Mobile */}
            <form onSubmit={handleSearchSubmit} className="relative w-full py-1">
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-full px-4 py-2 pl-10 rounded-xl border border-slate-200 bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
              <Search className="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
            </form>

            <Link
              to="/products"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-base font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600"
            >
              Products
            </Link>
            <Link
              to="/chatbot"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-base font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600"
            >
              AI Assistant
            </Link>

            {isAuthenticated ? (
              <>
                <Link
                  to="/wishlist"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-3 py-2 rounded-xl text-base font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600"
                >
                  My Wishlist ({wishlistItems.length})
                </Link>
                <Link
                  to="/cart"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-3 py-2 rounded-xl text-base font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600"
                >
                  My Cart ({cartItems.length})
                </Link>
                <Link
                  to="/orders"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-3 py-2 rounded-xl text-base font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600"
                >
                  My Orders
                </Link>

                {/* Role Specific */}
                {(user?.role === 'seller' || user?.role === 'admin') && (
                  <>
                    <Link
                      to="/dashboard"
                      onClick={() => setMobileMenuOpen(false)}
                      className="block px-3 py-2 rounded-xl text-base font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600"
                    >
                      Seller Dashboard
                    </Link>
                    <Link
                      to="/analytics"
                      onClick={() => setMobileMenuOpen(false)}
                      className="block px-3 py-2 rounded-xl text-base font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600"
                    >
                      Analytics Center
                    </Link>
                  </>
                )}
                {user?.role === 'admin' && (
                  <Link
                    to="/admin"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-xl text-base font-medium text-slate-700 hover:bg-slate-50 hover:text-blue-600"
                  >
                    Admin Control
                  </Link>
                )}

                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    logout();
                  }}
                  className="w-full text-left block px-3 py-2 rounded-xl text-base font-medium text-red-600 hover:bg-red-50"
                >
                  Log Out
                </button>
              </>
            ) : (
              <div className="grid grid-cols-2 gap-2 pt-2">
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2.5 rounded-xl border border-slate-200 text-slate-700 font-medium text-sm hover:bg-slate-50"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center py-2.5 rounded-xl bg-blue-600 text-white font-medium text-sm hover:bg-blue-700 shadow-sm"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-100 py-12 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center sm:text-left">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2 space-y-3">
              <div className="flex items-center justify-center sm:justify-start space-x-2">
                <Sparkles className="h-5 w-5 text-blue-600" />
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  XE-Commerce Platform
                </span>
              </div>
              <p className="text-sm text-slate-400 max-w-xs leading-relaxed">
                Reinventing online retail with integrated predictive models, sentiment tags, and live RAG conversational shopping.
              </p>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-3">AI Platforms</h4>
              <ul className="space-y-2 text-sm text-slate-500">
                <li><Link to="/chatbot" className="hover:text-blue-600 transition-colors">Shopping Chatbot</Link></li>
                <li><Link to="/products" className="hover:text-blue-600 transition-colors">Semantic & Image Search</Link></li>
                <li><span className="text-slate-400">Price Prediction Engines</span></li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-3">Accounts</h4>
              <ul className="space-y-2 text-sm text-slate-500">
                <li><Link to="/orders" className="hover:text-blue-600 transition-colors">Purchases Timeline</Link></li>
                <li><Link to="/wishlist" className="hover:text-blue-600 transition-colors">Saved Wishlist</Link></li>
                <li><Link to="/dashboard" className="hover:text-blue-600 transition-colors">Seller Console</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-100 mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
            <p>&copy; {new Date().getFullYear()} XE-Commerce AI Platform. All rights reserved.</p>
            <div className="flex space-x-4">
              <span>Privacy Policy</span>
              <span>Terms of Service</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;
