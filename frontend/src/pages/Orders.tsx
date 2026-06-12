import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { orderService } from '../services/order';
import {
  ShoppingBag,
  Clock,
  CheckCircle2,
  XCircle,
  Truck,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  Info,
  MapPin,
  CreditCard,
  Cpu
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Orders: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'all' | 'active' | 'completed'>('all');
  const [expandedOrderId, setExpandedOrderId] = useState<number | null>(null);
  
  // Return States
  const [returnOrderId, setReturnOrderId] = useState<number | null>(null);
  const [returnReason, setReturnReason] = useState('');
  const [returnLoading, setReturnLoading] = useState(false);

  // Queries
  const { data: orders = [], isLoading: ordersLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: orderService.getOrders
  });

  // Mutations
  const cancelOrderMutation = useMutation({
    mutationFn: (orderId: number) => orderService.cancelOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      alert('Order cancelled successfully.');
    },
    onError: (err: any) => {
      alert(err?.response?.data?.detail || 'Failed to cancel order.');
    }
  });

  const handleReturnSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!returnOrderId || !returnReason.trim()) return;

    setReturnLoading(true);
    try {
      const res = await orderService.returnOrder(returnOrderId, returnReason);
      if (res.success) {
        queryClient.invalidateQueries({ queryKey: ['orders'] });
        alert('Return request submitted successfully.');
        setReturnOrderId(null);
        setReturnReason('');
      }
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to submit return request.');
    } finally {
      setReturnLoading(false);
    }
  };

  // Filter orders based on tabs
  const filteredOrders = orders.filter((o) => {
    if (activeTab === 'active') {
      return ['pending', 'processing', 'shipped'].includes(o.status.toLowerCase());
    }
    if (activeTab === 'completed') {
      return ['delivered', 'cancelled', 'returned'].includes(o.status.toLowerCase());
    }
    return true;
  });

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return <Clock className="h-5 w-5 text-amber-500" />;
      case 'processing':
        return <Cpu className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'shipped':
        return <Truck className="h-5 w-5 text-indigo-500" />;
      case 'delivered':
        return <CheckCircle2 className="h-5 w-5 text-emerald-500" />;
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'returned':
        return <RotateCcw className="h-5 w-5 text-purple-500" />;
      default:
        return <Info className="h-5 w-5 text-slate-500" />;
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-amber-50 border-amber-100 text-amber-700';
      case 'processing':
        return 'bg-blue-50 border-blue-100 text-blue-700';
      case 'shipped':
        return 'bg-indigo-50 border-indigo-100 text-indigo-700';
      case 'delivered':
        return 'bg-emerald-50 border-emerald-100 text-emerald-700';
      case 'cancelled':
        return 'bg-red-50 border-red-100 text-red-700';
      case 'returned':
        return 'bg-purple-50 border-purple-100 text-purple-700';
      default:
        return 'bg-slate-50 border-slate-100 text-slate-700';
    }
  };

  if (ordersLoading) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto px-4 py-8">
        <div className="h-32 skeleton rounded-3xl" />
        <div className="h-32 skeleton rounded-3xl" />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 flex items-center gap-2">
            <ShoppingBag className="h-8 w-8 text-blue-600" />
            My Orders
          </h1>
          <p className="text-sm text-slate-500 mt-1">Track shipping details and order history</p>
        </div>

        {/* Tab Controls */}
        <div className="flex bg-slate-100 p-1 rounded-xl">
          {[
            { id: 'all', label: 'All Orders' },
            { id: 'active', label: 'Active' },
            { id: 'completed', label: 'Completed' }
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

      {filteredOrders.length > 0 ? (
        <div className="space-y-6">
          {filteredOrders.map((order) => {
            const isExpanded = expandedOrderId === order.id;
            return (
              <div
                key={order.id}
                className="rounded-3xl border border-slate-100 bg-white shadow-sm overflow-hidden"
              >
                {/* Accordion Header */}
                <div
                  onClick={() => setExpandedOrderId(isExpanded ? null : order.id)}
                  className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer hover:bg-slate-50/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-xl bg-slate-50 flex items-center justify-center border border-slate-100">
                      {getStatusIcon(order.status)}
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-800 text-sm">Order #{order.id}</h3>
                      <p className="text-[10px] text-slate-400 mt-0.5">Placed on {new Date(order.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    <span className="text-sm font-extrabold text-blue-600">
                      ₹{order.final_amount ? order.final_amount.toLocaleString() : order.total_amount.toLocaleString()}
                    </span>
                    <span className={`px-2.5 py-1 text-[10px] font-bold uppercase rounded-lg border ${getStatusBadgeClass(order.status)}`}>
                      {order.status}
                    </span>
                    {isExpanded ? <ChevronUp className="h-5 w-5 text-slate-400" /> : <ChevronDown className="h-5 w-5 text-slate-400" />}
                  </div>
                </div>

                {/* Accordion Content */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="border-t border-slate-50 px-6 py-6 bg-slate-50/20 space-y-6"
                    >
                      {/* Products list */}
                      <div className="space-y-3">
                        <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wide">Ordered Items</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          {order.items?.map((item) => (
                            <div key={item.id} className="p-4 rounded-2xl border border-slate-100 bg-white flex items-center gap-4">
                              <div className="h-14 w-14 bg-slate-50 border border-slate-100 rounded-xl flex items-center justify-center overflow-hidden flex-shrink-0">
                                {item.product?.image_url ? (
                                  <img src={item.product.image_url} alt={item.product.name} className="object-cover h-full w-full" />
                                ) : (
                                  <Cpu className="h-6 w-6 text-slate-300" />
                                )}
                              </div>
                              <div className="min-w-0">
                                <h5 className="font-bold text-slate-800 text-xs truncate">{item.product?.name || 'Loading Item...'}</h5>
                                <p className="text-[10px] text-slate-400 mt-0.5">Qty: {item.quantity} | Price: ₹{item.price.toLocaleString()}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Delivery specs */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-slate-100/60 text-xs">
                        <div className="space-y-1.5">
                          <span className="font-bold text-slate-400 uppercase tracking-wide text-[9px] flex items-center gap-1">
                            <MapPin className="h-3.5 w-3.5" />
                            Shipping Details
                          </span>
                          <p className="text-slate-700 font-medium leading-relaxed">{order.shipping_address}</p>
                        </div>
                        <div className="space-y-1.5">
                          <span className="font-bold text-slate-400 uppercase tracking-wide text-[9px] flex items-center gap-1">
                            <CreditCard className="h-3.5 w-3.5" />
                            Payment Method
                          </span>
                          <p className="text-slate-700 font-bold">{order.payment_method}</p>
                        </div>
                      </div>

                      {/* Timeline status stepper */}
                      <div className="pt-6 border-t border-slate-100/60">
                        <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wide mb-6">Delivery Timeline</h4>
                        <div className="relative flex flex-col md:flex-row justify-between items-start md:items-center gap-6 md:gap-0">
                          {/* Horizontal line for desktop */}
                          <div className="absolute top-4 left-4 right-4 h-0.5 bg-slate-150 z-0 hidden md:block" />

                          {[
                            { step: 'Order Placed', code: 'pending', desc: 'Awaiting vendor processing' },
                            { step: 'Processing', code: 'processing', desc: 'Verifying inventory' },
                            { step: 'Shipped', code: 'shipped', desc: 'Dispatched to location' },
                            { step: 'Delivered', code: 'delivered', desc: 'Package dropped off' }
                          ].map((step, idx) => {
                            const stepsMap = ['pending', 'processing', 'shipped', 'delivered'];
                            const currentIdx = stepsMap.indexOf(order.status.toLowerCase());
                            const stepIdx = stepsMap.indexOf(step.code);
                            
                            const isCompleted = stepIdx <= currentIdx && order.status.toLowerCase() !== 'cancelled';
                            const isActive = step.code === order.status.toLowerCase();

                            return (
                              <div key={idx} className="flex md:flex-col items-center gap-4 md:gap-2 z-10 md:w-1/4 relative">
                                <div className={`h-8 w-8 rounded-full flex items-center justify-center border font-bold text-xs ${
                                  isCompleted
                                    ? 'bg-blue-600 border-blue-600 text-white shadow-sm'
                                    : 'bg-white border-slate-200 text-slate-400'
                                }`}>
                                  {isCompleted ? '✓' : idx + 1}
                                </div>
                                <div className="text-left md:text-center">
                                  <p className={`text-xs font-bold ${isActive ? 'text-blue-600' : 'text-slate-700'}`}>{step.step}</p>
                                  <p className="text-[9px] text-slate-400 mt-0.5">{step.desc}</p>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      {/* Cancel/Return Buttons */}
                      <div className="flex justify-end gap-3 pt-4 border-t border-slate-100/60">
                        {['pending', 'processing'].includes(order.status.toLowerCase()) && (
                          <button
                            onClick={() => {
                              if (confirm('Cancel this order?')) cancelOrderMutation.mutate(order.id);
                            }}
                            className="px-4 py-2 bg-red-50 hover:bg-red-100 border border-red-100 text-red-600 font-semibold text-xs rounded-xl transition-colors cursor-pointer"
                          >
                            Cancel Order
                          </button>
                        )}
                        {order.status.toLowerCase() === 'delivered' && (
                          <button
                            onClick={() => setReturnOrderId(order.id)}
                            className="px-4 py-2 bg-purple-50 hover:bg-purple-100 border border-purple-100 text-purple-600 font-semibold text-xs rounded-xl transition-colors cursor-pointer"
                          >
                            Return Items
                          </button>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl shadow-sm">
          <ShoppingBag className="h-12 w-12 text-slate-200 mx-auto mb-4" />
          <h2 className="text-lg font-bold text-slate-800">No Orders Placed</h2>
          <p className="text-sm text-slate-400 max-w-xs mx-auto mt-1 leading-relaxed">
            You haven't ordered any premium hardware or components yet.
          </p>
        </div>
      )}

      {/* Return Order Modal */}
      <AnimatePresence>
        {returnOrderId !== null && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 relative overflow-hidden"
            >
              <h3 className="font-extrabold text-slate-800 text-base flex items-center gap-1.5">
                <RotateCcw className="h-5 w-5 text-purple-600 animate-spin" />
                Return Request Order #{returnOrderId}
              </h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Provide details for return review. Suspicious profiles or feedback may be audited by spam classifiers.
              </p>

              <form onSubmit={handleReturnSubmit} className="space-y-4 pt-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Reason for Return</label>
                  <textarea
                    rows={3}
                    placeholder="Provide details about why you are returning this hardware..."
                    value={returnReason}
                    onChange={(e) => setReturnReason(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                    required
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => {
                      setReturnOrderId(null);
                      setReturnReason('');
                    }}
                    className="flex-1 py-2 bg-slate-100 text-slate-600 font-semibold rounded-xl text-xs hover:bg-slate-200 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={returnLoading}
                    className="flex-1 py-2 bg-purple-600 text-white font-semibold rounded-xl text-xs hover:bg-purple-700 transition-colors flex items-center justify-center gap-1.5"
                  >
                    {returnLoading ? (
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    ) : (
                      <>
                        Submit Request
                      </>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Orders;
