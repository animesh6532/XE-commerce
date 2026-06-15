import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquareCode,
  Sparkles,
  X,
  Volume2,
  VolumeX,
  Copy,
  RotateCcw,
  Maximize2,
  Minimize2,
  ChevronDown,
  Send,
  Check,
  User,
  ExternalLink
} from 'lucide-react';
import { chatbotService, ChatbotProduct, ComparisonResponse } from '../../services/chatbot';
import { useAuth } from '../../context/AuthContext';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  originalQuery?: string;
  products?: ChatbotProduct[];
  comparison?: ComparisonResponse;
  source?: string;
  routedDataset?: string;
  timestamp: string;
}

export const FloatingChatbot: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  useEffect(() => {
    const handleOpen = () => {
      setIsOpen(true);
      setIsMinimized(false);
    };
    window.addEventListener('open-aura-chatbot', handleOpen);
    return () => {
      window.removeEventListener('open-aura-chatbot', handleOpen);
    };
  }, []);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Hello! I am Aura, your AI Shopping Assistant. Ask me to recommend products, specify budgets, or compare items side-by-side! \n\n*Try asking:*\n- "Show me mechanical keyboards under 5000"\n- "Compare Boat vs JBL Headphones"\n- "Recommend split AC above 4 star rating"',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // TTS State
  const [isMuted, setIsMuted] = useState(() => {
    const saved = localStorage.getItem('aura_tts_muted');
    return saved ? JSON.parse(saved) : false;
  });
  const [volume, setVolume] = useState(() => {
    const saved = localStorage.getItem('aura_tts_volume');
    return saved ? parseFloat(saved) : 0.8;
  });
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>('');
  
  // Streaming State
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [streamedText, setStreamedText] = useState<Record<string, string>>({});
  
  // UI States
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [showVoiceSettings, setShowVoiceSettings] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    "Gaming mouse under 3000",
    "Compare Samsung vs OnePlus",
    "Best AC under 35000",
    "Running shoes under 5000"
  ];

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, streamedText]);

  // Load Speech Voices
  useEffect(() => {
    const updateVoices = () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        const allVoices = window.speechSynthesis.getVoices();
        setVoices(allVoices);
        const savedVoice = localStorage.getItem('aura_tts_voice');
        const defaultVoice = allVoices.find(v => v.name === savedVoice) ||
          allVoices.find(v => v.lang.startsWith('en') || v.default) || 
          allVoices[0];
        if (defaultVoice) {
          setSelectedVoice(defaultVoice.name);
        }
      }
    };

    updateVoices();
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = updateVoices;
    }
    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, []);

  // Sync TTS preferences
  useEffect(() => {
    localStorage.setItem('aura_tts_muted', JSON.stringify(isMuted));
  }, [isMuted]);

  useEffect(() => {
    localStorage.setItem('aura_tts_volume', String(volume));
  }, [volume]);

  // TTS Speaker Helper
  const speakText = (text: string) => {
    if (isMuted || typeof window === 'undefined' || !window.speechSynthesis) return;
    
    window.speechSynthesis.cancel(); // Cancel active speech

    // Clean Markdown tags
    const cleanText = text
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/_([^_]+)_/g, '$1')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/#+\s?/g, '')
      .replace(/⭐/g, 'stars')
      .replace(/₹/g, 'Rs')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.volume = volume;

    if (selectedVoice) {
      const voice = voices.find(v => v.name === selectedVoice);
      if (voice) utterance.voice = voice;
    }

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  };

  // Start Local Streaming typing animation
  const startStreaming = (messageId: string, fullText: string) => {
    setStreamingMessageId(messageId);
    const words = fullText.split(' ');
    let currentIdx = 0;
    let currentText = '';

    const interval = setInterval(() => {
      if (currentIdx < words.length) {
        currentText += (currentText ? ' ' : '') + words[currentIdx];
        setStreamedText(prev => ({
          ...prev,
          [messageId]: currentText
        }));
        currentIdx++;
      } else {
        clearInterval(interval);
        setStreamingMessageId(null);
      }
    }, 45); // Adjust typing speed here

    // Speak response aloud automatically as it arrives
    speakText(fullText);
  };

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim()) return;

    stopSpeaking();

    const userMsgId = Date.now().toString();
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    setMessages(prev => [
      ...prev,
      { id: userMsgId, sender: 'user', text: textToSend, timestamp }
    ]);
    setInput('');
    setLoading(true);

    try {
      const isCompare = /compare|vs|versus/i.test(textToSend);

      if (isCompare) {
        const result = await chatbotService.compareProducts(textToSend);
        const assistantMsgId = (Date.now() + 1).toString();
        const recText = result.comparison?.recommendation || result.message || "I compared the items but could not find specific recommendations.";
        
        setMessages(prev => [
          ...prev,
          {
            id: assistantMsgId,
            sender: 'assistant',
            text: recText,
            originalQuery: textToSend,
            comparison: result,
            source: 'comparison_engine',
            routedDataset: result.dataset || 'unknown',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
        startStreaming(assistantMsgId, recText);
      } else {
        const result = await chatbotService.queryChatbot(textToSend);
        const assistantMsgId = (Date.now() + 1).toString();
        const responseText = result.response || "I couldn't find exact information, but I can still help you explore products.";
        
        setMessages(prev => [
          ...prev,
          {
            id: assistantMsgId,
            sender: 'assistant',
            text: responseText,
            originalQuery: textToSend,
            products: result.rag_data?.products || [],
            source: result.source || 'fallback',
            routedDataset: result.rag_data?.routed_dataset || 'unknown',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
        startStreaming(assistantMsgId, responseText);
      }
    } catch (err: any) {
      console.error('Chatbot floating error:', err);
      const assistantMsgId = (Date.now() + 1).toString();
      const errText = 'AI Assistant is temporarily unavailable.';
      setMessages(prev => [
        ...prev,
        {
          id: assistantMsgId,
          sender: 'assistant',
          text: errText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      startStreaming(assistantMsgId, errText);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, msgId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMessageId(msgId);
    setTimeout(() => setCopiedMessageId(null), 2000);
  };

  const renderMarkdown = (text: string) => {
    return text.split('\n').map((line, idx) => {
      let formatted = line;
      const boldRegex = /\*\*(.*?)\*\*/g;
      formatted = formatted.replace(boldRegex, '<strong>$1</strong>');

      const starSuggestRegex = /\*(.*?)\*/g;
      formatted = formatted.replace(starSuggestRegex, '<em>$1</em>');

      if (line.startsWith('- ') || line.startsWith('* ')) {
        return (
          <li
            key={idx}
            className="ml-4 list-disc text-slate-700 text-sm leading-relaxed"
            dangerouslySetInnerHTML={{ __html: formatted.substring(2) }}
          />
        );
      }
      return (
        <p
          key={idx}
          className="mb-2 text-slate-700 text-sm leading-relaxed"
          dangerouslySetInnerHTML={{ __html: formatted }}
        />
      );
    });
  };

  const handleProductClick = (link: string | undefined) => {
    if (!link) return;
    if (link.startsWith('/product/')) {
      const parts = link.split('/');
      const id = parts[parts.length - 1];
      navigate(`/product/${id}`);
      setIsMinimized(true);
    } else {
      window.open(link, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <>
      {/* Styles for glassmorphism and animations */}
      <style dangerouslySetInnerHTML={{ __html: `
        .aura-glass {
          background: rgba(255, 255, 255, 0.85);
          backdrop-filter: blur(14px);
          border: 1px solid rgba(255, 255, 255, 0.4);
          box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12);
        }
        .aura-glass-dark {
          background: rgba(15, 23, 42, 0.9);
          backdrop-filter: blur(14px);
          border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .aura-btn-primary {
          background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        }
        .aura-accent-bg {
          background-color: rgba(6, 182, 212, 0.1);
          color: #06B6D4;
        }
        .aura-chat-window-height {
          height: 580px;
        }
        @media (max-width: 640px) {
          .aura-chat-window-height {
            height: calc(100vh - 120px);
            width: 92%;
          }
        }
      `}} />

      {/* Floating Button Trigger */}
      <AnimatePresence>
        {(!isOpen || isMinimized) && (
          <motion.button
            key="fab"
            initial={{ scale: 0, opacity: 0, y: 50 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0, opacity: 0, y: 50 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              setIsOpen(true);
              setIsMinimized(false);
            }}
            className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full text-white shadow-xl focus:outline-none aura-btn-primary cursor-pointer"
            aria-label="Open AI Assistant"
          >
            <div className="relative">
              <MessageSquareCode className="h-6 w-6" />
              <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-cyan-400 text-[8px] font-bold text-slate-900 animate-pulse">
                new
              </span>
            </div>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Main Chat Panel */}
      <AnimatePresence>
        {isOpen && !isMinimized && (
          <motion.div
            key="chat-panel"
            initial={{ opacity: 0, scale: 0.9, y: 60 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 60 }}
            transition={{ type: 'spring', damping: 25, stiffness: 220 }}
            className="fixed bottom-6 right-6 z-50 w-full max-w-[400px] rounded-2xl overflow-hidden aura-glass flex flex-col aura-chat-window-height"
          >
            {/* Header */}
            <div className="p-4 flex items-center justify-between border-b border-slate-200/50 aura-btn-primary text-white">
              <div className="flex items-center gap-2.5">
                <div className="h-9 w-9 rounded-full bg-white/10 flex items-center justify-center border border-white/20">
                  <Sparkles className="h-5 w-5 text-cyan-300 animate-pulse" />
                </div>
                <div>
                  <h3 className="font-bold text-sm font-outfit tracking-wide flex items-center gap-1.5">
                    AURA ASSISTANT
                  </h3>
                  <div className="flex items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                    <span className="text-[10px] text-white/80 font-medium">Online & Product-Aware</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1">
                {/* Voice Control Controls */}
                <button
                  onClick={() => setShowVoiceSettings(!showVoiceSettings)}
                  className="p-1.5 rounded-lg hover:bg-white/10 transition-colors text-white/80 hover:text-white"
                  title="Voice Settings"
                >
                  <Volume2 className="h-4.5 w-4.5" />
                </button>
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className="p-1.5 rounded-lg hover:bg-white/10 transition-colors text-white/80 hover:text-white"
                  title={isMuted ? "Unmute TTS" : "Mute TTS"}
                >
                  {isMuted ? <VolumeX className="h-4.5 w-4.5 text-cyan-300" /> : <Volume2 className="h-4.5 w-4.5" />}
                </button>
                <button
                  onClick={() => setIsMinimized(true)}
                  className="p-1.5 rounded-lg hover:bg-white/10 transition-colors text-white/80 hover:text-white"
                  title="Minimize"
                >
                  <Minimize2 className="h-4.5 w-4.5" />
                </button>
                <button
                  onClick={() => {
                    stopSpeaking();
                    setIsOpen(false);
                  }}
                  className="p-1.5 rounded-lg hover:bg-white/10 transition-colors text-white/80 hover:text-white"
                  title="Close"
                >
                  <X className="h-4.5 w-4.5" />
                </button>
              </div>
            </div>

            {/* Voice Settings Dropdown */}
            <AnimatePresence>
              {showVoiceSettings && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="bg-slate-100 border-b border-slate-200 px-4 py-2.5 text-xs text-slate-700 flex flex-col gap-2 overflow-hidden"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-semibold text-slate-600">Voice Language:</span>
                    <select
                      value={selectedVoice}
                      onChange={(e) => {
                        setSelectedVoice(e.target.value);
                        localStorage.setItem('aura_tts_voice', e.target.value);
                      }}
                      className="bg-white border border-slate-300 rounded px-1.5 py-1 text-slate-800 focus:outline-none w-[200px] truncate"
                    >
                      {voices.map((v, i) => (
                        <option key={i} value={v.name}>{v.name} ({v.lang})</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-semibold text-slate-600">Volume:</span>
                    <div className="flex items-center gap-2 flex-1 max-w-[200px]">
                      <VolumeX className="h-3.5 w-3.5 text-slate-400" />
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={volume}
                        onChange={(e) => setVolume(parseFloat(e.target.value))}
                        className="w-full accent-blue-600 h-1 bg-slate-200 rounded"
                      />
                      <Volume2 className="h-3.5 w-3.5 text-slate-400" />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Message Area */}
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 bg-slate-50/50">
              {messages.map((msg) => {
                const isUser = msg.sender === 'user';
                const isStreaming = msg.id === streamingMessageId;
                const displayText = isStreaming ? (streamedText[msg.id] || '') : msg.text;

                return (
                  <div
                    key={msg.id}
                    className={`flex gap-2.5 max-w-[85%] ${isUser ? 'self-end flex-row-reverse' : 'self-start'}`}
                  >
                    {/* Avatar */}
                    <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
                      isUser 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gradient-to-tr from-blue-600 to-purple-600 text-white'
                    }`}>
                      {isUser ? (
                        user?.username ? user.username.substring(0, 2).toUpperCase() : <User className="h-4.5 w-4.5" />
                      ) : (
                        <Sparkles className="h-4.5 w-4.5 text-cyan-300" />
                      )}
                    </div>

                    {/* Bubble */}
                    <div className="flex flex-col gap-1">
                      <div className={`rounded-2xl px-3.5 py-2.5 text-sm shadow-sm ${
                        isUser 
                          ? 'bg-blue-600 text-white rounded-tr-none' 
                          : 'bg-white text-slate-800 border border-slate-100 rounded-tl-none'
                      }`}>
                        {isUser ? (
                          <p>{msg.text}</p>
                        ) : (
                          <>
                            {renderMarkdown(displayText)}

                            {/* Show products list */}
                            {!isStreaming && msg.products && msg.products.length > 0 && (
                              <div className="flex flex-col gap-2 mt-3 pt-3 border-t border-slate-100">
                                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Recommended Products</span>
                                <div className="flex flex-col gap-2">
                                  {msg.products.map((p, idx) => (
                                    <div
                                      key={idx}
                                      onClick={() => handleProductClick(p.link)}
                                      className="flex items-center gap-2.5 p-2 bg-slate-50 hover:bg-slate-100 rounded-xl border border-slate-100 cursor-pointer transition-colors group"
                                    >
                                      {p.image ? (
                                        <img src={p.image} alt={p.name} className="h-10 w-10 object-contain bg-white rounded-lg p-0.5" />
                                      ) : (
                                        <div className="h-10 w-10 rounded-lg bg-slate-200 flex items-center justify-center text-[8px] font-bold text-slate-500">No Image</div>
                                      )}
                                      <div className="flex-1 min-w-0">
                                        <div className="text-xs font-semibold text-slate-800 truncate group-hover:text-blue-600">{p.name}</div>
                                        <div className="flex items-center gap-2 mt-0.5">
                                          <span className="text-xs font-bold text-blue-600">
                                            {String(p.discount_price).replace('₹', 'Rs. ').trim()}
                                          </span>
                                          {p.clean_rating && (
                                            <span className="text-[9px] bg-amber-50 border border-amber-100 text-amber-600 font-bold px-1 rounded flex items-center gap-0.5">
                                              {p.clean_rating}⭐
                                            </span>
                                          )}
                                        </div>
                                      </div>
                                      <ExternalLink className="h-3.5 w-3.5 text-slate-400 group-hover:text-blue-600 shrink-0" />
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Show comparison table */}
                            {!isStreaming && msg.comparison && (
                              <div className="flex flex-col gap-2 mt-3 pt-3 border-t border-slate-100">
                                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Product Comparison</span>
                                <div className="grid grid-cols-2 gap-2 text-xs">
                                  {/* Product A */}
                                  {msg.comparison.product_a && (
                                    <div className="p-2 bg-slate-50 rounded-xl border border-slate-100 flex flex-col gap-1">
                                      <div className="font-bold text-slate-700 truncate">{msg.comparison.brand_a}</div>
                                      <div className="text-[10px] text-slate-500 truncate">{msg.comparison.product_a.name}</div>
                                      <div className="text-blue-600 font-semibold mt-1">
                                        {String(msg.comparison.product_a.discount_price).replace('₹', 'Rs.')}
                                      </div>
                                      <div className="text-[10px] text-slate-500">Rating: {msg.comparison.product_a.clean_rating} ⭐</div>
                                    </div>
                                  )}
                                  {/* Product B */}
                                  {msg.comparison.product_b && (
                                    <div className="p-2 bg-slate-50 rounded-xl border border-slate-100 flex flex-col gap-1">
                                      <div className="font-bold text-slate-700 truncate">{msg.comparison.brand_b}</div>
                                      <div className="text-[10px] text-slate-500 truncate">{msg.comparison.product_b.name}</div>
                                      <div className="text-blue-600 font-semibold mt-1">
                                        {String(msg.comparison.product_b.discount_price).replace('₹', 'Rs.')}
                                      </div>
                                      <div className="text-[10px] text-slate-500">Rating: {msg.comparison.product_b.clean_rating} ⭐</div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </>
                        )}
                      </div>

                      {/* Bubble Action Controls */}
                      <div className={`flex items-center gap-2 mt-1 px-1 text-[10px] text-slate-400 ${isUser ? 'justify-end' : 'justify-start'}`}>
                        <span>{msg.timestamp}</span>
                        {!isUser && !isStreaming && (
                          <>
                            <span>•</span>
                            <button
                              onClick={() => copyToClipboard(msg.text, msg.id)}
                              className="hover:text-blue-600 flex items-center gap-0.5 transition-colors"
                            >
                              {copiedMessageId === msg.id ? (
                                <Check className="h-3 w-3 text-emerald-500" />
                              ) : (
                                <Copy className="h-3 w-3" />
                              )}
                              {copiedMessageId === msg.id ? 'Copied' : 'Copy'}
                            </button>
                            {msg.originalQuery && (
                              <>
                                <span>•</span>
                                <button
                                  onClick={() => handleRegenerate(msg.originalQuery!)}
                                  className="hover:text-blue-600 flex items-center gap-0.5 transition-colors"
                                >
                                  <RotateCcw className="h-3 w-3" />
                                  Regen
                                </button>
                              </>
                            )}
                            <span>•</span>
                            <button
                              onClick={() => speakText(msg.text)}
                              className="hover:text-blue-600 flex items-center gap-0.5 transition-colors"
                            >
                              <Volume2 className="h-3 w-3" />
                              Replay
                            </button>
                            {msg.routedDataset && msg.routedDataset !== 'unknown' && (
                              <>
                                <span>•</span>
                                <span className="text-slate-400/80 italic">🗺️ {msg.routedDataset}</span>
                              </>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Typing indicator */}
              {loading && (
                <div className="flex gap-2.5 max-w-[85%] self-start">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 text-white flex items-center justify-center shrink-0">
                    <Sparkles className="h-4.5 w-4.5 text-cyan-300 animate-pulse" />
                  </div>
                  <div className="rounded-2xl px-4 py-3 bg-white text-slate-800 border border-slate-100 rounded-tl-none shadow-sm flex items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="h-2 w-2 rounded-full bg-blue-600 animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Suggestions Chips */}
            <div className="px-4 py-2 border-t border-slate-200/50 bg-slate-50 flex gap-1.5 overflow-x-auto scrollbar-none whitespace-nowrap shrink-0">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(s)}
                  className="px-2.5 py-1 text-xs bg-white text-slate-600 hover:text-blue-600 rounded-full border border-slate-200/60 shadow-sm cursor-pointer hover:border-blue-400 transition-all shrink-0"
                >
                  {s}
                </button>
              ))}
            </div>

            {/* Input Form */}
            <div className="p-3 border-t border-slate-200/50 bg-white flex gap-2 shrink-0 items-center">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
                placeholder="Ask Aura something..."
                className="flex-1 bg-slate-100/80 border border-slate-200/60 rounded-xl px-3.5 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition-all text-slate-800"
                disabled={loading}
              />
              <button
                onClick={() => handleSend(input)}
                disabled={loading || !input.trim()}
                className="h-9 w-9 rounded-xl text-white flex items-center justify-center aura-btn-primary cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shrink-0 transition-opacity"
              >
                <Send className="h-4.5 w-4.5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
