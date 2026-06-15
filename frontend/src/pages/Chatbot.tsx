import React from 'react';
import { motion } from 'framer-motion';
import {
  MessageSquareCode,
  Sparkles,
  Volume2,
  ListFilter,
  ArrowRight,
  HelpCircle,
  Database,
  RefreshCw
} from 'lucide-react';

const Chatbot: React.FC = () => {
  const triggerOpen = () => {
    window.dispatchEvent(new CustomEvent('open-aura-chatbot'));
  };

  const features = [
    {
      icon: <Sparkles className="h-6 w-6 text-blue-600" />,
      title: 'Product-Aware RAG Intelligence',
      desc: 'Retrieves live database matching products in real-time, matching queries like "Best smartphone under 25000".'
    },
    {
      icon: <Volume2 className="h-6 w-6 text-purple-600" />,
      title: 'Text-to-Speech Engine',
      desc: 'Speech synthesis reads responses aloud. Custom volume sliders, mute preferences, and language selection included.'
    },
    {
      icon: <RefreshCw className="h-6 w-6 text-cyan-600" />,
      title: 'Word-by-word Streaming',
      desc: 'Simulates a premium chat typing effect with smooth word flow and instant typing indicators.'
    },
    {
      icon: <Database className="h-6 w-6 text-emerald-600" />,
      title: 'SQLite Storefront Linking',
      desc: 'Connects directly with SQLite backend data to provide matching product cards routing straight to product pages.'
    }
  ];

  return (
    <div className="py-12 max-w-5xl mx-auto space-y-16 px-4">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 border border-blue-100 text-blue-600 text-xs font-bold uppercase tracking-wider"
        >
          <Sparkles className="h-4 w-4 animate-spin-slow" />
          Global AI Store Assistant
        </motion.div>
        
        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-5xl font-extrabold text-slate-800 tracking-tight font-outfit"
        >
          Meet <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Aura AI Assistant</span>
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg text-slate-500 max-w-2xl mx-auto leading-relaxed"
        >
          We’ve upgraded your shopping experience. Aura is now a global Floating Assistant available on every page, loaded with voice support, real database querying, and brand comparison tools.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="pt-4"
        >
          <button
            onClick={triggerOpen}
            className="inline-flex items-center gap-2.5 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold rounded-2xl shadow-lg hover:shadow-xl transition-all scale-100 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
          >
            <MessageSquareCode className="h-5.5 w-5.5 animate-pulse" />
            Launch AI Assistant
            <ArrowRight className="h-5 w-5" />
          </button>
        </motion.div>
      </div>

      {/* Feature Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6">
        {features.map((feat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: idx * 0.1 }}
            className="p-6 bg-white border border-slate-100 rounded-3xl shadow-sm hover:shadow-md transition-shadow flex gap-4"
          >
            <div className="h-12 w-12 rounded-2xl bg-slate-50 flex items-center justify-center shrink-0 border border-slate-100/50">
              {feat.icon}
            </div>
            <div className="space-y-2">
              <h3 className="font-bold text-slate-800 text-base font-outfit">{feat.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{feat.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Suggestion / Tips Guide */}
      <div className="p-8 bg-gradient-to-tr from-slate-50 to-blue-50/20 border border-slate-100 rounded-3xl space-y-4">
        <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2 font-outfit">
          <HelpCircle className="h-5 w-5 text-blue-600" />
          What can you ask Aura?
        </h3>
        <p className="text-sm text-slate-500 leading-relaxed">
          Aura is fully aware of all active product collections, specifications, prices, and consumer reviews. Try typing the following directly into the assistant at the bottom right corner of your screen:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-2">
          <div className="p-3.5 bg-white border border-slate-100 rounded-2xl flex items-center justify-between">
            <span className="text-slate-600 font-medium italic">"Recommend a laptop under 80000"</span>
            <span className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">Laptops</span>
          </div>
          <div className="p-3.5 bg-white border border-slate-100 rounded-2xl flex items-center justify-between">
            <span className="text-slate-600 font-medium italic">"Best smartphone under 25000"</span>
            <span className="text-[10px] text-purple-600 font-bold uppercase tracking-wider">Phones</span>
          </div>
          <div className="p-3.5 bg-white border border-slate-100 rounded-2xl flex items-center justify-between">
            <span className="text-slate-600 font-medium italic">"Compare Samsung vs OnePlus"</span>
            <span className="text-[10px] text-cyan-600 font-bold uppercase tracking-wider">Comparison</span>
          </div>
          <div className="p-3.5 bg-white border border-slate-100 rounded-2xl flex items-center justify-between">
            <span className="text-slate-600 font-medium italic">"Show trending products"</span>
            <span className="text-[10px] text-emerald-600 font-bold uppercase tracking-wider">Trends</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
