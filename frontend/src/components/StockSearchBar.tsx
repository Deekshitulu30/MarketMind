import React, { useState, useEffect, useRef } from 'react';
import { Search, Globe, ChevronRight, X, Building2, Sparkles, TrendingUp } from 'lucide-react';
import { api } from '../services/api';
import { StockSearchResult } from '../types';

interface StockSearchBarProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
}

const POPULAR_SHORTLIST = [
  { symbol: 'AAPL', name: 'Apple', exchange: 'NASDAQ' },
  { symbol: 'NVDA', name: 'NVIDIA', exchange: 'NASDAQ' },
  { symbol: 'MSFT', name: 'Microsoft', exchange: 'NASDAQ' },
  { symbol: 'RELIANCE', name: 'Reliance Ind.', exchange: 'NSE' },
  { symbol: 'TCS', name: 'TCS', exchange: 'NSE' },
  { symbol: 'INFY', name: 'Infosys', exchange: 'NSE' },
  { symbol: 'SPY', name: 'S&P 500 ETF', exchange: 'NYSE' },
  { symbol: 'TSLA', name: 'Tesla', exchange: 'NASDAQ' },
];

export const StockSearchBar: React.FC<StockSearchBarProps> = ({
  selectedSymbol,
  onSymbolChange,
}) => {
  const [query, setQuery] = useState<string>('');
  const [exchangeFilter, setExchangeFilter] = useState<string>('ALL');
  const [results, setResults] = useState<StockSearchResult[]>([]);
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch search results on query / filter change with debounce
  useEffect(() => {
    if (!isOpen) return;

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const data = await api.searchStocks(query, exchangeFilter === 'ALL' ? undefined : exchangeFilter, 25);
        setResults(data);
        setSelectedIndex(-1);
      } catch (err) {
        console.error('Failed to search stocks:', err);
      } finally {
        setIsLoading(false);
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [query, exchangeFilter, isOpen]);

  const handleSelect = (sym: string) => {
    onSymbolChange(sym);
    setQuery('');
    setIsOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        setIsOpen(true);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < results.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : 0));
    } else if (e.key === 'Enter' && selectedIndex >= 0 && selectedIndex < results.length) {
      e.preventDefault();
      handleSelect(results[selectedIndex].symbol);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div ref={containerRef} className="relative flex items-center space-x-3">
      {/* Search Input Container */}
      <div className="relative w-72 lg:w-96">
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onFocus={() => setIsOpen(true)}
            onChange={(e) => {
              setQuery(e.target.value);
              setIsOpen(true);
            }}
            onKeyDown={handleKeyDown}
            placeholder={`Active: ${selectedSymbol} | Search all NSE & US equities...`}
            className="w-full pl-9 pr-8 py-1.5 bg-[#111827] text-xs font-mono text-white placeholder:text-slate-500 rounded-xl border border-white/10 focus:outline-none focus:border-blue-500/60 focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner"
          />
          {query && (
            <button
              onClick={() => {
                setQuery('');
                inputRef.current?.focus();
              }}
              className="absolute right-2.5 p-0.5 text-slate-400 hover:text-white rounded-md transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Dropdown Popup */}
        {isOpen && (
          <div className="absolute top-full left-0 mt-2 w-[420px] max-w-[90vw] bg-[#111827] border border-white/10 rounded-2xl shadow-2xl z-50 overflow-hidden backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150">
            {/* Filter Tabs */}
            <div className="flex items-center justify-between px-3 py-2 bg-[#0B0F17] border-b border-white/5 text-[11px]">
              <div className="flex items-center space-x-1">
                {['ALL', 'NSE', 'NASDAQ', 'NYSE'].map((ex) => (
                  <button
                    key={ex}
                    onClick={() => setExchangeFilter(ex)}
                    className={`px-2 py-0.5 rounded-md font-medium transition-all ${
                      exchangeFilter === ex
                        ? 'bg-blue-600 text-white'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                    }`}
                  >
                    {ex}
                  </button>
                ))}
              </div>
              <span className="text-[10px] text-slate-500 font-mono">
                {results.length} results
              </span>
            </div>

            {/* Quick Popular Shortlist when search is empty */}
            {!query && (
              <div className="p-3 border-b border-white/5 bg-white/[0.01]">
                <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider flex items-center space-x-1 mb-2">
                  <Sparkles className="w-3 h-3 text-amber-400" />
                  <span>Popular Benchmark Equities</span>
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {POPULAR_SHORTLIST.map((item) => (
                    <button
                      key={item.symbol}
                      onClick={() => handleSelect(item.symbol)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-mono font-medium transition-all border ${
                        selectedSymbol === item.symbol
                          ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                          : 'bg-[#0B0F17] text-slate-300 border-white/5 hover:border-blue-500/40 hover:bg-white/5'
                      }`}
                    >
                      <span className="font-bold">{item.symbol}</span>
                      <span className="text-[10px] text-slate-400 ml-1.5 opacity-80">
                        {item.exchange}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Results List */}
            <div className="max-h-72 overflow-y-auto divide-y divide-white/5">
              {isLoading ? (
                <div className="p-6 text-center text-xs text-slate-400">
                  Searching whole-exchange directory...
                </div>
              ) : results.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-400 space-y-1">
                  <p>No listed equities found matching "{query}".</p>
                  <p className="text-[11px] text-slate-500">
                    Try searching by ticker symbol (e.g. RELIANCE, TCS, NVDA) or company name.
                  </p>
                </div>
              ) : (
                results.map((item, idx) => {
                  const isSelected = idx === selectedIndex;
                  const isCurrentActive = item.symbol === selectedSymbol;

                  return (
                    <div
                      key={item.symbol}
                      onClick={() => handleSelect(item.symbol)}
                      className={`px-3.5 py-2.5 flex items-center justify-between cursor-pointer transition-all ${
                        isSelected || isCurrentActive
                          ? 'bg-blue-600/15 text-white'
                          : 'hover:bg-white/5 text-slate-300'
                      }`}
                    >
                      <div className="flex items-center space-x-3 min-w-0">
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-mono font-bold shrink-0 ${
                            item.exchange === 'NSE'
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                          }`}
                        >
                          {item.exchange === 'NSE' ? '₹' : '$'}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-xs font-mono text-white tracking-wide">
                              {item.symbol}
                            </span>
                            <span className="text-[9px] px-1.5 py-0.2 rounded font-mono bg-white/5 text-slate-400 border border-white/10">
                              {item.exchange}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 truncate max-w-[240px]">
                            {item.company_name}
                          </p>
                        </div>
                      </div>

                      <div className="text-right shrink-0 flex items-center space-x-2">
                        {item.sector && (
                          <span className="text-[10px] text-slate-500 hidden sm:inline max-w-[100px] truncate">
                            {item.sector}
                          </span>
                        )}
                        <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Bottom info */}
            <div className="px-3 py-1.5 bg-[#0B0F17] border-t border-white/5 text-[10px] text-slate-500 font-mono flex justify-between items-center">
              <span>Whole-exchange search with on-demand price sync</span>
              <span>Use ↑↓ to navigate, Enter to select</span>
            </div>
          </div>
        )}
      </div>

      {/* Quick Pills for Active Selection */}
      <div className="hidden xl:flex items-center space-x-1.5 bg-[#111827] p-1 rounded-xl border border-white/10">
        {POPULAR_SHORTLIST.slice(0, 6).map((item) => (
          <button
            key={item.symbol}
            onClick={() => onSymbolChange(item.symbol)}
            className={`px-2.5 py-0.5 rounded-lg text-xs font-mono font-medium transition-all ${
              selectedSymbol === item.symbol
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
            }`}
          >
            {item.symbol}
          </button>
        ))}
      </div>
    </div>
  );
};
