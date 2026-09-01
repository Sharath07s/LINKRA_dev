import React from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "./button";

interface ErrorStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  onRetry?: () => void;
  icon?: React.ReactNode;
}

export function ErrorState({
  title = "System Error",
  description = "An error occurred while loading this intelligence component.",
  onRetry,
  icon = <AlertTriangle className="h-8 w-8 text-destructive" />,
  className,
  ...props
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "flex min-h-[300px] flex-col items-center justify-center rounded-xl border border-destructive/30 bg-destructive/5 p-8 text-center",
        className
      )}
      {...props}
    >
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10 border border-destructive/20 shadow-inner">
        {icon}
      </div>
      <h3 className="mt-5 text-base font-semibold text-foreground tracking-tight">{title}</h3>
      <p className="mt-1.5 mb-6 max-w-sm text-sm text-muted-foreground leading-relaxed">{description}</p>
      
      {onRetry && (
        <Button 
          variant="outline" 
          onClick={onRetry}
          className="border-destructive/30 bg-transparent text-destructive hover:bg-destructive/10 hover:text-destructive"
        >
          <RefreshCcw className="mr-2 h-4 w-4" />
          Retry Connection
        </Button>
      )}
    </div>
  );
}
