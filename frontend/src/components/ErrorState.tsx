import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CloudOff, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message = "Failed to load weather data", onRetry }: ErrorStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="col-span-full"
    >
      <Card className="p-12 border border-card-border bg-muted/30">
        <div className="flex flex-col items-center justify-center text-center">
          <motion.div
            initial={{ rotate: 0 }}
            animate={{ rotate: [0, -10, 10, -10, 0] }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <CloudOff className="h-20 w-20 text-muted-foreground mb-4" />
          </motion.div>
          <h3 className="text-xl font-semibold text-foreground mb-2">Oops! Something went wrong</h3>
          <p className="text-sm text-muted-foreground mb-6 max-w-md">
            {message}
          </p>
          {onRetry && (
            <Button onClick={onRetry} variant="default" className="gap-2" data-testid="button-retry">
              <RefreshCw className="h-4 w-4" />
              Try Again
            </Button>
          )}
        </div>
      </Card>
    </motion.div>
  );
}
