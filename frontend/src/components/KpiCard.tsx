import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

export interface KpiCardProps {
  title?: string;
  label?: string;
  value: string | number;
  subtitle?: string;
  subtext?: string;
  icon?: LucideIcon | React.ReactNode;
  trend?: 'up' | 'down' | 'neutral' | 'positive' | 'negative';
  trendValue?: string;
  tooltip?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  label,
  value,
  subtitle,
  subtext,
  icon,
  trend,
  trendValue,
  tooltip,
}) => {
  const displayTitle = title || label || '';
  const displaySubtitle = subtitle || subtext || '';

  const isUp = trend === 'up' || trend === 'positive';
  const isDown = trend === 'down' || trend === 'negative';

  const renderIcon = () => {
    if (!icon) return null;
    if (React.isValidElement(icon)) {
      return <div className="text-slate-400">{icon}</div>;
    }
    const IconComp = icon as LucideIcon;
    return <IconComp className="w-4 h-4 text-slate-400" />;
  };

  return (
    <div className="card-surface p-5 hover:border-white/10 transition-colors" title={tooltip}>
      <div className="flex items-center justify-between mb-2">
        <span className="stat-label">{displayTitle}</span>
        {renderIcon()}
      </div>
      <div className="flex items-baseline space-x-2">
        <div className="text-2xl font-bold font-mono text-slate-100">{value}</div>
        {trend && (
          <div
            className={`flex items-center text-xs font-mono font-medium ${
              isUp ? 'text-emerald-400' : isDown ? 'text-rose-400' : 'text-slate-400'
            }`}
          >
            {isUp && <TrendingUp className="w-3 h-3 mr-0.5" />}
            {isDown && <TrendingDown className="w-3 h-3 mr-0.5" />}
            {trendValue}
          </div>
        )}
      </div>
      {displaySubtitle && <p className="text-xs text-slate-400 mt-1">{displaySubtitle}</p>}
    </div>
  );
};
