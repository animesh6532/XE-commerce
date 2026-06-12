import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../services/analytics';
import { orderService } from '../services/order';
import { productService } from '../services/product';
import {
  LayoutDashboard,
  DollarSign,
  ShoppingBag,
  Cpu,
  Users,
  AlertTriangle,
  ChevronRight,
  TrendingUp,
  Clock
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // Queries
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['dashboardOverview'],
    queryFn: analyticsService.getDashboardOverview
  });

  const { data: recentOrders = [], isLoading: ordersLoading } = useQuery({
    queryKey: ['recentOrders'],
    queryFn: orderService.getRecentOrders
  });

  const { data: inventory, isLoading: inventoryLoading } = useQuery({
    queryKey: ['inventoryStatus'],
    queryFn: productService.getInventoryStatus
  });

  if (overviewLoading || ordersLoading || inventoryLoading) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto px-4 py-8">
        <div className="h-40 skeleton rounded-3xl" />
        <div className="h-60 skeleton rounded-3xl" />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 flex items-center gap-2">
            <LayoutDashboard className="h-8 w-8 text-blue-600" />
            Seller Portal
          </h1>
          <p className="text-sm text-slate-500 mt-1">Real-time summaries of store inventory and revenues</p>
        </div>
        <Link
          to="/analytics"
          className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-semibold hover:bg-blue-700 shadow-sm transition-all flex items-center gap-1 cursor-pointer"
        >
          View Advanced Analytics
          <ChevronRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Metrics Cards */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Store Revenue', value: `₹${Math.round(overview.total_revenue).toLocaleString()}`, desc: 'Gross earnings value', icon: DollarSign, bg: 'bg-emerald-50 text-emerald-600' },
            { label: 'Completed Orders', value: overview.total_orders, desc: 'Successful orders', icon: ShoppingBag, bg: 'bg-blue-50 text-blue-600' },
            { label: 'Active Catalog', value: overview.total_products, desc: 'Products in inventory', icon: Cpu, bg: 'bg-purple-50 text-purple-600' },
            { label: 'Registered Customers', value: overview.total_users, desc: 'Active shopper profiles', icon: Users, bg: 'bg-cyan-50 text-cyan-600' }
          ].map((card, idx) => (
            <div key={idx} className="p-5 rounded-2xl bg-white border border-slate-100 shadow-sm space-y-3">
              <div className="flex justify-between items-start">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">{card.label}</span>
                <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${card.bg}`}>
                  <card.icon className="h-4.5 w-4.5" />
                </div>
              </div>
              <div>
                <p className="text-2xl font-black text-slate-800">{card.value}</p>
                <p className="text-[9px] text-slate-400 font-semibold mt-0.5">{card.desc}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail grid: Recent Orders + Inventory warnings */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Recent Orders List */}
        <div className="lg:col-span-2 p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-slate-50">
            <h3 className="font-extrabold text-slate-800 text-sm flex items-center gap-1.5">
              <Clock className="h-4.5 w-4.5 text-blue-600" />
              Recent Transactions
            </h3>
            <Link to="/orders" className="text-xs font-semibold text-blue-600 hover:text-blue-700">
              View History
            </Link>
          </div>

          {recentOrders.length > 0 ? (
            <div className="divide-y divide-slate-50">
              {recentOrders.slice(0, 4).map((ord) => (
                <div key={ord.id} className="py-3.5 flex justify-between items-center text-xs">
                  <div>
                    <span className="font-bold text-slate-850">Order #{ord.id}</span>
                    <p className="text-[10px] text-slate-400 mt-0.5">{new Date(ord.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="text-right">
                    <span className="font-extrabold text-slate-800">
                      ₹{(ord.final_amount || ord.total_amount).toLocaleString()}
                    </span>
                    <span className="block mt-0.5 text-[9px] font-bold uppercase text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100/30">
                      {ord.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 text-center py-8">No recent orders found.</p>
          )}
        </div>

        {/* Low Stock Alerts */}
        <div className="lg:col-span-1 p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
          <h3 className="font-extrabold text-slate-800 text-sm flex items-center gap-1.5">
            <AlertTriangle className="h-4.5 w-4.5 text-red-500" />
            Inventory Alerts
          </h3>
          <p className="text-[10px] text-slate-400">Products with stock quantities falling under critical levels (less than 10)</p>
          
          {inventory && inventory.low_stock_count > 0 ? (
            <div className="space-y-3.5 max-h-60 overflow-y-auto pr-1">
              {inventory.low_stock_items.map((item) => (
                <div key={item.id} className="p-3 bg-red-50/20 border border-red-100 text-red-800 rounded-xl flex items-center justify-between text-xs font-semibold">
                  <span className="truncate max-w-[140px] text-slate-800">{item.name}</span>
                  <span className="text-red-600 bg-red-50 px-2 py-0.5 rounded border border-red-100/50">
                    {item.stock} left
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 text-center bg-slate-50/50 rounded-2xl border border-dashed border-slate-200">
              <TrendingUp className="h-8 w-8 text-slate-300 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-500">All inventory items healthy!</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
