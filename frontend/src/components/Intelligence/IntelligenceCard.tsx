import React from "react";
import { cn } from "@/lib/utils";
import { AlertCircle, Info, ShieldAlert, AlertTriangle } from "lucide-react";

export type IntelligenceSeverity = "INFO" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

interface IntelligenceCardProps {
  severity: IntelligenceSeverity;
  title: string;
  source: string;
  timestamp: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  className?: string;
}

export function IntelligenceCard({
  severity,
  title,
  source,
  timestamp,
  description,
  actionText,
  onAction,
  className,
}: IntelligenceCardProps) {
  const getSeverityConfig = (sev: IntelligenceSeverity) => {
    switch (sev) {
      case "CRITICAL":
        return {
          wrapper: "border-destructive/40 bg-destructive/5 hover:border-destructive/60",
          badge: "bg-destructive/10 text-destructive border-destructive/30",
          icon: <ShieldAlert className="h-4 w-4 text-destructive" />,
          titleColor: "text-destructive",
        };
      case "HIGH":
        return {
          wrapper: "border-amber-500/40 bg-amber-500/5 hover:border-amber-500/60",
          badge: "bg-amber-500/10 text-amber-500 border-amber-500/30",
          icon: <AlertTriangle className="h-4 w-4 text-amber-500" />,
          titleColor: "text-amber-500",
        };
      case "MEDIUM":
        return {
          wrapper: "border-yellow-500/40 bg-yellow-500/5 hover:border-yellow-500/60",
          badge: "bg-yellow-500/10 text-yellow-500 border-yellow-500/30",
          icon: <AlertCircle className="h-4 w-4 text-yellow-500" />,
          titleColor: "text-yellow-500",
        };
      case "LOW":
        return {
          wrapper: "border-emerald-500/40 bg-emerald-500/5 hover:border-emerald-500/60",
          badge: "bg-emerald-500/10 text-emerald-500 border-emerald-500/30",
          icon: <Info className="h-4 w-4 text-emerald-500" />,
          titleColor: "text-emerald-500",
        };
      default:
        return {
          wrapper: "border-border/60 bg-secondary/30 hover:border-border",
          badge: "bg-secondary text-muted-foreground border-border",
          icon: <Info className="h-4 w-4 text-muted-foreground" />,
          titleColor: "text-foreground",
        };
    }
  };

  const config = getSeverityConfig(severity);

  return (
    <div
      className={cn(
        "group flex flex-col justify-between rounded-xl border p-4 transition-all duration-200",
        config.wrapper,
        className
      )}
    >
      <div>
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            {config.icon}
            <h4 className={cn("font-semibold tracking-tight text-sm", config.titleColor)}>
              {title}
            </h4>
          </div>
          <span
            className={cn(
              "rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest",
              config.badge
            )}
          >
            {severity}
          </span>
        </div>
        
        <p className="text-sm text-muted-foreground leading-relaxed mb-4">
          {description}
        </p>
      </div>

      <div className="mt-auto flex items-center justify-between border-t border-border/50 pt-3">
        <div className="flex flex-col gap-0.5">
          <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Source</span>
          <span className="text-xs font-mono text-foreground">{source}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] text-muted-foreground font-mono">{timestamp}</span>
          {actionText && onAction && (
            <button
              onClick={onAction}
              className="text-[10px] font-bold text-primary hover:text-primary/80 transition-colors uppercase tracking-wider"
            >
              {actionText}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
