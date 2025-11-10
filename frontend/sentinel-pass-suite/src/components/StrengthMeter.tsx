import { motion } from 'framer-motion';
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';

interface StrengthMeterProps {
  strength: 'weak' | 'medium' | 'strong';
  probabilities: {
    weak: number;
    medium: number;
    strong: number;
  };
}

export const StrengthMeter = ({ strength, probabilities }: StrengthMeterProps) => {
  const getColor = (level: string) => {
    switch (level) {
      case 'weak': return 'hsl(0, 84%, 60%)';
      case 'medium': return 'hsl(45, 100%, 50%)';
      case 'strong': return 'hsl(120, 100%, 40%)';
      default: return 'hsl(var(--muted))';
    }
  };

  const getIcon = () => {
    switch (strength) {
      case 'weak': return <AlertTriangle className="w-12 h-12" />;
      case 'medium': return <Shield className="w-12 h-12" />;
      case 'strong': return <CheckCircle className="w-12 h-12" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Main strength indicator */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 200 }}
        className="flex items-center justify-center"
      >
        <div 
          className="relative w-32 h-32 rounded-full flex items-center justify-center animate-pulse-glow"
          style={{
            color: getColor(strength),
            boxShadow: `0 0 30px ${getColor(strength)}80, 0 0 60px ${getColor(strength)}40`
          }}
        >
          {getIcon()}
        </div>
      </motion.div>

      {/* Strength label */}
      <div className="text-center">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold capitalize"
          style={{ color: getColor(strength) }}
        >
          {strength}
        </motion.div>
      </div>

      {/* Probability bars */}
      <div className="space-y-3">
        {(['weak', 'medium', 'strong'] as const).map((level) => (
          <div key={level} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="capitalize text-foreground/70">{level}</span>
              <span className="text-foreground/90">{(probabilities[level] * 100).toFixed(1)}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${probabilities[level] * 100}%` }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="h-full rounded-full"
                style={{
                  backgroundColor: getColor(level),
                  boxShadow: `0 0 10px ${getColor(level)}`
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
