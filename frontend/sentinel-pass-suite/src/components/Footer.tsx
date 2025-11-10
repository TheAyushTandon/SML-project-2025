import { Github } from 'lucide-react';
import { motion } from 'framer-motion';

export const Footer = () => {

  return (
    <footer className="relative py-12 px-4 border-t border-primary/20">
      <div className="container max-w-6xl mx-auto">
        <div className="grid md:grid-cols-2 gap-8 items-center">
          {/* Left: Credits */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center md:text-left"
          >
            <p className="text-foreground/80">
              made by <span className="font-semibold gradient-text">team AI-Vault</span>
            </p>
          </motion.div>

          {/* Right: GitHub Link */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="flex gap-4 justify-center md:justify-end"
          >
            <motion.a
              href="https://github.com/TheAyushTandon/sentinel-pass-suite"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="glass p-3 rounded-xl hover:border-primary/50 transition-all group"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
            </motion.a>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="mt-8 pt-8 border-t border-primary/10 text-center"
        >
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Sentinel Pass. All rights reserved.
          </p>
        </motion.div>
      </div>
    </footer>
  );
};
