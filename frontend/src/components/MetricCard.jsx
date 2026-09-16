import React from 'react';

export default function MetricCard({ title, value, subtitle, icon: Icon, trend, color = 'blue' }) {
  // Pure bg-white data card with border-brand-sage and sharp semantic left border
  const borderAccents = {
    blue: 'border-l-4 border-l-blue-600',
    red: 'border-l-4 border-l-red-600',
    amber: 'border-l-4 border-l-amber-500',
    emerald: 'border-l-4 border-l-emerald-600',
    green: 'border-l-4 border-l-emerald-600',
  };

  const textColors = {
    blue: 'text-blue-900',
    red: 'text-red-700',
    amber: 'text-amber-700',
    emerald: 'text-emerald-700',
    green: 'text-emerald-700',
  };

  const iconColors = {
    blue: 'text-blue-700 bg-blue-50',
    red: 'text-red-700 bg-red-50',
    amber: 'text-amber-700 bg-amber-50',
    emerald: 'text-emerald-700 bg-emerald-50',
    green: 'text-emerald-700 bg-emerald-50',
  };

  const borderClass = borderAccents[color] || borderAccents.blue;
  const textClass = textColors[color] || textColors.blue;
  const iconClass = iconColors[color] || iconColors.blue;

  return (
    <div className={`p-4 bg-white rounded-md border border-brand-sage ${borderClass} shadow-sm transition-all hover:border-brand-bronze/60`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-brand-navy">
          {title}
        </span>
        <div className={`p-1.5 rounded ${iconClass}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-2.5 flex items-baseline gap-2">
        <span className={`text-2xl font-black tracking-tight ${textClass}`}>
          {value}
        </span>
        {trend && (
          <span className="text-xs font-semibold text-slate-500">
            {trend}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="mt-1 text-xs text-slate-600 font-medium">
          {subtitle}
        </p>
      )}
    </div>
  );
}
