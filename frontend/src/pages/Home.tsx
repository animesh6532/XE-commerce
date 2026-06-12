import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { productService } from '../services/product';
import { recommendationService } from '../services/recommendation';
import {
  Sparkles,
  ArrowRight,
  TrendingUp,
  Cpu,
  Bookmark,
  DollarSign,
  Search,
  ChevronRight
} from 'lucide-react';
import { motion } from 'framer-motion';

const Home: React.FC = () => {
  const navigate = useNavigate();

  // Queries
  const { data: trendingProducts = [], isLoading: trendingLoading } = useQuery({
    queryKey: ['trendingProducts'],
    queryFn: productService.getTrendingProducts
  });

  const { data: dealProducts = [], isLoading: dealsLoading } = useQuery({
    queryKey: ['dealProducts'],
    queryFn: productService.getDealProducts
  });

  // Budget states
  const [budgetCategory, setBudgetCategory] = useState('Keyboards');
  const [budgetValue, setBudgetValue] = useState('');
  const [budgetResults, setBudgetResults] = useState<any[]>([]);
  const [budgetLoading, setBudgetLoading] = useState(false);
  const [budgetSearched, setBudgetSearched] = useState(false);

  const handleBudgetSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const parsedBudget = parseFloat(budgetValue);
    if (isNaN(parsedBudget) || parsedBudget <= 0) return;

    setBudgetLoading(true);
    setBudgetSearched(true);
    try {
      const data = await recommendationService.getBudgetRecommendations({
        category: budgetCategory,
        budget: parsedBudget,
        top_k: 4
      });
      setBudgetResults(data);
    } catch {
      setBudgetResults([]);
    } finally {
      setBudgetLoading(false);
    }
  };

  return (
    <div className="space-y-16 pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white shadow-xl py-16 px-8 sm:px-12 text-center md:text-left">
        <div className="max-w-3xl space-y-6 relative z-10">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-white/10 backdrop-blur-md text-xs font-bold uppercase tracking-wider rounded-full text-blue-100 border border-white/10">
            <Sparkles className="h-3.5 w-3.5 text-yellow-300 animate-spin" />
            AI-Driven Commerce Platform
          </span>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            Discover Tech Reimagined by Artificial Intelligence
          </h1>
          <p className="text-lg text-blue-100 leading-relaxed max-w-xl">
            Experience real-time price drops, sentiment tags, and natural language shopping queries powered by five enterprise ML pipelines.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 pt-2 justify-center md:justify-start">
            <Link
              to="/products"
              className="px-6 py-3.5 bg-white text-blue-600 rounded-xl font-semibold hover:bg-slate-50 shadow-md transition-all flex items-center justify-center gap-2"
            >
              Browse Catalog
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/chatbot"
              className="px-6 py-3.5 bg-white/10 border border-white/20 hover:bg-white/20 rounded-xl font-semibold transition-all flex items-center justify-center gap-2"
            >
              Ask AI Assistant
            </Link>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-0 right-0 h-full w-1/3 bg-radial-gradient from-white/10 to-transparent pointer-events-none hidden md:block" />
        <div className="absolute -bottom-10 -right-10 h-40 w-40 rounded-full bg-indigo-500/20 blur-3xl pointer-events-none" />
      </section>

      {/* Category Explorer */}
      <section className="space-y-6">
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-800">Explore Categories</h2>
            <p className="text-sm text-slate-500 mt-1">Sleek designs tailored for high performance</p>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { name: 'Monitors', desc: '4K IPS Panels', icon: Cpu, col: 'from-blue-500 to-cyan-500' },
            { name: 'Keyboards', desc: 'Mechanical switches', icon: Cpu, col: 'from-indigo-500 to-purple-500' },
            { name: 'Audio', desc: 'ANC Wireless', icon: Cpu, col: 'from-pink-500 to-rose-500' },
            { name: 'Laptops', desc: 'Next-Gen Intel/M3', icon: Cpu, col: 'from-emerald-500 to-teal-500' }
          ].map((cat, idx) => (
            <div
              key={idx}
              onClick={() => navigate(`/products?category=${cat.name}`)}
              className="group p-6 rounded-2xl glass hover:shadow-lg transition-all cursor-pointer border border-slate-100 flex flex-col justify-between h-40 relative overflow-hidden bg-white"
            >
              <div className={`h-10 w-10 rounded-xl bg-slate-50 flex items-center justify-center group-hover:scale-110 transition-all shadow-sm`}>
                <cat.icon className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-bold text-slate-800 text-base">{cat.name}</h3>
                <p className="text-xs text-slate-400 mt-0.5">{cat.desc}</p>
              </div>
              <ChevronRight className="absolute bottom-6 right-6 h-5 w-5 text-slate-300 group-hover:translate-x-1 transition-transform" />
            </div>
          ))}
        </div>
      </section>

      {/* Budget Advisor AI Tool */}
      <section className="glass rounded-3xl p-8 border border-white/50 bg-white/70 shadow-md">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <div className="lg:col-span-1 space-y-4">
            <div className="h-10 w-10 rounded-xl bg-purple-50 flex items-center justify-center border border-purple-100">
              <DollarSign className="h-5 w-5 text-purple-600" />
            </div>
            <h2 className="text-xl font-extrabold text-slate-800">AI Budget Assistant</h2>
            <p className="text-sm text-slate-500 leading-relaxed">
              Input your target category and budget. Our hybrid candidate generator will screen products and match optimal fits instantly.
            </p>
            
            <form onSubmit={handleBudgetSearch} className="space-y-4 pt-2">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Category</label>
                  <select
                    value={budgetCategory}
                    onChange={(e) => setBudgetCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-white text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="Monitors">Monitors</option>
                    <option value="Keyboards">Keyboards</option>
                    <option value="Audio">Audio</option>
                    <option value="Laptops">Laptops</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Max Price</label>
                  <input
                    type="number"
                    placeholder="e.g. 5000"
                    value={budgetValue}
                    onChange={(e) => setBudgetValue(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-xl bg-white text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                    required
                  />
                </div>
              </div>
              <button
                type="submit"
                className="w-full py-2.5 bg-slate-900 text-white font-semibold rounded-xl text-xs hover:bg-slate-800 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Search className="h-3.5 w-3.5" />
                Find Optimal Matches
              </button>
            </form>
          </div>

          <div className="lg:col-span-2 flex flex-col justify-center min-h-[200px]">
            {budgetLoading ? (
              <div className="grid grid-cols-2 gap-4">
                {[1, 2].map((i) => (
                  <div key={i} className="h-32 skeleton rounded-2xl" />
                ))}
              </div>
            ) : budgetSearched ? (
              budgetResults.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {budgetResults.map((prod) => (
                    <div
                      key={prod.id}
                      onClick={() => navigate(`/product/${prod.id}`)}
                      className="p-4 rounded-2xl border border-slate-100 bg-white shadow-sm hover:shadow-md transition-shadow cursor-pointer flex gap-4"
                    >
                      <div className="h-16 w-16 bg-slate-50 border border-slate-100 rounded-xl flex items-center justify-center overflow-hidden flex-shrink-0">
                        {prod.image_url ? (
                          <img src={prod.image_url} alt={prod.name} className="object-cover h-full w-full" />
                        ) : (
                          <Cpu className="h-6 w-6 text-slate-300" />
                        )}
                      </div>
                      <div className="min-w-0">
                        <h4 className="font-bold text-slate-800 text-sm truncate">{prod.name}</h4>
                        <span className="inline-block mt-1 text-[10px] font-bold text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                          {prod.brand}
                        </span>
                        <p className="mt-2 text-sm font-extrabold text-blue-600">₹{prod.price.toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 bg-slate-50/50 rounded-2xl border border-dashed border-slate-200">
                  <Bookmark className="h-8 w-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-sm font-medium text-slate-500">No items found within that price range.</p>
                </div>
              )
            ) : (
              <div className="text-center py-12 bg-slate-50/30 rounded-2xl border border-dashed border-slate-150">
                <Cpu className="h-10 w-10 text-slate-300 mx-auto mb-3 animate-bounce" />
                <p className="text-sm font-semibold text-slate-500">Results will render here</p>
                <p className="text-xs text-slate-400 mt-1">Configure parameters on the left to invoke budget checks.</p>
              </div>
            )}
          </div>

        </div>
      </section>

      {/* Trending Items Grid */}
      <section className="space-y-6">
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-800 flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-blue-600" />
              Trending Deals
            </h2>
            <p className="text-sm text-slate-500 mt-1">Our most popular items backed by verified customer opinions</p>
          </div>
          <Link to="/products" className="text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1">
            View All
            <ChevronRight className="h-4 w-4" />
          </Link>
        </div>

        {trendingLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-64 skeleton rounded-2xl" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {trendingProducts.slice(0, 4).map((prod) => (
              <div
                key={prod.id}
                onClick={() => navigate(`/product/${prod.id}`)}
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
                      ★ {prod.rating}
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-800 text-sm line-clamp-1 group-hover:text-blue-600 transition-colors">
                    {prod.name}
                  </h3>
                  <span className="text-[10px] font-bold text-slate-400 mt-0.5 block">{prod.category}</span>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-base font-extrabold text-slate-800">₹{prod.price.toLocaleString()}</span>
                  <span className="text-xs text-slate-400 font-semibold">{prod.stock > 0 ? `${prod.stock} in stock` : 'Out of stock'}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Featured Deals Carousel */}
      <section className="space-y-6">
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-800">Featured Releases</h2>
            <p className="text-sm text-slate-500 mt-1">Exclusive releases curated by premium sellers</p>
          </div>
        </div>

        {dealsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-44 skeleton rounded-2xl" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {dealProducts.slice(0, 3).map((prod) => (
              <div
                key={prod.id}
                onClick={() => navigate(`/product/${prod.id}`)}
                className="p-5 rounded-2xl border border-slate-100 bg-white shadow-sm hover:shadow-md transition-all cursor-pointer flex gap-5 relative overflow-hidden"
              >
                <div className="h-20 w-20 bg-slate-50 rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden border border-slate-50">
                  {prod.image_url ? (
                    <img src={prod.image_url} alt={prod.name} className="object-cover h-full w-full" />
                  ) : (
                    <Cpu className="h-8 w-8 text-slate-300" />
                  )}
                </div>
                <div className="flex flex-col justify-between min-w-0 flex-1">
                  <div>
                    <h3 className="font-bold text-slate-800 text-sm truncate">{prod.name}</h3>
                    <p className="text-[10px] font-bold text-slate-400 mt-0.5">{prod.brand}</p>
                  </div>
                  <div className="flex justify-between items-end mt-4">
                    <span className="text-sm font-extrabold text-blue-600">₹{prod.price.toLocaleString()}</span>
                    <span className="text-[10px] text-slate-400 font-bold border border-slate-100 px-2 py-0.5 rounded">
                      Featured
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default Home;
