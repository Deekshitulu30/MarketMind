import React from 'react';
import { Calendar, ShieldAlert } from 'lucide-react';
import { StockSearchBar } from './StockSearchBar';

interface NavbarProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  availableSymbols?: string[];
  startDate?: string;
  endDate?: string;
  onDateChange?: (start: string, end: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  selectedSymbol,
  onSymbolChange,
}) => {
  return (
    <header className="h-16 bg-[#0B0F17]/90 backdrop-blur-md border-b border-white/5 px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Whole-Exchange Stock Search & Quick Selector */}
      <div className="flex items-center space-x-3">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider hidden sm:inline">
          Active Stock:
        </span>
        <StockSearchBar
          selectedSymbol={selectedSymbol}
          onSymbolChange={onSymbolChange}
        />
      </div>

      {/* Dataset Scope Indicator & Disclaimer Pill */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        <div className="hidden md:flex items-center space-x-2 text-xs text-slate-400 bg-[#111827] px-3 py-1.5 rounded-lg border border-white/5">
          <Calendar className="w-3.5 h-3.5 text-blue-400" />
          <span>Whole-Exchange Sync & Historical Horizon</span>
        </div>
        <div className="flex items-center space-x-1.5 text-[11px] text-amber-400/90 bg-amber-500/10 px-2.5 py-1 rounded-md border border-amber-500/20">
          <ShieldAlert className="w-3 h-3" />
          <span>Academic & Research Sandbox</span>
        </div>
      </div>
    </header>
  );
};
