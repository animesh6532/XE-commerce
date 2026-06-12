import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { orderService } from '../services/order';
import {
  Settings,
  ShoppingBag,
  Clock,
  CheckCircle2,
  XCircle,
  Truck,
  RotateCcw,
  UserCheck,
  RefreshCw,
  Cpu
} from 'lucide-react';

const Admin: React.FC = () => {
  const queryClient = useQueryClient();

  // Queries
  const { data: allOrders = [], isLoading: ordersLoading } = useQuery({
    queryKey: ['adminAllOrders'],
    queryFn: orderService.getAllOrders
  });

  // Mutations
  const updateStatusMutation = useMutation({
    mutationFn: ({ orderId, status }: { orderId: number; status: string }) =>
      orderService.updateOrderStatus(orderId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminAllOrders'] });
      alert('Order status updated successfully!');
    },
    onError: (err: any) => {
      alert(err?.response?.data?.detail || 'Failed to update order status.');
    }
  });

  const handleStatusChange = (orderId: number, nextStatus: string) => {
    updateStatusMutation.mutate({ orderId, status: nextStatus });
  };

  // Stats
  const pendingCount = allOrders.filter(o => o.status.toLowerCase() === 'pending').length;
  const shippedCount = allOrders.filter(o => o.status.toLowerCase() === 'shipped').length;
  const deliveredCount = allOrders.filter(o => o.status.toLowerCase() === 'delivered').length;
  const totalVal = allOrders.reduce((sum, o) => sum + (o.final_amount || o.total_amount), 0);

  if (ordersLoading) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto px-4 py-8">
        <div className="h-40 skeleton rounded-3xl" />
        <div className="h-60 skeleton rounded-3xl" />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-800 flex items-center gap-2">
          <Settings className="h-8 w-8 text-blue-600 animate-spin" />
          Admin Console
        </h1>
        <p className="text-sm text-slate-500 mt-1">Manage order dispatch and logistics fulfillment status</p>
      </div>

      {/* Overview stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Orders', value: allOrders.length, desc: 'Across all accounts', icon: ShoppingBag, bg: 'bg-blue-50 text-blue-600' },
          { label: 'Pending Dispatch', value: pendingCount, desc: 'Awaiting packing', icon: Clock, bg: 'bg-amber-50 text-amber-600' },
          { label: 'In Transit', value: shippedCount, desc: 'Packages shipped', icon: Truck, bg: 'bg-indigo-50 text-indigo-600' },
          { label: 'Total Volume', value: `₹${Math.round(totalVal).toLocaleString()}`, desc: 'Gross earnings', icon: UserCheck, bg: 'bg-emerald-50 text-emerald-600' }
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

      {/* Orders admin table */}
      <div className="rounded-3xl border border-slate-100 bg-white shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-50">
          <h3 className="font-extrabold text-slate-800 text-sm">Fulfillment Grid</h3>
        </div>

        {allOrders.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-[10px] font-bold text-slate-400 uppercase tracking-wide border-b border-slate-100">
                  <th className="px-6 py-4">ID</th>
                  <th className="px-6 py-4">Customer ID</th>
                  <th className="px-6 py-4">Delivery Address</th>
                  <th className="px-6 py-4">Total Amount</th>
                  <th className="px-6 py-4">Fulfillment Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 text-xs text-slate-700">
                {allOrders.map((ord) => (
                  <tr key={ord.id} className="hover:bg-slate-50/30 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-800">#{ord.id}</td>
                    <td className="px-6 py-4">User {ord.user_id}</td>
                    <td className="px-6 py-4 max-w-[200px] truncate">{ord.shipping_address}</td>
                    <td className="px-6 py-4 font-extrabold text-slate-800">
                      ₹{(ord.final_amount || ord.total_amount).toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      {/* Select input status update */}
                      <select
                        value={ord.status}
                        onChange={(e) => handleStatusChange(ord.id, e.target.value)}
                        disabled={updateStatusMutation.isPending}
                        className={`px-3 py-1.5 border border-slate-200 rounded-lg bg-slate-50 font-bold focus:outline-none focus:ring-2 focus:ring-blue-600 ${
                          ord.status.toLowerCase() === 'delivered'
                            ? 'text-emerald-600 border-emerald-100'
                            : ord.status.toLowerCase() === 'cancelled'
                            ? 'text-red-500 border-red-100'
                            : 'text-slate-700'
                        }`}
                      >
                        <option value="pending">pending</option>
                        <option value="processing">processing</option>
                        <option value="shipped">shipped</option>
                        <option value="delivered">delivered</option>
                        <option value="cancelled">cancelled</option>
                        <option value="returned">returned</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <ShoppingBag className="h-8 w-8 text-slate-200 mx-auto mb-2" />
            <p className="text-xs font-semibold text-slate-400">No active customer orders found.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
