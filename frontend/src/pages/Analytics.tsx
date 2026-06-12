import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '../services/analytics';
import {
  Sparkles,
  TrendingUp,
  Cpu,
  BarChart3,
  Calendar,
  Globe,
  ExternalLink
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const Analytics: React.FC = () => {
  // Queries
  const { data: monthlySales = [], isLoading: monthlyLoading } = useQuery({
    queryKey: ['monthlySales'],
    queryFn: analyticsService.getMonthlySales
  });

  const { data: categoryAnalytics = [], isLoading: categoryLoading } = useQuery({
    queryKey: ['categoryAnalytics'],
    queryFn: analyticsService.getCategoryAnalytics
  });

  const { data: demandForecast = [], isLoading: demandLoading } = useQuery({
    queryKey: ['demandForecast'],
    queryFn: analyticsService.getDemandForecast
  });

  const COLORS = ['#2563EB', '#7C3AED', '#06B6D4', '#10B981', '#F59E0B', '#EF4444'];

  const loading = monthlyLoading || categoryLoading || demandLoading;

  if (loading) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto px-4 py-8">
        <div className="h-60 skeleton rounded-3xl" />
        <div className="h-60 skeleton rounded-3xl" />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 flex items-center gap-2">
            <BarChart3 className="h-8 w-8 text-blue-600" />
            Analytics Center
          </h1>
          <p className="text-sm text-slate-500 mt-1">Deep analysis of ML pipeline predictions and store demand</p>
        </div>

        {/* External Link to Plotly */}
        <a
          href="http://localhost:8000/api/chatbot/analytics/dashboard"
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2.5 bg-slate-900 text-white font-semibold rounded-xl text-xs hover:bg-slate-800 transition-all flex items-center gap-1.5 cursor-pointer"
        >
          Open Plotly Dashboard
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>

      {/* Chart Row 1: Sales forecasting (Area) + Category metrics (Pie) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Sales Forecast */}
        <div className="lg:col-span-2 p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
          <div>
            <h3 className="font-extrabold text-slate-800 text-sm flex items-center gap-1">
              <TrendingUp className="h-4.5 w-4.5 text-blue-600" />
              Monthly Sales Trends
            </h3>
            <p className="text-[10px] text-slate-400">Revenues and transaction values over the past months</p>
          </div>

          <div className="h-64 w-full pt-4">
            {monthlySales.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={monthlySales} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="month" stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${v}`} />
                  <Tooltip formatter={(v: any) => [`₹${parseFloat(v).toLocaleString()}`, 'Monthly Sales']} />
                  <Area type="monotone" dataKey="revenue" stroke="#2563EB" strokeWidth={3} fillOpacity={1} fill="url(#colorSales)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-xs text-slate-400 text-center py-12">No monthly sales metrics found.</p>
            )}
          </div>
        </div>

        {/* Category distribution */}
        <div className="lg:col-span-1 p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-slate-800 text-sm flex items-center gap-1">
              <Cpu className="h-4.5 w-4.5 text-purple-600" />
              Category Spread
            </h3>
            <p className="text-[10px] text-slate-400">Total items sold by category</p>
          </div>

          <div className="h-56 w-full flex items-center justify-center pt-2">
            {categoryAnalytics.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryAnalytics}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="total_sales"
                    nameKey="category"
                  >
                    {categoryAnalytics.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-xs text-slate-400 text-center py-12">No category data.</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500 font-bold border-t border-slate-50 pt-3">
            {categoryAnalytics.slice(0, 4).map((entry, index) => (
              <div key={index} className="flex items-center gap-1.5 truncate">
                <div className="h-2 w-2 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                <span>{entry.category}: {entry.total_sales} sold</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Chart Row 2: Random forest next 7 days demand forecast */}
      <div className="grid grid-cols-1 gap-8">
        <div className="p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
          <div>
            <h3 className="font-extrabold text-slate-800 text-sm flex items-center gap-1.5">
              <Calendar className="h-4.5 w-4.5 text-blue-600" />
              AI Demand Forecast (Random Forest Model)
            </h3>
            <p className="text-[10px] text-slate-400">Predictive daily order counts for the next 7 days</p>
          </div>

          <div className="h-72 w-full pt-4">
            {demandForecast.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={demandForecast} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="day" stroke="#94A3B8" fontSize={10} tickLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip formatter={(v: any) => [v, 'Predicted Orders']} />
                  <Bar dataKey="orders" fill="#7C3AED" radius={[8, 8, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-xs text-slate-400 text-center py-12">No demand forecasts found.</p>
            )}
          </div>
        </div>
      </div>

    </div>
  );
};

export default Analytics;
