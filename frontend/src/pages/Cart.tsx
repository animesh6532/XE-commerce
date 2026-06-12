import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cartService } from '../services/cart';
import {
  ShoppingBag,
  Trash2,
  Bookmark,
  Heart,
  Plus,
  Minus,
  Tag,
  ArrowRight,
  ChevronLeft,
  Cpu
} from 'lucide-react';
import { motion } from 'framer-motion';

const Cart: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [couponCode, setCouponCode] = useState('');
  const [couponMsg, setCouponMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

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

  // Mutations
  const updateQtyMutation = useMutation({
    mutationFn: ({ productId, qty }: { productId: number; qty: number }) =>
      cartService.updateQuantity(productId, qty),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['cartSummary'] });
    }
  });

  const removeMutation = useMutation({
    mutationFn: (productId: number) => cartService.removeFromCart(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['cartSummary'] });
    }
  });

  const clearMutation = useMutation({
    mutationFn: () => cartService.clearCart(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['cartSummary'] });
    }
  });

  const saveForLaterMutation = useMutation({
    mutationFn: (productId: number) => cartService.saveForLater(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['cartSummary'] });
      alert('Product saved for later.');
    }
  });

  const moveToWishlistMutation = useMutation({
    mutationFn: (productId: number) => cartService.moveToWishlist(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
      queryClient.invalidateQueries({ queryKey: ['cartSummary'] });
      alert('Product moved to wishlist.');
    }
  });

  const applyCouponMutation = useMutation({
    mutationFn: (code: string) => cartService.applyCoupon(code),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['cartSummary'] });
      if (res.success) {
        setCouponMsg({ type: 'success', text: `Coupon applied successfully! ${res.message}` });
      } else {
        setCouponMsg({ type: 'error', text: res.message });
      }
    },
    onError: (err: any) => {
      setCouponMsg({ type: 'error', text: err?.response?.data?.detail || 'Failed to apply coupon.' });
    }
  });

  const handleApplyCoupon = (e: React.FormEvent) => {
    e.preventDefault();
    if (couponCode.trim()) {
      applyCouponMutation.mutate(couponCode);
    }
  };

  const handleQtyChange = (productId: number, currentQty: number, offset: number) => {
    const nextQty = currentQty + offset;
    if (nextQty <= 0) {
      removeMutation.mutate(productId);
    } else {
      updateQtyMutation.mutate({ productId, qty: nextQty });
    }
  };

  const activeItems = cartItems.filter(item => !item.saved_for_later);
  const savedItems = cartItems.filter(item => item.saved_for_later);

  if (cartLoading) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto px-4 py-8">
        <div className="h-60 skeleton rounded-3xl" />
        <div className="h-20 skeleton rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-800 flex items-center gap-2">
          <ShoppingBag className="h-8 w-8 text-blue-600" />
          Shopping Cart
        </h1>
        <p className="text-sm text-slate-500 mt-1">Review and manage your pending purchases</p>
      </div>

      {activeItems.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Active Items Feed */}
          <div className="lg:col-span-2 space-y-4">
            {activeItems.map((item) => (
              <div
                key={item.id}
                className="p-5 rounded-2xl border border-slate-100 bg-white shadow-sm flex flex-col sm:flex-row gap-5 items-center justify-between"
              >
                {/* Product Meta */}
                <div className="flex gap-4 items-center w-full sm:w-auto">
                  <div className="h-20 w-20 bg-slate-50 border border-slate-100 rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden">
                    {item.product?.image_url ? (
                      <img src={item.product.image_url} alt={item.product.name} className="object-cover h-full w-full" />
                    ) : (
                      <Cpu className="h-8 w-8 text-slate-300" />
                    )}
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-bold text-slate-800 text-sm line-clamp-1">{item.product?.name || 'Loading Item...'}</h3>
                    <p className="text-[10px] font-bold text-slate-400 mt-0.5">{item.product?.brand}</p>
                    <p className="text-sm font-extrabold text-slate-800 mt-2">₹{item.product?.price.toLocaleString()}</p>
                  </div>
                </div>

                {/* Controls */}
                <div className="flex items-center justify-between sm:justify-end gap-6 w-full sm:w-auto">
                  {/* Quantity selector */}
                  <div className="flex items-center border border-slate-200 rounded-lg bg-slate-50">
                    <button
                      onClick={() => handleQtyChange(item.product_id, item.quantity, -1)}
                      className="p-1.5 text-slate-500 hover:text-slate-800"
                    >
                      <Minus className="h-4 w-4" />
                    </button>
                    <span className="px-3 text-xs font-bold text-slate-800">{item.quantity}</span>
                    <button
                      onClick={() => handleQtyChange(item.product_id, item.quantity, 1)}
                      className="p-1.5 text-slate-500 hover:text-slate-800"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Move/Remove buttons */}
                  <div className="flex gap-3 text-slate-400">
                    <button
                      onClick={() => moveToWishlistMutation.mutate(item.product_id)}
                      className="hover:text-blue-600 p-1"
                      title="Move to Wishlist"
                    >
                      <Heart className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => saveForLaterMutation.mutate(item.product_id)}
                      className="hover:text-purple-600 p-1"
                      title="Save for Later"
                    >
                      <Bookmark className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => removeMutation.mutate(item.product_id)}
                      className="hover:text-red-500 p-1"
                      title="Remove"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {/* Clear Cart Button */}
            <div className="flex justify-end">
              <button
                onClick={() => {
                  if (confirm('Clear all items from your cart?')) clearMutation.mutate();
                }}
                className="text-xs font-bold text-red-500 hover:text-red-600 flex items-center gap-1.5 uppercase tracking-wider cursor-pointer"
              >
                <Trash2 className="h-4 w-4" />
                Clear Shopping Cart
              </button>
            </div>
          </div>

          {/* Checkout & Summary Panel */}
          <div className="lg:col-span-1 space-y-6">
            <div className="p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-6">
              <h3 className="font-extrabold text-slate-800 text-sm">Order Summary</h3>

              {summary && (
                <div className="space-y-3.5 text-xs text-slate-600">
                  <div className="flex justify-between">
                    <span>Subtotal</span>
                    <span className="font-bold text-slate-800">₹{summary.subtotal.toLocaleString()}</span>
                  </div>
                  {summary.discount > 0 && (
                    <div className="flex justify-between text-emerald-600">
                      <span>Applied Coupon Discount</span>
                      <span className="font-bold">-₹{summary.discount.toLocaleString()}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>Shipping Charges</span>
                    <span className="font-bold text-slate-800">₹{summary.shipping.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Estimated Tax</span>
                    <span className="font-bold text-slate-800">₹{summary.tax.toLocaleString()}</span>
                  </div>
                  <div className="border-t border-slate-50 pt-4 flex justify-between text-sm font-black text-slate-800">
                    <span>Order Total</span>
                    <span className="text-blue-600">₹{summary.total.toLocaleString()}</span>
                  </div>
                </div>
              )}

              {/* Coupon Form */}
              <form onSubmit={handleApplyCoupon} className="space-y-2 pt-2 border-t border-slate-50">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Promo Coupon Code</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="e.g. DISCOUNT10"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    className="flex-1 px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 uppercase"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-slate-900 text-white font-semibold rounded-xl text-xs hover:bg-slate-800 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Tag className="h-3.5 w-3.5" />
                    Apply
                  </button>
                </div>
                {couponMsg && (
                  <p className={`text-[10px] font-semibold mt-1 ${couponMsg.type === 'success' ? 'text-emerald-600' : 'text-red-500'}`}>
                    {couponMsg.text}
                  </p>
                )}
              </form>

              {/* Checkout Button */}
              <Link
                to="/checkout"
                className="w-full py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-md shadow-blue-500/10 cursor-pointer"
              >
                Proceed to Checkout
                <ArrowRight className="h-4.5 w-4.5" />
              </Link>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl shadow-sm">
          <ShoppingBag className="h-12 w-12 text-slate-200 mx-auto mb-4 animate-bounce" />
          <h2 className="text-lg font-bold text-slate-800">Your Cart is Empty</h2>
          <p className="text-sm text-slate-400 max-w-xs mx-auto mt-1 leading-relaxed">
            Browse through our catalog of top-tier mechanical keyboards and monitors.
          </p>
          <Link
            to="/products"
            className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800"
          >
            <ChevronLeft className="h-4 w-4" />
            Continue Shopping
          </Link>
        </div>
      )}

      {/* Saved for later list */}
      {savedItems.length > 0 && (
        <div className="space-y-4 pt-8 border-t border-slate-100">
          <div>
            <h3 className="font-extrabold text-slate-800 text-sm flex items-center gap-1.5">
              <Bookmark className="h-4.5 w-4.5 text-purple-600" />
              Saved For Later ({savedItems.length})
            </h3>
            <p className="text-xs text-slate-400">Items you want to review at a later date</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedItems.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-2xl border border-slate-100 bg-white shadow-sm flex gap-4 items-center justify-between"
              >
                <div className="flex gap-3 items-center">
                  <div className="h-16 w-16 bg-slate-50 border border-slate-100 rounded-xl flex items-center justify-center overflow-hidden flex-shrink-0">
                    {item.product?.image_url ? (
                      <img src={item.product.image_url} alt={item.product.name} className="object-cover h-full w-full" />
                    ) : (
                      <Cpu className="h-6 w-6 text-slate-300" />
                    )}
                  </div>
                  <div className="min-w-0">
                    <h4 className="font-bold text-slate-800 text-xs truncate max-w-[150px]">{item.product?.name}</h4>
                    <p className="text-xs font-extrabold text-slate-800 mt-1">₹{item.product?.price.toLocaleString()}</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => updateQtyMutation.mutate({ productId: item.product_id, qty: 1 })}
                    className="px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg text-[10px] font-bold hover:bg-blue-100 border border-blue-100 cursor-pointer"
                  >
                    Move to Cart
                  </button>
                  <button
                    onClick={() => removeMutation.mutate(item.product_id)}
                    className="p-1.5 hover:text-red-500 text-slate-400"
                    title="Remove"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;
