import { Search, Sun, Moon, Globe } from "lucide-react";
import { useTheme } from "@/contexts/ThemeContext";
import { useTemperature } from "@/contexts/TemperatureContext";
import { motion } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export function Header({ searchQuery, onSearchChange }: HeaderProps) {
  const { theme, toggleTheme } = useTheme();
  const { unit, toggleUnit } = useTemperature();

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="sticky top-0 z-50 backdrop-blur-md bg-background/80 border-b border-border shadow-sm"
    >
      <div className="container mx-auto px-4 h-16 flex items-center justify-between gap-2 md:gap-4">
        <motion.div
          className="flex items-center gap-2"
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Globe className="h-5 w-5 md:h-6 md:w-6 text-primary" />
          <h1 className="text-lg md:text-2xl font-bold bg-gradient-to-r from-primary via-chart-2 to-primary bg-clip-text text-transparent whitespace-nowrap">
            Weather Dashboard
          </h1>
        </motion.div>

        <div className="flex-1 max-w-md mx-2 md:mx-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search city..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-10 rounded-full bg-card border-card-border"
              data-testid="input-search-city"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={toggleUnit}
            className="px-3 min-w-[48px]"
            data-testid="button-unit-toggle"
          >
            {unit === "celsius" ? "°C" : "°F"}
          </Button>

          <motion.button
            onClick={toggleTheme}
            className="p-2 rounded-full hover-elevate active-elevate-2 bg-card border border-card-border"
            whileTap={{ scale: 0.95 }}
            data-testid="button-theme-toggle"
          >
            <motion.div
              initial={false}
              animate={{ rotate: theme === "dark" ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              {theme === "dark" ? (
                <Moon className="h-5 w-5 text-foreground" />
              ) : (
                <Sun className="h-5 w-5 text-foreground" />
              )}
            </motion.div>
          </motion.button>
        </div>
      </div>
    </motion.header>
  );
}
