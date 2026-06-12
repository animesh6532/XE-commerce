import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productService, type Product } from '../services/product';
import { searchService } from '../services/search';
import { voiceSearchService } from '../services/voiceSearch';
import { imageSearchService } from '../services/imageSearch';
import { userActivityService } from '../services/userActivity';
import { useAuth } from '../context/AuthContext';
import {
  Search,
  Mic,
  Camera,
  SlidersHorizontal,
  X,
  Cpu,
  RefreshCw,
  ShoppingBag,
  Heart,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Info
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Products: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();

  // Search/Filter states from URL params or local
  const queryParam = searchParams.get('q') || '';
  const categoryParam = searchParams.get('category') || '';

  const [searchQuery, setSearchQuery] = useState(queryParam);
  const [searchMode, setSearchMode] = useState<'keyword' | 'semantic' | 'ai'>('keyword');
  
  // Filters
  const [selectedCategory, setSelectedCategory] = useState(categoryParam);
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minRating, setMinRating] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Modals
  const [voiceModalOpen, setVoiceModalOpen] = useState(false);
  const [imageModalOpen, setImageModalOpen] = useState(false);

  // Voice Search states
  const [isRecording, setIsRecording] = useState(false);
  const [voiceText, setVoiceText] = useState('');
  const [voiceCommandResponse, setVoiceCommandResponse] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  // Image Search states
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const [imageSearchLoading, setImageSearchLoading] = useState(false);
  const [visualMatches, setVisualMatches] = useState<Product[]>([]);

  // Page index
  const [page, setPage] = useState(1);
  const limit = 12;

  // Track search query URL updates
  useEffect(() => {
    setSearchQuery(queryParam);
  }, [queryParam]);

  useEffect(() => {
    setSelectedCategory(categoryParam);
  }, [categoryParam]);

  // Main Products Query using react-query
  const { data: products = [], isLoading: productsLoading, refetch } = useQuery({
    queryKey: ['products', page, selectedCategory, minPrice, maxPrice, minRating, selectedBrand, queryParam, searchMode],
    queryFn: async () => {
      // Log search activity to backend if user is authenticated and query exists
      if (isAuthenticated && queryParam) {
        userActivityService.trackSearch(queryParam).catch(() => {});
      }

      // If we have a query, use the search services
      if (queryParam) {
        if (searchMode === 'semantic') {
          return await searchService.semanticSearch(queryParam);
        } else if (searchMode === 'ai') {
          return await searchService.aiSearch(queryParam);
        } else {
          const res = await searchService.keywordSearch(queryParam, page, limit);
          return res.results;
        }
      }

      // If we have filters but no query
      if (selectedCategory || minPrice || maxPrice || minRating || selectedBrand) {
        return await productService.filterProducts({
          category: selectedCategory || undefined,
          min_price: minPrice ? parseFloat(minPrice) : undefined,
          max_price: maxPrice ? parseFloat(maxPrice) : undefined,
          min_rating: minRating ? parseFloat(minRating) : undefined,
          brand: selectedBrand || undefined
        });
      }

      // Default catalog paginated
      return await productService.getProducts(page, limit);
    }
  });

  // Reset page on filter changes
  useEffect(() => {
    setPage(1);
  }, [selectedCategory, minPrice, maxPrice, minRating, selectedBrand, queryParam]);

  // Handle Search Input submissions
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchParams((prev) => {
      if (searchQuery) prev.set('q', searchQuery);
      else prev.delete('q');
      return prev;
    });
  };

  const clearFilters = () => {
    setSelectedCategory('');
    setMinPrice('');
    setMaxPrice('');
    setMinRating('');
    setSelectedBrand('');
    setSearchQuery('');
    setSearchParams({});
    setVisualMatches([]);
  };

  // ---------------- Voice Search (Web Speech API) ----------------
  const startVoiceRecording = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition is not supported by your browser. Please try Chrome, Edge, or Safari.');
      return;
    }

    const rec = new SpeechRecognition();
    recognitionRef.current = rec;
    rec.continuous = false;
    rec.lang = 'en-US';
    rec.interimResults = false;

    rec.onstart = () => {
      setIsRecording(true);
      setVoiceText('Listening...');
      setVoiceCommandResponse(null);
    };

    rec.onresult = async (event: any) => {
      const text = event.results[0][0].transcript;
      setVoiceText(text);
      setIsRecording(false);

      try {
        // Run Voice Command check on the text (e.g. check if user spoke a control phrase)
        const cmdRes = await voiceSearchService.runVoiceCommand(text);
        if (cmdRes && cmdRes.action !== 'unknown') {
          setVoiceCommandResponse(`Command Action: ${cmdRes.action.toUpperCase()} - ${cmdRes.message}`);
          if (cmdRes.action === 'navigate_products') {
            setTimeout(() => {
              setVoiceModalOpen(false);
              navigate('/products');
            }, 1500);
          } else if (cmdRes.action === 'cart_add') {
            queryClient.invalidateQueries({ queryKey: ['cart'] });
          }
        } else {
          // If not a system command, treat as a text search query!
          setTimeout(() => {
            setVoiceModalOpen(false);
            setSearchParams({ q: text });
          }, 1000);
        }
      } catch {
        // Fallback to searching the query directly
        setTimeout(() => {
          setVoiceModalOpen(false);
          setSearchParams({ q: text });
        }, 1000);
      }
    };

    rec.onerror = () => {
      setIsRecording(false);
      setVoiceText('Recording failed. Try again.');
    };

    rec.onend = () => {
      setIsRecording(false);
    };

    rec.start();
  };

  const stopVoiceRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  // ---------------- Image Search ----------------
  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(file);
      setImagePreviewUrl(URL.createObjectURL(file));
      setVisualMatches([]);
    }
  };

  const runVisualImageSearch = async () => {
    if (!selectedImage) return;
    setImageSearchLoading(true);
    try {
      const res = await imageSearchService.searchByImage(selectedImage);
      if (res && res.success) {
        setVisualMatches(res.results);
        setImageModalOpen(false);
        // Toast can be displayed here
      }
    } catch {
      setVisualMatches([]);
      alert('Visual search failed. Check backend models.');
    } finally {
      setImageSearchLoading(false);
    }
  };

  const handleProductClick = (id: number) => {
    if (isAuthenticated) {
      userActivityService.trackClick(id, 'catalog_search').catch(() => {});
    }
    navigate(`/product/${id}`);
  };

  // Render visual search results or regular query results
  const activeProductsList = visualMatches.length > 0 ? visualMatches : products;

  return (
    <div className="flex flex-col gap-6">
      
      {/* Search mode / action controls */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
        
        {/* Search Mode Toggles */}
        <div className="flex bg-slate-100 p-1 rounded-xl w-full md:w-auto">
          {[
            { id: 'keyword', label: 'Keyword' },
            { id: 'semantic', label: 'Semantic (AI)' },
            { id: 'ai', label: 'RAG Search' }
          ].map((mode) => (
            <button
              key={mode.id}
              onClick={() => setSearchMode(mode.id as any)}
              className={`flex-1 md:flex-none text-xs font-semibold px-4 py-2 rounded-lg transition-all ${
                searchMode === mode.id
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {mode.label}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSearchSubmit} className="w-full md:max-w-xl flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder={`Search via ${searchMode} engine...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <Search className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
          </div>
          
          {/* Micro / Voice Search */}
          <button
            type="button"
            onClick={() => setVoiceModalOpen(true)}
            className="p-2.5 bg-slate-100 border border-slate-200 rounded-xl hover:bg-slate-200 transition-colors text-slate-600"
            title="Voice Search"
          >
            <Mic className="h-5 w-5" />
          </button>

          {/* Camera / Image Search */}
          <button
            type="button"
            onClick={() => setImageModalOpen(true)}
            className="p-2.5 bg-slate-100 border border-slate-200 rounded-xl hover:bg-slate-200 transition-colors text-slate-600"
            title="Image Search"
          >
            <Camera className="h-5 w-5" />
          </button>

          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2.5 rounded-xl border transition-colors flex items-center gap-1 text-sm font-semibold cursor-pointer ${
              showFilters || selectedCategory || minPrice || maxPrice || minRating || selectedBrand
                ? 'bg-blue-50 border-blue-200 text-blue-600'
                : 'bg-slate-100 border-slate-200 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <SlidersHorizontal className="h-5 w-5" />
            <span className="hidden sm:inline">Filters</span>
          </button>
        </form>
      </div>

      {/* Filter drawer / bar */}
      <AnimatePresence>
        {(showFilters || selectedCategory || minPrice || maxPrice || minRating || selectedBrand) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border border-slate-100 rounded-2xl bg-white shadow-sm p-6"
          >
            <div className="flex justify-between items-center mb-4 pb-2 border-b border-slate-50">
              <h3 className="font-bold text-slate-800 text-sm flex items-center gap-1.5">
                <SlidersHorizontal className="h-4.5 w-4.5 text-blue-600" />
                Refine Catalog Filters
              </h3>
              <button onClick={clearFilters} className="text-xs font-semibold text-slate-400 hover:text-blue-600 flex items-center gap-1">
                <RefreshCw className="h-3 w-3" />
                Clear All
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              {/* Category selector */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">All Categories</option>
                  <option value="Monitors">Monitors</option>
                  <option value="Keyboards">Keyboards</option>
                  <option value="Audio">Audio</option>
                  <option value="Laptops">Laptops</option>
                </select>
              </div>

              {/* Price range */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Price Range (₹)</label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    placeholder="Min"
                    value={minPrice}
                    onChange={(e) => setMinPrice(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                  <span className="text-slate-300">-</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={maxPrice}
                    onChange={(e) => setMaxPrice(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>

              {/* Ratings */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Ratings</label>
                <select
                  value={minRating}
                  onChange={(e) => setMinRating(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">Any Rating</option>
                  <option value="4">4.0 ★ & Above</option>
                  <option value="3">3.0 ★ & Above</option>
                  <option value="2">2.0 ★ & Above</option>
                </select>
              </div>

              {/* Brand */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Brand</label>
                <input
                  type="text"
                  placeholder="e.g. Boat, JBL"
                  value={selectedBrand}
                  onChange={(e) => setSelectedBrand(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Visual Search Results indicator */}
      {visualMatches.length > 0 && (
        <div className="p-4 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-center justify-between text-emerald-800">
          <p className="text-sm font-semibold flex items-center gap-1.5">
            <Sparkles className="h-4.5 w-4.5 text-emerald-600 animate-spin" />
            Showing similarity results based on visual image search.
          </p>
          <button onClick={() => setVisualMatches([])} className="text-xs font-bold text-emerald-600 hover:text-emerald-800 uppercase tracking-wider">
            Reset to Catalog
          </button>
        </div>
      )}

      {/* Catalog Grid */}
      {productsLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="h-80 skeleton rounded-2xl" />
          ))}
        </div>
      ) : activeProductsList.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-6">
          {activeProductsList.map((prod) => (
            <div
              key={prod.id}
              onClick={() => handleProductClick(prod.id)}
              className="group rounded-2xl border border-slate-100 bg-white p-4 hover:shadow-lg transition-all cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="aspect-square bg-slate-50 border border-slate-100 rounded-xl flex items-center justify-center overflow-hidden relative mb-4">
                  {prod.image_url ? (
                    <img src={prod.image_url} alt={prod.name} className="object-cover h-full w-full group-hover:scale-105 transition-transform" />
                  ) : (
                    <Cpu className="h-12 w-12 text-slate-300" />
                  )}
                  <span className="absolute top-2 right-2 px-2 py-0.5 bg-blue-600 text-[10px] font-bold uppercase rounded text-white shadow-sm">
                    ★ {prod.rating || 4.2}
                  </span>
                </div>
                <h3 className="font-bold text-slate-800 text-sm line-clamp-2 group-hover:text-blue-600 transition-colors">
                  {prod.name}
                </h3>
                <span className="text-[10px] font-bold text-slate-400 mt-0.5 block">{prod.brand}</span>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <span className="text-base font-extrabold text-slate-800">₹{prod.price.toLocaleString()}</span>
                <span className="text-xs text-slate-400 font-semibold">{prod.stock > 0 ? `${prod.stock} in stock` : 'Out of stock'}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white border border-slate-100 rounded-3xl shadow-sm">
          <Cpu className="h-12 w-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-base font-bold text-slate-800">No Products Found</h3>
          <p className="text-sm text-slate-400 max-w-xs mx-auto mt-1 leading-relaxed">
            Try adjusting your search criteria, switching modes, or resetting your filter fields.
          </p>
          <button onClick={clearFilters} className="mt-4 px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-xl hover:bg-slate-800 transition-colors">
            Reset Catalog
          </button>
        </div>
      )}

      {/* Pagination controls */}
      {!queryParam && activeProductsList.length >= limit && (
        <div className="flex items-center justify-center gap-4 pt-6">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="p-2 border border-slate-200 rounded-xl bg-white hover:bg-slate-50 disabled:opacity-50 transition-all cursor-pointer"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <span className="text-sm font-semibold text-slate-600">Page {page}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={activeProductsList.length < limit}
            className="p-2 border border-slate-200 rounded-xl bg-white hover:bg-slate-50 disabled:opacity-50 transition-all cursor-pointer"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      )}

      {/* ---------------- Voice Search Modal ---------------- */}
      <AnimatePresence>
        {voiceModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 relative overflow-hidden"
            >
              <button
                onClick={() => {
                  stopVoiceRecording();
                  setVoiceModalOpen(false);
                }}
                className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>

              <div className="text-center py-6 space-y-6">
                <div className="space-y-2">
                  <h3 className="font-extrabold text-slate-800 text-base">Voice Assistant search</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Speak commands like "Mechanical keyboards under 5000" or controls like "add item 2 to cart" or "navigate to products".
                  </p>
                </div>

                <div className="flex justify-center">
                  <button
                    onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                    className={`h-20 w-20 rounded-full flex items-center justify-center transition-all ${
                      isRecording
                        ? 'bg-red-500 text-white animate-ping'
                        : 'bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-100'
                    }`}
                  >
                    <Mic className="h-8 w-8" />
                  </button>
                </div>

                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Transcribing</p>
                  <p className="text-sm font-bold text-slate-700 mt-1">{voiceText || 'Press the microphone to begin...'}</p>
                </div>

                {voiceCommandResponse && (
                  <div className="p-3 bg-blue-50 border border-blue-100 text-blue-700 rounded-xl text-xs font-semibold flex items-center gap-1.5">
                    <Info className="h-4 w-4 flex-shrink-0" />
                    {voiceCommandResponse}
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ---------------- Image Search Modal ---------------- */}
      <AnimatePresence>
        {imageModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 relative overflow-hidden"
            >
              <button
                onClick={() => setImageModalOpen(false)}
                className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>

              <div className="space-y-6">
                <div>
                  <h3 className="font-extrabold text-slate-800 text-base">Visual Image Search</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Upload an image of a device or component, and our visual encoder will scan the database for matching products.
                  </p>
                </div>

                <div className="border-2 border-dashed border-slate-200 rounded-2xl p-6 text-center bg-slate-50/50 hover:bg-slate-50 transition-colors relative">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  {imagePreviewUrl ? (
                    <div className="space-y-3">
                      <img src={imagePreviewUrl} alt="Preview" className="mx-auto h-32 object-contain rounded-xl border border-slate-100" />
                      <p className="text-xs font-semibold text-slate-500">Click or drag another image to change</p>
                    </div>
                  ) : (
                    <div className="space-y-2 py-4">
                      <Camera className="h-8 w-8 text-slate-300 mx-auto" />
                      <p className="text-xs font-bold text-slate-600">Select Image File</p>
                      <p className="text-[10px] text-slate-400">Supports PNG, JPG, JPEG</p>
                    </div>
                  )}
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setImageModalOpen(false)}
                    className="flex-1 py-2.5 bg-slate-100 text-slate-600 font-semibold rounded-xl text-xs hover:bg-slate-200 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={runVisualImageSearch}
                    disabled={!selectedImage || imageSearchLoading}
                    className="flex-1 py-2.5 bg-blue-600 text-white font-semibold rounded-xl text-xs hover:bg-blue-700 transition-colors flex items-center justify-center gap-1.5 disabled:opacity-50"
                  >
                    {imageSearchLoading ? (
                      <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <>
                        <Search className="h-3.5 w-3.5" />
                        Scan Image
                      </>
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
};

export default Products;
