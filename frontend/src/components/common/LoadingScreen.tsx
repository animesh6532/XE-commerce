import React from 'react';
import { Sparkles } from 'lucide-react';

export const LoadingScreen: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-900 text-slate-100 font-sans">
      <div className="flex flex-col items-center space-y-4">
        <div className="relative">
          <div className="h-16 w-16 animate-spin rounded-full border-4 border-t-blue-500 border-r-purple-500 border-b-pink-500 border-l-transparent"></div>
          <Sparkles className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-6 w-6 text-yellow-300 animate-pulse" />
        </div>
        <div className="text-center space-y-1">
          <h2 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            XE-Commerce
          </h2>
          <p className="text-xs text-slate-400">Loading platform components...</p>
        </div>
      </div>
    </div>
  );
};
