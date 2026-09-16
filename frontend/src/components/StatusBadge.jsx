import React from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, Clock, HelpCircle } from 'lucide-react';

export default function StatusBadge({ status, size = 'md', showIcon = true, textOverride = null }) {
  const normStatus = (status || '').toLowerCase();

  const configs = {
    compliant: {
      bg: 'bg-emerald-100',
      text: 'text-emerald-800',
      border: 'border-emerald-300',
      label: 'COMPLIANT',
      icon: CheckCircle2,
    },
    violation: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-200',
      label: 'VIOLATION DETECTED',
      icon: AlertOctagon,
    },
    review: {
      bg: 'bg-amber-100',
      text: 'text-amber-800',
      border: 'border-amber-300',
      label: 'REVIEW REQUIRED',
      icon: AlertTriangle,
    },
    processing: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      border: 'border-blue-200',
      label: 'PROCESSING',
      icon: Clock,
    },
    waived: {
      bg: 'bg-slate-100',
      text: 'text-slate-800',
      border: 'border-slate-300',
      label: 'OVERRIDDEN / WAIVED',
      icon: HelpCircle,
    }
  };

  const config = configs[normStatus] || configs.review;
  const Icon = config.icon;

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5 font-bold tracking-wide gap-1 rounded',
    md: 'text-xs px-2.5 py-0.5 font-bold tracking-wide gap-1.5 rounded',
    lg: 'text-xs px-3 py-1 font-bold tracking-wider gap-1.5 rounded-md',
    banner: 'text-sm px-3.5 py-1.5 font-extrabold tracking-wider gap-2 rounded-md'
  };

  return (
    <span
      className={`inline-flex items-center border font-mono uppercase ${config.bg} ${config.text} ${config.border} ${sizeStyles[size] || sizeStyles.md}`}
    >
      {showIcon && (
        <Icon className={size === 'banner' ? 'w-4 h-4 flex-shrink-0' : 'w-3.5 h-3.5 flex-shrink-0'} />
      )}
      <span>{textOverride || config.label}</span>
    </span>
  );
}
