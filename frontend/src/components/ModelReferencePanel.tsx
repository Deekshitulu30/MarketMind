import React, { useState } from 'react';
import {
  ShieldAlert,
  HelpCircle,
  Eye,
  EyeOff,
  TrendingUp,
  TrendingDown,
  Target,
  Shield,
  Activity,
  Layers,
  CheckCircle2,
  X,
  BookOpen
} from 'lucide-react';
import { ModelReferenceLevelsPayload } from '../types';

interface ModelReferencePanelProps {
  symbol: string;
  currency?: string;
  referenceData?: ModelReferenceLevelsPayload | null;
  currentPrice?: number;
}

export const ModelReferencePanel: React.FC<ModelReferencePanelProps> = ({
  symbol,
  currency = 'USD',
  referenceData,
  currentPrice,
}) => {
  // RULE 5: Switch OFF by default on initial render / session
  const [showReferenceLevels, setShowReferenceLevels] = useState<boolean>(false);
  const [showMethodologyModal, setShowMethodologyModal] = useState<boolean>(false);

  const currSymbol = currency === 'INR' || symbol.includes('.NS') || (!symbol.includes('.') && symbol.length > 4) ? '₹' : '$';

  if (!referenceData) {
    return null;
  }

  const isUp = referenceData.direction === 'UP';
  const targetVal = referenceData.reference_target.value;
  const stopLossVal = referenceData.reference_stop_loss.value;
  const predPrice = referenceData.predicted_price;
  const atrVal = referenceData.atr_14;
  const kMult = referenceData.multipliers.target_k;
  const mMult = referenceData.multipliers.stop_loss_m;

  return (
    <div className="card-surface p-5 rounded-2xl border border-white/10 space-y-4 relative shadow-2xl bg-gradient-to-b from-[#111827] to-[#0B0F17]">
      {/* Top Banner & Session Toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/5">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight flex items-center space-x-2">
              <span>Model-Derived Reference Panel</span>
              <span className="text-[10px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                Educational Only
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Statistical volatility bounds anchored to model expectation
            </p>
          </div>
        </div>

        {/* RULE 5: Explicit Opt-In Toggle */}
        <button
          onClick={() => setShowReferenceLevels(!showReferenceLevels)}
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all border ${
            showReferenceLevels
              ? 'bg-blue-600/20 text-blue-300 border-blue-500/40 hover:bg-blue-600/30'
              : 'bg-white/5 text-slate-300 border-white/10 hover:bg-white/10'
          }`}
        >
          {showReferenceLevels ? <EyeOff className="w-3.5 h-3.5 text-blue-400" /> : <Eye className="w-3.5 h-3.5 text-slate-400" />}
          <span>{showReferenceLevels ? 'Hide Reference Levels' : 'Show educational reference levels'}</span>
        </button>
      </div>

      {/* Gated Content */}
      {!showReferenceLevels ? (
        <div className="py-8 px-4 rounded-xl border border-dashed border-white/10 bg-[#0B0F17]/60 text-center space-y-3">
          <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-slate-400 border border-white/5">
            <EyeOff className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h4 className="text-xs font-semibold text-slate-200">
              Educational Reference Levels Hidden
            </h4>
            <p className="text-[11px] text-slate-400 max-w-sm mx-auto leading-relaxed">
              In adherence with educational research framing standards, model reference targets and stop-losses require an explicit session opt-in toggle.
            </p>
          </div>
          <button
            onClick={() => setShowReferenceLevels(true)}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-all inline-flex items-center space-x-1.5"
          >
            <span>Show educational reference levels</span>
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Main Sibling Card - RULES 1 & 2 */}
          <div className="p-4 rounded-xl bg-[#0B0F17] border border-white/10 space-y-4">
            {/* Context Header: Model Version & Direction Confidence */}
            <div className="flex items-center justify-between text-xs font-mono pb-2 border-b border-white/5">
              <div className="flex items-center space-x-2 text-slate-400">
                <Layers className="w-3.5 h-3.5 text-indigo-400" />
                <span>Model: <strong className="text-white">{referenceData.model_version}</strong></span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-slate-400">Directional Confidence:</span>
                <span className={`px-2 py-0.5 rounded font-bold ${isUp ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'}`}>
                  {referenceData.direction} ({referenceData.confidence_pct}%)
                </span>
              </div>
            </div>

            {/* Level Values Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Predicted Price */}
              <div className="p-3 rounded-lg bg-[#111827] border border-white/5 space-y-1">
                <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block">
                  Model Expected Price
                </span>
                <div className="text-lg font-extrabold font-mono text-white">
                  {currSymbol}{predPrice.toFixed(2)}
                </div>
                <span className="text-[10px] text-slate-400 font-mono block">
                  Expected Return: {referenceData.expected_return_pct >= 0 ? '+' : ''}{referenceData.expected_return_pct.toFixed(2)}%
                </span>
              </div>

              {/* RULE 1: Exact UI Label "Model Reference Target (educational)" */}
              <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/30 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-semibold text-emerald-400 font-sans">
                    Model Reference Target (educational)
                  </span>
                  <Target className="w-3.5 h-3.5 text-emerald-400" />
                </div>
                <div className="text-lg font-extrabold font-mono text-emerald-300">
                  {currSymbol}{targetVal.toFixed(2)}
                </div>
                <span className="text-[10px] text-emerald-400/80 font-mono block">
                  +{kMult}× ATR ({currSymbol}{referenceData.reference_target.buffer.toFixed(2)})
                </span>
              </div>

              {/* RULE 1: Exact UI Label "Model Reference Stop-Loss (educational)" */}
              <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/30 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-semibold text-rose-400 font-sans">
                    Model Reference Stop-Loss (educational)
                  </span>
                  <Shield className="w-3.5 h-3.5 text-rose-400" />
                </div>
                <div className="text-lg font-extrabold font-mono text-rose-300">
                  {currSymbol}{stopLossVal.toFixed(2)}
                </div>
                <span className="text-[10px] text-rose-400/80 font-mono block">
                  -{mMult}× ATR ({currSymbol}{referenceData.reference_stop_loss.buffer.toFixed(2)})
                </span>
              </div>
            </div>

            {/* ATR Volatility & Multipliers Metadata */}
            <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-lg bg-white/[0.02] border border-white/5 text-[11px] font-mono text-slate-400">
              <div className="flex items-center space-x-3">
                <span>14-Day ATR: <strong className="text-slate-200">{currSymbol}{atrVal.toFixed(2)}</strong></span>
                <span>Risk/Reward Ratio: <strong className="text-slate-200">{referenceData.risk_reward_ratio}:1</strong></span>
              </div>
              
              {/* RULE 4: "How is this calculated?" Link */}
              <button
                onClick={() => setShowMethodologyModal(true)}
                className="flex items-center space-x-1 text-blue-400 hover:text-blue-300 transition-colors font-sans underline underline-offset-2 cursor-pointer"
              >
                <HelpCircle className="w-3.5 h-3.5" />
                <span>How is this calculated?</span>
              </button>
            </div>

            {/* RULE 2: Mandatory Sentence - Same Card / Same Glance */}
            <div className="flex items-start space-x-2 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300/90 text-xs">
              <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <p className="leading-relaxed font-sans font-medium">
                {referenceData.mandatory_disclaimer}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* RULE 4: Methodology Modal */}
      {showMethodologyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-[#111827] border border-white/10 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <div className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-blue-400" />
                <h3 className="text-base font-bold text-white">How Are Reference Levels Calculated?</h3>
              </div>
              <button
                onClick={() => setShowMethodologyModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-300 leading-relaxed font-sans">
              <p>
                These levels are derived from standard <strong>Average True Range (ATR)</strong> volatility dispersion metrics applied to the machine-learning model's projected price, serving strictly as a statistical risk framing exercise.
              </p>

              <div className="p-3.5 rounded-xl bg-[#0B0F17] border border-white/5 font-mono text-[11px] space-y-2 text-slate-300">
                <div className="text-blue-400 font-semibold">1. Projected Anchor Price:</div>
                <div>Predicted Price = Last Close × (1 + Model Expected Return)</div>

                <div className="text-emerald-400 font-semibold pt-1">2. Model Reference Target:</div>
                <div>Target = Predicted Price + ({kMult} × 14-Day ATR) [for UP direction]</div>

                <div className="text-rose-400 font-semibold pt-1">3. Model Reference Stop-Loss:</div>
                <div>Stop-Loss = Predicted Price − ({mMult} × 14-Day ATR) [for UP direction]</div>
              </div>

              <div className="space-y-1.5 text-slate-400 text-[11px]">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>Uses 14-period Average True Range ({currSymbol}{atrVal.toFixed(2)}) based on high/low intraday spreads.</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>Explicit multipliers: Target multiplier $k = {kMult}$, Stop-Loss multiplier $m = {mMult}$.</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  <span>Educational mathematical illustration. Not a trading signal or financial recommendation.</span>
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setShowMethodologyModal(false)}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-all"
              >
                Close Explanation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
