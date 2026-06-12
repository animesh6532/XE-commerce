import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { wishlistService } from '../services/wishlist';
import {
  Heart,
  ShoppingBag,
  Trash2,
  Bookmark,
  TrendingDown,
  Sparkles,
  RefreshCw,
  Info,
  DollarSign,
  Cpu
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const Wishlist: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'board' | 'alerts' | 'analytics'>('board');

  // Queries
  const { data: wishlist = [], isLoading: wishlistLoading } = useQuery({
    queryKey: ['wishlist'],
    queryFn: wishlistService.getWishlist
  });

  const { data: priceAlerts = [] } = useQuery({
    queryKey: ['priceAlerts'],
    queryFn: wishlistService.getPriceAlerts,
    enabled: activeTab === 'alerts'
  });

  const { data: dealTracking = [] } = useQuery({
    queryKey: ['dealTracking'],
    queryFn: wishlistService.getDealTracking,
    enabled: activeTab === 'board'
  });

  const { data: analytics } = useQuery({
    queryKey: ['wishlistAnalytics'],
    queryFn: wishlistService.getWishlistAnalytics,
    enabled: activeTab === 'analytics'
  });

  const { data: recs = [] } = useQuery({
    queryKey: ['wishlistRecs'],
    queryFn: wishlistService.getWishlistRecommendations,
    enabled: wishlist.length > 0
  });

  // Mutations
  const removeMutation = useMutation({
    mutationFn: (productId: number) => wishlistService.removeFromWishlist(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
      queryClient.invalidateQueries({ queryKey: ['wishlistAnalytics'] });
    }
  });

  const moveToCartMutation = useMutation({
    mutationFn: (productId: number) => wishlistService.moveToCart(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['wishlistAnalytics'] });
      alert('Product moved to shopping cart!');
    }
  });

  const clearMutation = useMutation({
    mutationFn: () => wishlistService.clearWishlist(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
      queryClient.invalidateQueries({ queryKey: ['wishlistAnalytics'] });
      alert('Wishlist cleared.');
    }
  });

  // Analytics Chart Formatting
  const COLORS = ['#2563EB', '#7C3AED', '#06B6D4', '#10B981', '#F59E0B', '#EF4444'];
  const chartData = analytics?.category_distribution
    ? Object.keys(analytics.category_distribution).map((key) => ({
        name: key,
        value: analytics.category_distribution[key],
      }))
    : [];

  if (wishlistLoading) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto px-4 py-8">
        <div className="h-60 skeleton rounded-3xl" />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 flex items-center gap-2">
            <Heart className="h-8 w-8 text-red-500 fill-red-500" />
            Wishlist Board
          </h1>
          <p className="text-sm text-slate-500 mt-1">Configure drop alerts and review visual distribution</p>
        </div>

        {/* Tab Selection */}
        <div className="flex bg-slate-100 p-1 rounded-xl">
          {[
            { id: 'board', label: 'My Saved Items' },
            { id: 'alerts', label: 'Price Alerts' },
            { id: 'analytics', label: 'Analytics' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`text-xs font-semibold px-4 py-2 rounded-lg transition-all ${
                activeTab === tab.id
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {wishlist.length > 0 ? (
        <div className="space-y-8">
          
          {/* Board View */}
          {activeTab === 'board' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Board grid list */}
              <div className="lg:col-span-2 space-y-4">
                {wishlist.map((item) => {
                  // Check if there is an AI deal score for this item
                  const deal = dealTracking?.find(d => d.product_id === item.product_id);
                  return (
                    <div
                      key={item.id}
                      className="p-5 rounded-2xl border border-slate-100 bg-white shadow-sm flex flex-col sm:flex-row gap-5 items-center justify-between"
                    >
                      <div className="flex gap-4 items-center w-full sm:w-auto">
                        <div className="h-20 w-20 bg-slate-50 border border-slate-100 rounded-xl flex items-center justify-center overflow-hidden flex-shrink-0">
                          {item.product?.image_url ? (
                            <img src={item.product.image_url} alt={item.product.name} className="object-cover h-full w-full" />
                          ) : (
                            <Cpu className="h-8 w-8 text-slate-300" />
                          )}
                        </div>
                        <div className="min-w-0">
                          <h3
                            onClick={() => navigate(`/product/${item.product_id}`)}
                            className="font-bold text-slate-800 text-sm line-clamp-1 hover:text-blue-600 transition-colors cursor-pointer"
                          >
                            {item.product?.name}
                          </h3>
                          <p className="text-[10px] font-bold text-slate-400 mt-0.5">{item.product?.brand}</p>
                          <p className="text-sm font-extrabold text-slate-800 mt-2">₹{item.product?.price.toLocaleString()}</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between sm:justify-end gap-4 w-full sm:w-auto">
                        {/* Deal score badge */}
                        {deal && deal.discount_percentage > 0 && (
                          <span className="px-2.5 py-1 bg-amber-50 border border-amber-100 text-amber-700 text-[10px] font-bold uppercase rounded-lg flex items-center gap-1">
                            <TrendingDown className="h-3 w-3" />
                            {deal.discount_percentage}% OFF
                          </span>
                        )}
                        
                        <div className="flex gap-2 text-slate-400">
                          <button
                            onClick={() => moveToCartMutation.mutate(item.product_id)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-semibold hover:bg-blue-700 transition-colors flex items-center gap-1 cursor-pointer"
                          >
                            <ShoppingBag className="h-3.5 w-3.5" />
                            Move
                          </button>
                          <button
                            onClick={() => removeMutation.mutate(item.product_id)}
                            className="p-2 border border-slate-200 rounded-xl hover:text-red-500 hover:border-red-200 transition-colors"
                            title="Remove"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}

                <div className="flex justify-end">
                  <button
                    onClick={() => {
                      if (confirm('Clear your entire wishlist?')) clearMutation.mutate();
                    }}
                    className="text-xs font-bold text-red-500 hover:text-red-600 flex items-center gap-1.5 uppercase tracking-wider cursor-pointer"
                  >
                    <Trash2 className="h-4 w-4" />
                    Clear Board
                  </button>
                </div>
              </div>

              {/* Sidebar recommendations */}
              {recs.length > 0 && (
                <div className="lg:col-span-1 p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
                  <h3 className="font-extrabold text-slate-800 text-sm flex items-center gap-1">
                    <Sparkles className="h-4 w-4 text-blue-600 animate-spin" />
                    AI Recommendations
                  </h3>
                  <p className="text-[10px] text-slate-400">Based on items currently saved on your board</p>
                  
                  <div className="divide-y divide-slate-50">
                    {recs.slice(0, 3).map((prod) => (
                      <div
                        key={prod.id}
                        onClick={() => navigate(`/product/${prod.id}`)}
                        className="py-3.5 flex gap-3 items-center hover:bg-slate-50 rounded-xl px-1.5 transition-colors cursor-pointer"
                      >
                        <div className="h-10 w-10 bg-slate-50 rounded-lg flex items-center justify-center overflow-hidden flex-shrink-0 border border-slate-50">
                          {prod.image_url ? (
                            <img src={prod.image_url} alt={prod.name} className="object-cover h-full w-full" />
                          ) : (
                            <Cpu className="h-5 w-5 text-slate-300" />
                          )}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="font-bold text-slate-800 text-xs truncate">{prod.name}</p>
                          <p className="text-[10px] font-extrabold text-blue-600 mt-0.5">₹{prod.price.toLocaleString()}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Price Alerts log */}
          {activeTab === 'alerts' && (
            <div className="max-w-2xl mx-auto space-y-4">
              <h3 className="font-extrabold text-slate-800 text-sm">Price Drop Logs</h3>
              {priceAlerts.length > 0 ? (
                priceAlerts.map((alert, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-2xl border border-blue-100 bg-blue-50/20 text-blue-800 flex items-start gap-3 shadow-sm"
                  >
                    <TrendingDown className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-bold text-xs text-slate-800">
                        {alert.name} price fell by ₹{alert.price_drop}!
                      </h4>
                      <p className="text-[10px] text-slate-400 mt-1">
                        Old price was ₹{alert.old_price.toLocaleString()} | New price is ₹{alert.new_price.toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center bg-slate-50 border border-dashed border-slate-200 rounded-2xl">
                  <TrendingDown className="h-8 w-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-xs font-semibold text-slate-500">No price changes detected recently.</p>
                </div>
              )}
            </div>
          )}

          {/* Analytics Radar / Pie chart */}
          {activeTab === 'analytics' && analytics && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center max-w-4xl mx-auto">
              {/* Details */}
              <div className="p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
                <h3 className="font-extrabold text-slate-800 text-sm">Wishlist Analytics</h3>
                
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100/50">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Average Price</span>
                    <p className="text-lg font-black text-slate-800 mt-1">₹{Math.round(analytics.average_price).toLocaleString()}</p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100/50">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Total Value</span>
                    <p className="text-lg font-black text-blue-600 mt-1">₹{analytics.total_value.toLocaleString()}</p>
                  </div>
                </div>

                <div className="p-4 bg-emerald-50 border border-emerald-100 text-emerald-800 rounded-2xl flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  <div>
                    <span className="text-[9px] font-bold text-emerald-600 uppercase">Potential Savings</span>
                    <p className="text-xs font-extrabold mt-0.5">Save up to ₹{analytics.potential_savings.toLocaleString()} using AI Deals</p>
                  </div>
                </div>
              </div>

              {/* Chart */}
              <div className="h-64 w-full bg-white border border-slate-100 rounded-3xl p-6 shadow-sm flex flex-col items-center justify-center">
                <p className="text-xs font-bold text-slate-800 self-start mb-2">Category Distribution</p>
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend verticalAlign="bottom" height={36} iconSize={10} fontSize={10} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-xs text-slate-400">Loading chart data...</p>
                )}
              </div>
            </div>
          )}

        </div>
      ) : (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl shadow-sm">
          <Heart className="h-12 w-12 text-slate-200 mx-auto mb-4" />
          <h2 className="text-lg font-bold text-slate-800">Your Wishlist Board is Empty</h2>
          <p className="text-sm text-slate-400 max-w-xs mx-auto mt-1 leading-relaxed">
            Click on the heart icon when browsing products to populate this analytics dashboard.
          </p>
        </div>
      )}
    </div>
  );
};

export default Wishlist;
