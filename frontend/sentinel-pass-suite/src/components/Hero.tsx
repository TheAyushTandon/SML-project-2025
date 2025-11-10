import { motion } from 'framer-motion';
import { Button } from './ui/button';
import { FloatingLock } from './FloatingLock';
import heroImage from '@/assets/hero-bg.jpg';

export const Hero = ({ onAnalyze, onGenerate }: { onAnalyze: () => void; onGenerate: () => void }) => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background image with overlay */}
      <div 
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `url(${heroImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: 0.3,
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-background via-background/80 to-background z-0" />

      <div className="container relative z-10 px-4 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
            >
              <h1 className="text-5xl md:text-7xl font-bold mb-4">
                <span className="gradient-text">Sentinel Pass</span>
              </h1>
              <p className="text-xl md:text-2xl text-muted-foreground">
                Enterprise-Grade Password Security Platform
              </p>
            </motion.div>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              className="text-lg text-foreground/80"
            >
              Advanced AI-powered password analysis and generation
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="flex flex-col sm:flex-row gap-4"
            >
              <Button
                variant="hero"
                size="lg"
                onClick={onAnalyze}
                className="text-lg"
              >
                Analyze Password
              </Button>
              <Button
                variant="neon-violet"
                size="lg"
                onClick={onGenerate}
                className="text-lg"
              >
                Generate Password
              </Button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.8 }}
              className="flex gap-8 pt-8"
            >
              <div className="text-center">
                <div className="text-3xl font-bold gradient-text">4</div>
                <div className="text-sm text-muted-foreground">AI Models</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold gradient-text">∞</div>
                <div className="text-sm text-muted-foreground">Passwords Analyzed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold gradient-text">99%</div>
                <div className="text-sm text-muted-foreground">Accuracy</div>
              </div>
            </motion.div>
          </motion.div>

          {/* Right - 3D Lock */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 1 }}
            className="relative"
          >
            <div className="relative z-10">
              <FloatingLock />
            </div>
            <div className="absolute inset-0 bg-gradient-radial from-primary/20 via-transparent to-transparent blur-3xl" />
          </motion.div>
        </div>
      </div>
    </section>
  );
};
