import React from 'react';

interface ConfusionMatrixProps {
  matrix: number[][]; // [[TN, FP], [FN, TP]]
  title?: string;
}

export const ConfusionMatrixCard: React.FC<ConfusionMatrixProps> = ({
  matrix,
  title = 'Out-of-Sample Confusion Matrix',
}) => {
  if (!matrix || matrix.length < 2) return null;

  const tn = matrix[0]?.[0] || 0;
  const fp = matrix[0]?.[1] || 0;
  const fn = matrix[1]?.[0] || 0;
  const tp = matrix[1]?.[1] || 0;

  const total = tn + fp + fn + tp || 1;
  const accuracy = ((tp + tn) / total) * 100;
  const precision = (tp / (tp + fp || 1)) * 100;
  const recall = (tp / (tp + fn || 1)) * 100;

  return (
    <div className="card-surface p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          {title}
        </h4>
        <span className="text-xs font-mono text-emerald-400">
          Acc: {accuracy.toFixed(1)}%
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-center font-mono">
        <div className="bg-[#1E293B]/60 p-3 rounded-lg border border-emerald-500/20">
          <span className="text-[10px] text-slate-400 uppercase block">True DOWN (TN)</span>
          <span className="text-xl font-bold text-emerald-400">{tn}</span>
          <span className="text-[10px] text-slate-500 block">{((tn / total) * 100).toFixed(1)}%</span>
        </div>
        <div className="bg-[#1E293B]/60 p-3 rounded-lg border border-rose-500/20">
          <span className="text-[10px] text-slate-400 uppercase block">False UP (FP)</span>
          <span className="text-xl font-bold text-rose-400">{fp}</span>
          <span className="text-[10px] text-slate-500 block">{((fp / total) * 100).toFixed(1)}%</span>
        </div>
        <div className="bg-[#1E293B]/60 p-3 rounded-lg border border-rose-500/20">
          <span className="text-[10px] text-slate-400 uppercase block">False DOWN (FN)</span>
          <span className="text-xl font-bold text-rose-400">{fn}</span>
          <span className="text-[10px] text-slate-500 block">{((fn / total) * 100).toFixed(1)}%</span>
        </div>
        <div className="bg-[#1E293B]/60 p-3 rounded-lg border border-emerald-500/20">
          <span className="text-[10px] text-slate-400 uppercase block">True UP (TP)</span>
          <span className="text-xl font-bold text-emerald-400">{tp}</span>
          <span className="text-[10px] text-slate-500 block">{((tp / total) * 100).toFixed(1)}%</span>
        </div>
      </div>

      <div className="flex justify-between text-[11px] font-mono text-slate-400 mt-3 pt-2 border-t border-white/5">
        <span>Precision: <strong className="text-slate-200">{precision.toFixed(1)}%</strong></span>
        <span>Recall: <strong className="text-slate-200">{recall.toFixed(1)}%</strong></span>
      </div>
    </div>
  );
};
