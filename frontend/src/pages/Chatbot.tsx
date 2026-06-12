import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chatbotService, type ChatbotResponse, type ComparisonResponse, type ChatbotProduct } from '../services/chatbot';
import {
  MessageSquareCode,
  Send,
  Cpu,
  RefreshCw,
  Sparkles,
  Info,
  Scale,
  DollarSign,
  Bookmark,
  Check,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  source?: string;
  products?: ChatbotProduct[];
  comparison?: ComparisonResponse['comparison'] & {
    brand_a: string;
    brand_b: string;
    prod_a?: any;
    prod_b?: any;
  };
}

const Chatbot: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'assistant',
      text: 'Hello! I am your XE-Commerce AI Assistant. Ask me to find products within a budget, compare brands (like "compare boat vs jbl"), or find optimal deals.',
    },
  ]);
  
  const bottomRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load chat history on mount
  useEffect(() => {
    (async () => {
      try {
        const historyRes = await chatbotService.getChatHistory();
        if (historyRes && historyRes.history && historyRes.history.length > 0) {
          const historicalMessages: Message[] = [];
          historyRes.history.forEach((h) => {
            historicalMessages.push({ sender: 'user', text: h.query });
            historicalMessages.push({ sender: 'assistant', text: h.response, source: h.source });
          });
          setMessages((prev) => [...prev, ...historicalMessages]);
        }
      } catch {
        // Ignore failure loading history
      }
    })();
  }, []);

  // Mutations
  const queryMutation = useMutation({
    mutationFn: async (text: string) => {
      const isComparison = text.toLowerCase().includes('vs') || text.toLowerCase().includes('compare');
      if (isComparison) {
        // Call comparison endpoint
        const res = await chatbotService.compareProducts(text);
        return { type: 'comparison', data: res } as { type: string; data: any };
      } else {
        // Call general RAG query endpoint
        const res = await chatbotService.queryChatbot(text);
        return { type: 'query', data: res } as { type: string; data: any };
      }
    },
    onSuccess: (res, variables) => {
      if (res.type === 'comparison') {
        const compData = res.data as ComparisonResponse;
        setMessages((prev) => [
          ...prev,
          {
            sender: 'assistant',
            text: compData.comparison.recommendation || `Successfully compared ${compData.brand_a} and ${compData.brand_b}.`,
            comparison: {
              brand_a: compData.brand_a,
              brand_b: compData.brand_b,
              ...compData.comparison,
              prod_a: compData.product_a,
              prod_b: compData.product_b,
            } as any
          }
        ]);
      } else {
        const queryData = res.data as ChatbotResponse;
        setMessages((prev) => [
          ...prev,
          {
            sender: 'assistant',
            text: queryData.response,
            source: queryData.source,
            products: queryData.rag_data?.products || []
          }
        ]);
      }
      queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
    },
    onError: (err: any) => {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: `Error processing query: ${err?.response?.data?.detail || 'General retrieval error.'}`
        }
      ]);
    }
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const queryText = inputValue;
    setMessages((prev) => [...prev, { sender: 'user', text: queryText }]);
    setInputValue('');
    queryMutation.mutate(queryText);
  };

  const handleProductCardClick = (link: string) => {
    // Extract ID from link if standard, or search database.
    // Standard link structure is "/product/ID" or direct URL.
    // For convenience, redirect to products with search parameters.
    navigate(`/products?q=${encodeURIComponent(link.split('/').pop() || '')}`);
  };

  return (
    <div className="space-y-6 pb-12 max-w-4xl mx-auto h-[calc(100vh-12rem)] flex flex-col">
      
      {/* Title Header */}
      <div className="flex-shrink-0">
        <h1 className="text-2xl font-extrabold text-slate-800 flex items-center gap-2">
          <MessageSquareCode className="h-7 w-7 text-blue-600 animate-pulse" />
          RAG Shopping Assistant
        </h1>
        <p className="text-xs text-slate-400">Ask shopping recommendations, compare brands, or locate hardware details.</p>
      </div>

      {/* Chat Space */}
      <div className="flex-1 min-h-0 bg-white border border-slate-100 rounded-3xl shadow-sm overflow-hidden flex flex-col">
        
        {/* Messages Feed */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 max-w-[85%] ${
                msg.sender === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
              }`}
            >
              {/* Profile icon */}
              <div className={`h-8 w-8 rounded-xl flex items-center justify-center flex-shrink-0 border ${
                msg.sender === 'user'
                  ? 'bg-blue-50 border-blue-100 text-blue-600 font-bold text-xs'
                  : 'bg-purple-50 border-purple-100 text-purple-600'
              }`}>
                {msg.sender === 'user' ? 'ME' : <Cpu className="h-4 w-4" />}
              </div>

              {/* Bubble */}
              <div className="space-y-3">
                <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-slate-900 text-white rounded-tr-none'
                    : 'bg-slate-50 border border-slate-100 text-slate-700 rounded-tl-none'
                }`}>
                  <p>{msg.text}</p>

                  {msg.source && (
                    <span className="inline-block mt-2 text-[9px] font-bold text-slate-400 uppercase tracking-wide">
                      LLM Model Source: {msg.source}
                    </span>
                  )}
                </div>

                {/* Match product cards */}
                {msg.products && msg.products.length > 0 && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                    {msg.products.slice(0, 2).map((prod, pIdx) => (
                      <div
                        key={pIdx}
                        onClick={() => handleProductCardClick(prod.name)}
                        className="p-3 bg-white border border-slate-150 rounded-xl shadow-sm hover:shadow-md transition-shadow cursor-pointer flex gap-3 items-center"
                      >
                        <div className="h-10 w-10 bg-slate-50 rounded-lg flex items-center justify-center flex-shrink-0 border border-slate-100 overflow-hidden">
                          <Cpu className="h-5 w-5 text-slate-350" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="font-bold text-slate-800 text-xs truncate">{prod.name}</p>
                          <p className="text-[10px] font-extrabold text-blue-600 mt-0.5">{prod.discount_price || prod.actual_price}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Side by side Brand Comparisons */}
                {msg.comparison && (
                  <div className="p-5 border border-slate-150 rounded-2xl bg-white shadow-sm space-y-4 max-w-lg">
                    <h4 className="font-bold text-slate-800 text-xs flex items-center gap-1">
                      <Scale className="h-4 w-4 text-blue-600" />
                      Attribute Comparison ({msg.comparison.brand_a} vs {msg.comparison.brand_b})
                    </h4>
                    
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div className="p-3 bg-slate-50 rounded-xl space-y-1.5">
                        <span className="font-bold text-slate-700 uppercase tracking-wide text-[9px]">
                          {msg.comparison.brand_a} Specs
                        </span>
                        <p className="font-bold text-slate-800">Price: {msg.comparison.price.split(' vs ')[0]}</p>
                        <p className="font-semibold text-slate-600">Rating: {msg.comparison.ratings.split(' vs ')[0]}</p>
                        <div className="text-[10px] text-slate-500">
                          <p className="font-bold text-emerald-600">Pros:</p>
                          <ul className="list-disc pl-3">
                            {msg.comparison.pros[msg.comparison.brand_a]?.slice(0, 2).map((p, i) => <li key={i}>{p}</li>)}
                          </ul>
                        </div>
                      </div>

                      <div className="p-3 bg-slate-50 rounded-xl space-y-1.5">
                        <span className="font-bold text-slate-700 uppercase tracking-wide text-[9px]">
                          {msg.comparison.brand_b} Specs
                        </span>
                        <p className="font-bold text-slate-800">Price: {msg.comparison.price.split(' vs ')[1] || 'N/A'}</p>
                        <p className="font-semibold text-slate-600">Rating: {msg.comparison.ratings.split(' vs ')[1] || 'N/A'}</p>
                        <div className="text-[10px] text-slate-500">
                          <p className="font-bold text-emerald-600">Pros:</p>
                          <ul className="list-disc pl-3">
                            {msg.comparison.pros[msg.comparison.brand_b]?.slice(0, 2).map((p, i) => <li key={i}>{p}</li>)}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {queryMutation.isPending && (
            <div className="flex gap-3 mr-auto items-center">
              <div className="h-8 w-8 rounded-xl bg-purple-50 border border-purple-100 text-purple-600 flex items-center justify-center">
                <RefreshCw className="h-4 w-4 animate-spin" />
              </div>
              <div className="p-3 bg-slate-50 border border-slate-100 text-slate-500 rounded-2xl rounded-tl-none text-xs font-semibold">
                Running RAG pipeline query...
              </div>
            </div>
          )}
          
          <div ref={bottomRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex-shrink-0">
          <form onSubmit={handleSend} className="flex gap-2">
            <input
              type="text"
              placeholder="Ask RAG shopping queries..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={queryMutation.isPending}
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={queryMutation.isPending || !inputValue.trim()}
              className="p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center cursor-pointer"
            >
              <Send className="h-4.5 w-4.5" />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
};

export default Chatbot;
