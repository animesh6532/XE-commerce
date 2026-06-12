import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productService } from '../services/product';
import { cartService } from '../services/cart';
import { wishlistService } from '../services/wishlist';
import { reviewService } from '../services/review';
import { pricePredictionService } from '../services/pricePrediction';
import { userActivityService } from '../services/userActivity';
import { useAuth } from '../context/AuthContext';
import {
  Cpu,
  ShoppingBag,
  Heart,
  Calendar,
  AlertTriangle,
  Award,
  Sparkles,
  TrendingDown,
  ThumbsUp,
  ThumbsDown,
  ChevronRight,
  ShieldCheck,
  Send,
  MessageSquare
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { motion } from 'framer-motion';

const reviewSchema = z.object({
  rating: z.coerce.number().min(1, 'Please select a rating').max(5),
  comment: z.string().min(5, 'Feedback comment must be at least 5 characters'),
});

type ReviewFormValues = z.infer<typeof reviewSchema>;

const ProductDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const productId = parseInt(id || '0');
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  const [reviewError, setReviewError] = useState<string | null>(null);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<ReviewFormValues>({
    resolver: zodResolver(reviewSchema) as any,
    defaultValues: { rating: 5, comment: '' }
  });

  // Track product view on load
  React.useEffect(() => {
    if (isAuthenticated && productId) {
      userActivityService.trackView(productId).catch(() => {});
    }
  }, [productId, isAuthenticated]);

  // Queries
  const { data: product, isLoading: productLoading, error: productError } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => productService.getProduct(productId),
    enabled: !!productId
  });

  const { data: reviews = [], isLoading: reviewsLoading } = useQuery({
    queryKey: ['reviews', productId],
    queryFn: () => reviewService.getProductReviews(productId),
    enabled: !!productId
  });

  const { data: reviewSummary } = useQuery({
    queryKey: ['reviewSummary', productId],
    queryFn: () => reviewService.getReviewSummary(productId),
    enabled: !!productId,
    retry: false
  });

  const { data: bestTime } = useQuery({
    queryKey: ['bestTimeToBuy', productId],
    queryFn: () => pricePredictionService.getBestTimeToBuy(productId),
    enabled: !!productId,
    retry: false
  });

  const { data: priceTrendData } = useQuery({
    queryKey: ['priceTrend', productId],
    queryFn: () => pricePredictionService.getPriceTrend(productId),
    enabled: !!productId,
    retry: false
  });

  const { data: optimalPriceData } = useQuery({
    queryKey: ['optimalPrice', productId],
    queryFn: () => pricePredictionService.predictPrice(productId),
    enabled: !!productId,
    retry: false
  });

  // Mutations
  const addToCartMutation = useMutation({
    mutationFn: () => cartService.addToCart(productId, 1),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      alert('Product added to shopping cart!');
    },
    onError: (err: any) => {
      alert(err?.response?.data?.detail || 'Failed to add item to cart. Make sure you are logged in.');
    }
  });

  const addToWishlistMutation = useMutation({
    mutationFn: () => wishlistService.addToWishlist(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wishlist'] });
      alert('Product added to wishlist!');
    },
    onError: (err: any) => {
      alert(err?.response?.data?.detail || 'Failed to add item to wishlist. Make sure you are logged in.');
    }
  });

  const addReviewMutation = useMutation({
    mutationFn: (payload: { rating: number; comment: string }) =>
      reviewService.addReview({ product_id: productId, ...payload }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', productId] });
      queryClient.invalidateQueries({ queryKey: ['reviewSummary', productId] });
      reset();
      alert('Review submitted successfully!');
    },
    onError: (err: any) => {
      setReviewError(err?.response?.data?.detail || 'Failed to submit review.');
    }
  });

  const likeReviewMutation = useMutation({
    mutationFn: (reviewId: number) => reviewService.likeReview(reviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', productId] });
    }
  });

  const dislikeReviewMutation = useMutation({
    mutationFn: (reviewId: number) => reviewService.dislikeReview(reviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', productId] });
    }
  });

  if (productLoading) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto px-4 py-8">
        <div className="h-96 skeleton rounded-3xl" />
        <div className="grid grid-cols-3 gap-6">
          <div className="h-40 skeleton rounded-2xl col-span-2" />
          <div className="h-40 skeleton rounded-2xl" />
        </div>
      </div>
    );
  }

  if (productError || !product) {
    return (
      <div className="text-center py-16">
        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-slate-800">Product Not Found</h2>
        <p className="text-sm text-slate-400 mt-1">This product could not be loaded from the database.</p>
        <button onClick={() => navigate('/products')} className="mt-4 px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold">
          Return to Catalog
        </button>
      </div>
    );
  }

  // Formatting historical / forecasting price points
  const graphPoints = priceTrendData?.trend || [];

  return (
    <div className="space-y-12 pb-12">
      {/* Product top row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Product Image */}
        <div className="aspect-square bg-white border border-slate-100 rounded-3xl p-8 flex items-center justify-center overflow-hidden shadow-sm relative">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} className="object-contain max-h-[400px] w-full" />
          ) : (
            <Cpu className="h-24 w-24 text-slate-200 animate-pulse" />
          )}

          {/* AI Deal Score Badge */}
          {optimalPriceData?.prediction && (
            <div className="absolute bottom-6 left-6 p-4 rounded-2xl glass flex items-center gap-3 border border-blue-100 shadow-lg">
              <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center font-extrabold text-blue-600 text-sm">
                AI
              </div>
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">AI Recommendation</p>
                <p className="text-xs font-bold text-slate-800">
                  Optimal Base: ₹{Math.round(optimalPriceData.prediction.optimal_price).toLocaleString()}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Specs, Actions, Buy Indicator */}
        <div className="flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold px-3 py-1 bg-blue-50 text-blue-600 border border-blue-100 rounded-full uppercase tracking-wider">
                {product.category}
              </span>
              <span className="text-[10px] font-bold px-3 py-1 bg-slate-50 text-slate-500 border border-slate-100 rounded-full uppercase tracking-wider">
                {product.brand}
              </span>
            </div>

            <h1 className="text-3xl font-extrabold text-slate-800">{product.name}</h1>
            
            <div className="flex items-center space-x-2">
              <div className="flex items-center text-amber-500 font-bold text-sm">
                ★ {product.rating || 4.5}
              </div>
              <span className="text-slate-300">|</span>
              <span className="text-xs text-slate-500 font-semibold">{reviews.length} customer reviews</span>
            </div>

            <p className="text-sm text-slate-500 leading-relaxed pt-2">{product.description}</p>
          </div>

          {/* Buy Indicator Alert */}
          {bestTime && (
            <div className={`p-4 rounded-2xl border ${
              bestTime.action === 'BUY'
                ? 'bg-emerald-50 border-emerald-100 text-emerald-800'
                : 'bg-amber-50 border-amber-100 text-amber-800'
            } flex items-start gap-3`}>
              <div className={`h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                bestTime.action === 'BUY' ? 'bg-emerald-100' : 'bg-amber-100'
              }`}>
                <TrendingDown className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-extrabold text-sm uppercase tracking-wide">
                  Price Forecast: {bestTime.action}
                </h4>
                <p className="text-xs font-medium mt-0.5 leading-relaxed">{bestTime.message}</p>
              </div>
            </div>
          )}

          {/* Purchase Box */}
          <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-6">
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-wide">Actual Price</p>
              <p className="text-3xl font-black text-slate-800 mt-1">₹{product.price.toLocaleString()}</p>
              <p className="text-[10px] text-slate-400 font-bold mt-1">
                {product.stock > 0 ? `${product.stock} units currently in stock` : 'Sold Out'}
              </p>
            </div>

            <div className="flex gap-3 w-full sm:w-auto">
              <button
                onClick={() => addToWishlistMutation.mutate()}
                className="p-3 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl text-slate-600 transition-colors flex-shrink-0 cursor-pointer"
                title="Save to Wishlist"
              >
                <Heart className="h-5 w-5" />
              </button>
              <button
                onClick={() => addToCartMutation.mutate()}
                disabled={product.stock <= 0}
                className="flex-1 sm:flex-none px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2 shadow-md shadow-blue-500/10 cursor-pointer"
              >
                <ShoppingBag className="h-5 w-5" />
                Add to Cart
              </button>
            </div>
          </div>

        </div>
      </div>

      {/* Price Forecast Section */}
      {graphPoints.length > 0 && (
        <section className="glass rounded-3xl p-8 border border-white/50 bg-white/70 shadow-sm">
          <div className="mb-6 space-y-1">
            <h3 className="text-lg font-extrabold text-slate-800 flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-blue-600" />
              AI Price Forecast Trends
            </h3>
            <p className="text-xs text-slate-400">Predicted price changes for the upcoming weeks</p>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={graphPoints} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="date" stroke="#94A3B8" fontSize={10} tickLine={false} />
                <YAxis
                  stroke="#94A3B8"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `₹${v}`}
                  domain={['dataMin - 500', 'dataMax + 500']}
                />
                <Tooltip
                  formatter={(v: any) => [`₹${parseFloat(v).toLocaleString()}`, 'Forecast Price']}
                  labelClassName="text-slate-400 font-medium text-xs"
                  contentStyle={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px' }}
                />
                <Area type="monotone" dataKey="price" stroke="#2563EB" strokeWidth={3} fillOpacity={1} fill="url(#colorPrice)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      {/* Review details grid */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Side: Summary & Write Review */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Review Summary metrics */}
          <div className="p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
            <h4 className="font-extrabold text-slate-800 text-sm">Rating Summary</h4>
            <div className="flex items-center gap-4">
              <span className="text-4xl font-black text-slate-800">
                {reviewSummary?.average_rating?.toFixed(1) || product.rating}
              </span>
              <div>
                <div className="flex text-amber-500 font-bold text-sm">
                  ★ {reviewSummary?.average_rating?.toFixed(1) || product.rating}
                </div>
                <p className="text-[10px] text-slate-400 font-semibold mt-0.5">
                  Based on {reviewSummary?.total_reviews || reviews.length} customer ratings
                </p>
              </div>
            </div>

            {/* Fake review percentage badge */}
            {reviewSummary && (
              <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-2xl flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-emerald-600" />
                <div>
                  <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wide">AI Spam Review Detection</p>
                  <p className="text-xs font-bold text-slate-700">
                    {Math.round(reviewSummary.fake_review_percentage)}% Flagged Suspicious
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Add Review form */}
          {isAuthenticated ? (
            <div className="p-6 rounded-3xl border border-slate-100 bg-white shadow-sm space-y-4">
              <h4 className="font-extrabold text-slate-800 text-sm flex items-center gap-1.5">
                <MessageSquare className="h-4.5 w-4.5 text-blue-600" />
                Write a Review
              </h4>
              
              <form onSubmit={handleSubmit((data: any) => addReviewMutation.mutate(data))} className="space-y-4">
                {reviewError && (
                  <div className="p-3 bg-red-50 text-red-600 rounded-xl text-xs font-semibold">
                    {reviewError}
                  </div>
                )}

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Rating (Stars)</label>
                  <select
                    {...register('rating')}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="5">5 Stars</option>
                    <option value="4">4 Stars</option>
                    <option value="3">3 Stars</option>
                    <option value="2">2 Stars</option>
                    <option value="1">1 Star</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Comments</label>
                  <textarea
                    rows={3}
                    placeholder="Provide details on features, pricing..."
                    {...register('comment')}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                  {errors.comment && (
                    <p className="text-xs text-red-500 font-medium">{errors.comment.message}</p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={addReviewMutation.isPending}
                  className="w-full py-2 bg-slate-900 text-white font-semibold rounded-xl text-xs hover:bg-slate-800 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <Send className="h-3.5 w-3.5" />
                  Submit Feedback
                </button>
              </form>
            </div>
          ) : (
            <div className="p-6 rounded-3xl border border-dashed border-slate-200 text-center bg-slate-50/50">
              <MessageSquare className="h-8 w-8 text-slate-300 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-500">Sign in to write a review</p>
              <Link to="/login" className="mt-3 inline-block px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800">
                Log In
              </Link>
            </div>
          )}

        </div>

        {/* Right Side: Reviews Feed */}
        <div className="lg:col-span-2 space-y-4">
          <h4 className="font-extrabold text-slate-800 text-sm">Customer Feedback</h4>
          
          {reviews.length > 0 ? (
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
              {reviews.map((rev) => (
                <div key={rev.id} className="p-5 rounded-2xl border border-slate-100 bg-white shadow-sm flex flex-col justify-between gap-3">
                  <div className="flex justify-between items-start gap-4">
                    <div>
                      <span className="font-bold text-slate-800 text-xs uppercase tracking-wide">
                        {rev.username || 'Anonymous User'}
                      </span>
                      <div className="flex text-amber-500 text-xs font-bold mt-0.5">
                        {'★'.repeat(Math.round(rev.rating))}
                        {'☆'.repeat(5 - Math.round(rev.rating))}
                      </div>
                    </div>

                    {/* Badge Container */}
                    <div className="flex flex-wrap gap-1.5 justify-end">
                      {/* Sentiment Badge */}
                      {rev.sentiment && (
                        <span className={`px-2 py-0.5 text-[9px] font-bold uppercase rounded border ${
                          rev.sentiment === 'Positive'
                            ? 'bg-emerald-50 border-emerald-100 text-emerald-700'
                            : rev.sentiment === 'Negative'
                            ? 'bg-red-50 border-red-100 text-red-700'
                            : 'bg-slate-50 border-slate-100 text-slate-600'
                        }`}>
                          Sentiment: {rev.sentiment}
                        </span>
                      )}

                      {/* Fake Review Moderation Check */}
                      {rev.is_fake !== undefined && (
                        <span className={`px-2 py-0.5 text-[9px] font-bold uppercase rounded border ${
                          rev.is_fake
                            ? 'bg-red-50 border-red-100 text-red-700'
                            : 'bg-emerald-50 border-emerald-100 text-emerald-700'
                        }`}>
                          AI Check: {rev.is_fake ? 'Suspected Spam' : 'Verified'}
                        </span>
                      )}
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed">{rev.comment}</p>

                  <div className="flex items-center gap-4 pt-1 border-t border-slate-50 text-[10px] text-slate-400 font-semibold">
                    <button
                      onClick={() => likeReviewMutation.mutate(rev.id)}
                      className="flex items-center gap-1 hover:text-blue-600"
                    >
                      <ThumbsUp className="h-3.5 w-3.5" />
                      {rev.likes || 0} Likes
                    </button>
                    <button
                      onClick={() => dislikeReviewMutation.mutate(rev.id)}
                      className="flex items-center gap-1 hover:text-red-600"
                    >
                      <ThumbsDown className="h-3.5 w-3.5" />
                      {rev.dislikes || 0} Dislikes
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-white border border-slate-100 rounded-3xl">
              <MessageSquare className="h-8 w-8 text-slate-200 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-400">No reviews has been written for this product yet.</p>
            </div>
          )}
        </div>

      </section>
    </div>
  );
};

export default ProductDetails;
