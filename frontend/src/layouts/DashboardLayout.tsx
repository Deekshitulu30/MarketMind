import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Navbar } from '../components/Navbar';
import { FinancialDisclaimer } from '../components/FinancialDisclaimer';

import { ErrorBoundary } from '../components/ErrorBoundary';

interface DashboardLayoutProps {
  selectedSymbol: string;
  onSymbolChange: (sym: string) => void;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  selectedSymbol,
  onSymbolChange,
}) => {
  return (
    <div className="flex h-screen bg-[#0B0F17] text-slate-100 overflow-hidden font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <Navbar selectedSymbol={selectedSymbol} onSymbolChange={onSymbolChange} />
        <main className="flex-1 p-8 max-w-7xl w-full mx-auto space-y-6">
          <ErrorBoundary fallbackTitle="Component Error">
            <Outlet />
          </ErrorBoundary>
          <FinancialDisclaimer />
        </main>
      </div>
    </div>
  );
};
