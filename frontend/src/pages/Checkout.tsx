import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cartService } from '../services/cart';
import { orderService } from '../services/order';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  CreditCard,
  MapPin,
  ShoppingBag,
  ArrowRight,
  ChevronLeft,
  Cpu,
  ShieldCheck
} from 'lucide-react';
import { motion } from 'framer-motion';

const checkoutSchema = z.object({
  shipping_address: z.string().min(10, 'Please enter a complete shipping address (min 10 characters)'),
  payment_method: z.string().min(1, 'Please select a payment method'),
});

type CheckoutFormValues = z.infer<typeof checkoutSchema>;

const Checkout: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [placeError, setPlaceError] = useState<string | null>(null);

  // Queries
  const { data: cartItems = [], isLoading: cartLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: cartService.getCart
  });

  const { data: summary } = useQuery({
    queryKey: ['cartSummary'],
    queryFn: cartService.getSummary,
    enabled: cartItems.length > 0
  });

  const { register, handleSubmit, formState: { errors } } = useForm<CheckoutFormValues>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: { payment_method: 'Credit Card' }
  });

  // Mutations
  const placeOrderMutation = useMutation({
    mutationFn: (payload: CheckoutFormValues) => orderService.placeOrder(payload),
    onSuccess: () => {
      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      queryClient.invalidateQueries({ queryKey: ['cartSummary'] });
      alert('Order placed successfully!');
      navigate('/orders');
    },
    onError: (err: any) => {
      setPlaceError(err?.response?.data?.detail || 'Failed to place order. Try again.');
    }
  });

  const activeItems = cartItems.filter(item => !item.saved_for_later);

  if (cartLoading) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto px-4 py-8">
        <div className="h-60 skeleton rounded-3xl" />
      </div>
    );
  }

  if (activeItems.length === 0) {
    return (
      <div className="text-center py-16">
        <ShoppingBag className="h-12 w-12 text-slate-200 mx-auto mb-4" />
        <h2 className="text-lg font-bold text-slate-800">Your Cart is Empty</h2>
        <p className="text-sm text-slate-400 mt-1">Please add items to cart before checking out.</p>
        <Link to="/products" className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold">
          <ChevronLeft className="h-4 w-4" />
          Browse Products
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-800 flex items-center gap-2">
          <ShieldCheck className="h-8 w-8 text-blue-600" />
          Secure Checkout
        </h1>
        <p className="text-sm text-slate-500 mt-1">Configure shipping and finalize your transaction</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Form: Address and payment */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-3xl border border-slate-100 bg-white shadow-sm">
            <form onSubmit={handleSubmit((data) => placeOrderMutation.mutate(data))} className="space-y-6">
              {placeError && (
                <div className="p-3.5 bg-red-50 text-red-600 rounded-xl text-xs font-semibold">
                  {placeError}
                </div>
              )}

              {/* Shipping address */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide flex items-center gap-1.5">
                  <MapPin className="h-4 w-4 text-blue-600" />
                  Delivery Shipping Address
                </label>
                <textarea
                  rows={4}
                  placeholder="Street Address, City, State, ZIP Code..."
                  {...register('shipping_address')}
                  className={`w-full px-3 py-2 border rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 ${
                    errors.shipping_address ? 'border-red-300' : 'border-slate-200'
                  }`}
                />
                {errors.shipping_address && (
                  <p className="text-xs text-red-500 font-medium">{errors.shipping_address.message}</p>
                )}
              </div>

              {/* Payment Method */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide flex items-center gap-1.5">
                  <CreditCard className="h-4 w-4 text-blue-600" />
                  Select Payment Method
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {[
                    { id: 'Credit Card', label: 'Credit / Debit Card', desc: 'Secure card transaction' },
                    { id: 'Cash On Delivery', label: 'Cash On Delivery (COD)', desc: 'Pay when delivered' }
                  ].map((method) => (
                    <label
                      key={method.id}
                      className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-start gap-3 cursor-pointer hover:bg-slate-100 transition-colors"
                    >
                      <input
                        type="radio"
                        value={method.id}
                        {...register('payment_method')}
                        className="mt-1"
                      />
                      <div>
                        <span className="text-xs font-bold text-slate-800">{method.label}</span>
                        <p className="text-[10px] text-slate-400 mt-0.5">{method.desc}</p>
                      </div>
                    </label>
                  ))}
                </div>
                {errors.payment_method && (
                  <p className="text-xs text-red-500 font-medium">{errors.payment_method.message}</p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-2">
                <Link
                  to="/cart"
                  className="px-5 py-2.5 border border-slate-200 rounded-xl hover:bg-slate-50 text-slate-600 font-semibold text-xs transition-colors flex items-center gap-1"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Review Cart
                </Link>
                <button
                  type="submit"
                  disabled={placeOrderMutation.isPending}
                  className="flex-1 py-2.5 bg-blue-600 text-white font-semibold rounded-xl text-xs hover:bg-blue-700 transition-all flex items-center justify-center gap-1.5 shadow-md shadow-blue-500/10 cursor-pointer"
                >
                  {placeOrderMutation.isPending ? (
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                  ) : (
                    <>
                      Confirm Order placement
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>

            </form>
          </div>
        </div>

        {/* Right Panel: Items preview & Totals */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Summary */}
          {summary && (
            <div className="p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
              <h3 className="font-extrabold text-slate-800 text-sm">Totals</h3>
              <div className="space-y-3.5 text-xs text-slate-600 border-b border-slate-50 pb-4">
                <div className="flex justify-between">
                  <span>Items Subtotal</span>
                  <span className="font-bold text-slate-800">₹{summary.subtotal.toLocaleString()}</span>
                </div>
                {summary.discount > 0 && (
                  <div className="flex justify-between text-emerald-600">
                    <span>Discount</span>
                    <span className="font-bold">-₹{summary.discount.toLocaleString()}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span>Shipping</span>
                  <span className="font-bold text-slate-800">₹{summary.shipping.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tax</span>
                  <span className="font-bold text-slate-800">₹{summary.tax.toLocaleString()}</span>
                </div>
              </div>
              <div className="flex justify-between text-sm font-black text-slate-800">
                <span>Final Amount</span>
                <span className="text-blue-600">₹{summary.total.toLocaleString()}</span>
              </div>
            </div>
          )}

          {/* List items */}
          <div className="p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
            <h3 className="font-extrabold text-slate-800 text-sm">Items In Order</h3>
            <div className="divide-y divide-slate-50 max-h-60 overflow-y-auto pr-1">
              {activeItems.map((item) => (
                <div key={item.id} className="py-3 flex gap-3 items-center justify-between text-xs">
                  <div className="flex gap-2 items-center min-w-0">
                    <div className="h-10 w-10 bg-slate-50 border border-slate-100 rounded-lg flex items-center justify-center overflow-hidden flex-shrink-0">
                      {item.product?.image_url ? (
                        <img src={item.product.image_url} alt={item.product.name} className="object-cover h-full w-full" />
                      ) : (
                        <Cpu className="h-5 w-5 text-slate-300" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <p className="font-bold text-slate-800 truncate max-w-[120px]">{item.product?.name}</p>
                      <p className="text-[10px] text-slate-400">Qty: {item.quantity}</p>
                    </div>
                  </div>
                  <span className="font-bold text-slate-800">
                    ₹{( (item.product?.price || 0) * item.quantity ).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default Checkout;
