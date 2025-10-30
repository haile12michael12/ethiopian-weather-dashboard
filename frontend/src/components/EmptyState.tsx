import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Search } from "lucide-react";

interface EmptyStateProps {
  searchQuery: string;
}

export function EmptyState({ searchQuery }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="col-span-full"
    >
      <Card className="p-12 border border-card-border bg-muted/30">
        <div className="flex flex-col items-center justify-center text-center">
          <Search className="h-20 w-20 text-muted-foreground mb-4" />
          <h3 className="text-xl font-semibold text-foreground mb-2">
            No results found for "{searchQuery}"
          </h3>
          <p className="text-sm text-muted-foreground max-w-md">
            Try searching for a different city or check your spelling.
          </p>
        </div>
      </Card>
    </motion.div>
  );
}
