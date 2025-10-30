import { motion } from "framer-motion";
import { Heart } from "lucide-react";

export function Footer() {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6, delay: 0.6 }}
      className="py-6 text-center border-t border-border"
    >
      <p className="text-sm text-muted-foreground flex items-center justify-center gap-2">
        Built with
        <Heart className="h-4 w-4 text-destructive fill-destructive" />
        using React + FastAPI
      </p>
    </motion.footer>
  );
}
