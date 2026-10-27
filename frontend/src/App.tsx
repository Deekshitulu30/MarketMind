import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { MarketOverview } from './pages/MarketOverview';
import { StockExplorer } from './pages/StockExplorer';
import { StatisticsLab } from './pages/StatisticsLab';
import { PredictionPage } from './pages/PredictionPage';
import { ModelLab } from './pages/ModelLab';
import { ExplainabilityPage } from './pages/ExplainabilityPage';
import { BacktestingPage } from './pages/BacktestingPage';
import { WhatIfSimulatorPage } from './pages/WhatIfSimulatorPage';

export const App: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AAPL');

  return (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <DashboardLayout
              selectedSymbol={selectedSymbol}
              onSymbolChange={setSelectedSymbol}
            />
          }
        >
          <Route
            path="/"
            element={<MarketOverview onSelectSymbol={setSelectedSymbol} />}
          />
          <Route
            path="/explorer"
            element={<StockExplorer symbol={selectedSymbol} />}
          />
          <Route
            path="/statistics"
            element={<StatisticsLab symbol={selectedSymbol} />}
          />
          <Route
            path="/predictions"
            element={<PredictionPage symbol={selectedSymbol} />}
          />
          <Route
            path="/models"
            element={<ModelLab symbol={selectedSymbol} />}
          />
          <Route
            path="/explainability"
            element={<ExplainabilityPage symbol={selectedSymbol} />}
          />
          <Route
            path="/backtesting"
            element={<BacktestingPage symbol={selectedSymbol} />}
          />
          <Route
            path="/what-if"
            element={<WhatIfSimulatorPage symbol={selectedSymbol} />}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
export default App;
