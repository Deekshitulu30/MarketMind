import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  TrendingUp,
  LineChart,
  Brain,
  Sliders,
  History,
  Info,
  BarChart2,
  PieChart,
  Layers,
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: 'Market Overview', icon: TrendingUp, section: 'Exploration' },
  { path: '/explorer', label: 'Stock Explorer', icon: LineChart, section: 'Exploration' },
  { path: '/statistics', label: 'Statistics Lab', icon: BarChart2, section: 'Quantitative Analysis' },
  { path: '/predictions', label: 'Predictions', icon: Brain, section: 'Machine Learning' },
  { path: '/models', label: 'Model Lab', icon: Layers, section: 'Machine Learning' },
  { path: '/explainability', label: 'Explainability & SHAP', icon: Info, section: 'Interpretability' },
  { path: '/backtesting', label: 'Walk-Forward Backtest', icon: History, section: 'Evaluation' },
  { path: '/what-if', label: 'What-If Simulator', icon: Sliders, section: 'Scenario Analysis' },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-[#0B0F17] border-r border-white/5 flex flex-col h-screen sticky top-0">
      {/* Brand Header */}
      <div className="p-6 border-b border-white/5 flex items-center space-x-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <TrendingUp className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-base tracking-tight text-white flex items-center space-x-1.5">
            <span>MarketMind</span>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              v1.0
            </span>
          </h1>
          <p className="text-[11px] text-slate-400">Explainable Intelligence</p>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        <div>
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 px-3 block mb-2">
            Workspace
          </span>
          <nav className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-blue-600/15 text-blue-400 border border-blue-500/20 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-white/5 bg-[#080C12]">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span>Engine Status</span>
          <span className="flex items-center space-x-1 text-emerald-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Online</span>
          </span>
        </div>
      </div>
    </aside>
  );
};
