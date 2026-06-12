import React, { useState, useEffect, useRef } from 'react';
import { 
  chatbotService, 
  Product, 
  ComparisonResponse, 
  HistoryItem 
} from '../../services/chatbot';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  products?: Product[];
  comparison?: ComparisonResponse;
  source?: string;
  routedDataset?: string;
}

export const ChatbotWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Hello! I am Aura, your AI Shopping Assistant. Ask me to recommend products, specify budgets, or compare items side-by-side! \n\n*Try asking:*\n- "Show me mechanical keyboards under 5000"\n- "Compare Boat vs JBL Headphones"\n- "Recommend split AC above 4 star rating"'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Quick suggestions
  const suggestions = [
    "Gaming mouse under 3000",
    "Compare Samsung vs OnePlus",
    "Lloyd AC under 35k and 4+ stars",
    "Dog food below 1500"
  ];

  useEffect(() => {
    // Scroll to bottom on new messages
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    // Load categories and history on mount
    loadCategories();
    loadHistory();
  }, []);

  const loadCategories = async () => {
    try {
      const data = await chatbotService.getCategories();
      setCategories(data.categories);
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };

  const loadHistory = async () => {
    try {
      const data = await chatbotService.getChatHistory();
      setHistory(data.history);
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim()) return;

    const userMsgId = Date.now().toString();
    const newMessages: Message[] = [
      ...messages,
      { id: userMsgId, sender: 'user', text: textToSend }
    ];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      // Determine if comparison or general query
      const isCompare = /compare|vs|versus/i.test(textToSend);

      if (isCompare) {
        const result = await chatbotService.compareProducts(textToSend);
        if (result.status === 'success') {
          setMessages(prev => [
            ...prev,
            {
              id: Date.now().toString(),
              sender: 'assistant',
              text: result.comparison.recommendation,
              comparison: result,
              source: 'comparison_engine',
              routedDataset: result.dataset
            }
          ]);
        } else {
          setMessages(prev => [
            ...prev,
            {
              id: Date.now().toString(),
              sender: 'assistant',
              text: `I tried to compare items, but encountered a problem: ${result.message}`
            }
          ]);
        }
      } else {
        const result = await chatbotService.queryChatbot(textToSend);
        setMessages(prev => [
          ...prev,
          {
            id: Date.now().toString(),
            sender: 'assistant',
            text: result.response,
            products: result.rag_data?.products || [],
            source: result.source,
            routedDataset: result.rag_data?.routed_dataset
          }
        ]);
      }
      loadHistory();
    } catch (err: any) {
      console.error('Chat error:', err);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          sender: 'assistant',
          text: 'Oops! I had trouble processing that request. Please check if the FastAPI backend is running and try again.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Simple Markdown renderer
  const renderMarkdown = (text: string) => {
    return text.split('\n').map((line, idx) => {
      // Bold matching
      let formatted = line;
      const boldRegex = /\*\*(.*?)\*\*/g;
      formatted = formatted.replace(boldRegex, '<strong>$1</strong>');

      // Italic suggestions list
      const starSuggestRegex = /\*(.*?)\*/g;
      formatted = formatted.replace(starSuggestRegex, '<em>$1</em>');

      if (line.startsWith('- ') || line.startsWith('* ')) {
        return <li key={idx} className="ml-4 list-disc" dangerouslySetInnerHTML={{ __html: formatted.substring(2) }} />;
      }
      return <p key={idx} className="mb-2" dangerouslySetInnerHTML={{ __html: formatted }} />;
    });
  };

  return (
    <div className="aura-chat-container">
      {/* CSS injection for premium styling */}
      <style dangerouslySetInnerHTML={{ __html: `
        .aura-chat-container {
          display: grid;
          grid-template-columns: ${showHistory ? '300px 1fr' : '1fr'};
          background-color: #0b0f19;
          border-radius: 20px;
          border: 1px solid rgba(255, 255, 255, 0.08);
          box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
          height: 75vh;
          overflow: hidden;
          font-family: 'Plus Jakarta Sans', sans-serif;
          transition: all 0.3s ease;
        }

        .aura-history-sidebar {
          background-color: rgba(22, 28, 45, 0.5);
          border-right: 1px solid rgba(255, 255, 255, 0.08);
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          overflow-y: auto;
        }

        .aura-chat-main {
          display: flex;
          flex-direction: column;
          height: 100%;
          background: radial-gradient(circle at 50% 50%, rgba(191, 90, 242, 0.03) 0%, transparent 100%);
        }

        .aura-chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.08);
          background: rgba(22, 28, 45, 0.3);
          backdrop-filter: blur(10px);
        }

        .aura-brand-name {
          font-family: 'Outfit', sans-serif;
          font-weight: 800;
          font-size: 1.4rem;
          background: linear-gradient(135deg, #fff 0%, #bf5af2 70%, #0a84ff 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .aura-messages-flow {
          flex: 1;
          overflow-y: auto;
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1.2rem;
        }

        .bubble-wrapper {
          display: flex;
          width: 100%;
        }
        .bubble-wrapper.user { justify-content: flex-end; }
        .bubble-wrapper.assistant { justify-content: flex-start; }

        .chat-bubble {
          max-width: 70%;
          padding: 1rem 1.25rem;
          border-radius: 16px;
          line-height: 1.5;
          font-size: 0.95rem;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
          position: relative;
        }

        .chat-bubble.user {
          background: linear-gradient(135deg, #8a2be2 0%, #bf5af2 100%);
          color: white;
          border-bottom-right-radius: 2px;
        }

        .chat-bubble.assistant {
          background: rgba(30, 41, 59, 0.7);
          color: #f5f5f7;
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-bottom-left-radius: 2px;
        }

        .bubble-meta {
          font-size: 0.75rem;
          color: rgba(255, 255, 255, 0.4);
          margin-top: 0.5rem;
          display: flex;
          justify-content: space-between;
        }

        .product-cards-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
          margin-top: 1rem;
          width: 100%;
        }

        .product-card {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 12px;
          padding: 0.75rem;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .product-card:hover {
          transform: translateY(-3px);
          border-color: #bf5af2;
        }

        .product-card-img {
          width: 100%;
          height: 120px;
          object-fit: contain;
          background: white;
          border-radius: 8px;
          padding: 4px;
        }

        .product-card-title {
          font-size: 0.85rem;
          font-weight: 600;
          color: #fff;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          height: 2.4rem;
        }

        .price-row {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }

        .discount-price {
          color: #0a84ff;
          font-weight: 700;
          font-size: 0.95rem;
        }

        .actual-price {
          color: rgba(255, 255, 255, 0.3);
          text-decoration: line-line-through;
          font-size: 0.8rem;
          text-decoration: line-through;
        }

        .rating-badge {
          background: rgba(255, 159, 10, 0.1);
          color: #ff9f0a;
          padding: 2px 6px;
          border-radius: 6px;
          font-size: 0.75rem;
          font-weight: 600;
          display: inline-block;
          width: fit-content;
        }

        .buy-btn {
          margin-top: auto;
          background: rgba(191, 90, 242, 0.15);
          color: #bf5af2;
          border: 1px solid rgba(191, 90, 242, 0.3);
          padding: 6px 12px;
          border-radius: 8px;
          text-align: center;
          text-decoration: none;
          font-size: 0.8rem;
          font-weight: 600;
          transition: background 0.2s;
        }
        .buy-btn:hover {
          background: #bf5af2;
          color: white;
        }

        /* Comparison layout */
        .comparison-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-top: 1rem;
        }

        .comparison-card {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 12px;
          padding: 1rem;
        }

        .compare-brand {
          font-family: 'Outfit', sans-serif;
          font-size: 1.1rem;
          font-weight: 600;
          color: #bf5af2;
          margin-bottom: 0.5rem;
        }

        .compare-metric {
          font-size: 0.85rem;
          margin-bottom: 0.3rem;
          color: #8e8e93;
        }

        .compare-metric span {
          color: #fff;
          font-weight: 600;
        }

        /* Suggestions chips */
        .aura-suggestions {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          background: rgba(22, 28, 45, 0.2);
          border-top: 1px solid rgba(255, 255, 255, 0.04);
        }

        .suggestion-chip {
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.08);
          color: rgba(255, 255, 255, 0.75);
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 0.8rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .suggestion-chip:hover {
          background: rgba(191, 90, 242, 0.15);
          border-color: #bf5af2;
          color: white;
        }

        .aura-chat-footer {
          padding: 1rem 1.5rem;
          border-top: 1px solid rgba(255, 255, 255, 0.08);
          background: rgba(22, 28, 45, 0.4);
          display: flex;
          gap: 1rem;
        }

        .aura-input-field {
          flex: 1;
          background: rgba(0, 0, 0, 0.25);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 0.75rem 1rem;
          color: white;
          font-size: 0.95rem;
          outline: none;
          transition: border-color 0.2s;
        }
        .aura-input-field:focus {
          border-color: #bf5af2;
        }

        .aura-send-btn {
          background: #bf5af2;
          border: none;
          color: white;
          border-radius: 12px;
          padding: 0 1.5rem;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }
        .aura-send-btn:hover {
          background: #8a2be2;
        }

        /* Typing dot animation */
        .typing-dots {
          display: flex;
          gap: 4px;
          padding: 4px 8px;
        }

        .typing-dot {
          width: 8px;
          height: 8px;
          background: #bf5af2;
          border-radius: 50%;
          animation: jump 1.4s infinite ease-in-out both;
        }
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes jump {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1.0); }
        }
      `}} />

      {/* Sidebar for Search History */}
      {showHistory && (
        <div className="aura-history-sidebar">
          <h3 className="font-semibold text-lg text-purple-400 mb-4 font-outfit">Session Searches</h3>
          {history.length === 0 ? (
            <div className="text-gray-500 text-sm italic">No history yet</div>
          ) : (
            <div className="flex flex-col gap-2">
              {history.map((h, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(h.query)}
                  className="text-left w-full p-2 rounded bg-white/5 hover:bg-purple-500/10 border border-white/5 hover:border-purple-500/35 transition text-sm text-gray-300 truncate"
                >
                  <div className="font-medium text-white truncate">{h.query}</div>
                  <div className="text-xs text-gray-500 truncate">Catalog: {h.routed_dataset}</div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Chat Area */}
      <div className="aura-chat-main">
        {/* Header */}
        <div className="aura-chat-header">
          <div className="flex items-center gap-3">
            <div className="aura-brand-name">AURA AI ASSISTANT</div>
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => setShowHistory(!showHistory)}
              className="bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-1.5 rounded-lg text-sm transition"
            >
              🕒 History
            </button>
            <a 
              href="/api/chatbot/analytics/dashboard" 
              target="_blank" 
              rel="noopener noreferrer"
              className="bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-1.5 rounded-lg text-sm transition no-underline text-white"
            >
              📊 Analytics Dashboard
            </a>
          </div>
        </div>

        {/* Message Flow */}
        <div className="aura-messages-flow">
          {messages.map((msg) => (
            <div key={msg.id} className={`bubble-wrapper ${msg.sender}`}>
              <div className={`chat-bubble ${msg.sender}`}>
                {renderMarkdown(msg.text)}

                {/* Show Products if Recommendation query */}
                {msg.products && msg.products.length > 0 && (
                  <div className="product-cards-grid">
                    {msg.products.map((p, pIdx) => {
                      const discPrice = String(p.discount_price).replace('₹', 'Rs.').trim();
                      const actPrice = String(p.actual_price).replace('₹', 'Rs.').trim();
                      return (
                        <div key={pIdx} className="product-card">
                          {p.image ? (
                            <img src={p.image} alt={p.name} className="product-card-img" />
                          ) : (
                            <div className="product-card-img flex items-center justify-center bg-gray-800 text-gray-400 font-semibold text-xs">No Image</div>
                          )}
                          <div className="product-card-title" title={p.name}>{p.name}</div>
                          {p.ratings && (
                            <div className="rating-badge">{p.clean_rating} ⭐ ({p.clean_no_of_ratings})</div>
                          )}
                          <div className="price-row">
                            <span className="discount-price">{discPrice}</span>
                            {actPrice && actPrice !== discPrice && (
                              <span className="actual-price">{actPrice}</span>
                            )}
                          </div>
                          <a href={p.link} target="_blank" rel="noopener noreferrer" className="buy-btn">View Product</a>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Show Comparison Details if Comparison Query */}
                {msg.comparison && (
                  <div className="flex flex-col gap-3 mt-4 w-full">
                    <div className="comparison-grid">
                      {/* Product A */}
                      {msg.comparison.product_a && (
                        <div className="comparison-card">
                          <div className="compare-brand">{msg.comparison.brand_a}</div>
                          <div className="text-sm font-semibold text-white mb-2 truncate" title={msg.comparison.product_a.name}>{msg.comparison.product_a.name}</div>
                          <div className="compare-metric">Price: <span>{String(msg.comparison.product_a.discount_price).replace('₹', 'Rs.')}</span></div>
                          <div className="compare-metric">Rating: <span>{msg.comparison.product_a.clean_rating} ⭐</span></div>
                          <div className="compare-metric">Reviews: <span>{msg.comparison.product_a.clean_no_of_ratings}</span></div>
                          <div className="mt-3">
                            <div className="text-xs font-bold text-green-400">PROS:</div>
                            {msg.comparison.comparison.pros[msg.comparison.brand_a].map((p, pi) => (
                              <div key={pi} className="text-xs text-gray-300">• {p}</div>
                            ))}
                          </div>
                          <div className="mt-2">
                            <div className="text-xs font-bold text-red-400">CONS:</div>
                            {msg.comparison.comparison.cons[msg.comparison.brand_a].map((c, ci) => (
                              <div key={ci} className="text-xs text-gray-300">• {c}</div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Product B */}
                      {msg.comparison.product_b && (
                        <div className="comparison-card">
                          <div className="compare-brand">{msg.comparison.brand_b}</div>
                          <div className="text-sm font-semibold text-white mb-2 truncate" title={msg.comparison.product_b.name}>{msg.comparison.product_b.name}</div>
                          <div className="compare-metric">Price: <span>{String(msg.comparison.product_b.discount_price).replace('₹', 'Rs.')}</span></div>
                          <div className="compare-metric">Rating: <span>{msg.comparison.product_b.clean_rating} ⭐</span></div>
                          <div className="compare-metric">Reviews: <span>{msg.comparison.product_b.clean_no_of_ratings}</span></div>
                          <div className="mt-3">
                            <div className="text-xs font-bold text-green-400">PROS:</div>
                            {msg.comparison.comparison.pros[msg.comparison.brand_b].map((p, pi) => (
                              <div key={pi} className="text-xs text-gray-300">• {p}</div>
                            ))}
                          </div>
                          <div className="mt-2">
                            <div className="text-xs font-bold text-red-400">CONS:</div>
                            {msg.comparison.comparison.cons[msg.comparison.brand_b].map((c, ci) => (
                              <div key={ci} className="text-xs text-gray-300">• {c}</div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Bubble Footer Metadata (Routed Dataset + Source) */}
                {msg.sender === 'assistant' && msg.routedDataset && (
                  <div className="bubble-meta">
                    <span>🗺️ Catalog: {msg.routedDataset}</span>
                    <span>Brain: {msg.source}</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Loading Typing Animation */}
          {loading && (
            <div className="bubble-wrapper assistant">
              <div className="chat-bubble assistant">
                <div className="typing-dots">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggestion Chips */}
        <div className="aura-suggestions">
          {suggestions.map((s, i) => (
            <button 
              key={i} 
              onClick={() => handleSend(s)}
              className="suggestion-chip"
            >
              {s}
            </button>
          ))}
        </div>

        {/* Input Footer */}
        <div className="aura-chat-footer">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
            placeholder="Type shopping query, e.g. best samsung phone under 20000..."
            className="aura-input-field"
            disabled={loading}
          />
          <button 
            onClick={() => handleSend(input)}
            className="aura-send-btn"
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};
