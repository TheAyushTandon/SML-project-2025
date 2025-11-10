import { useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Eye, EyeOff } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { StrengthMeter } from './StrengthMeter';
import { api, PasswordEvaluation } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface PasswordAnalyzerProps {
  isVisible: boolean;
}

export const PasswordAnalyzer = ({ isVisible }: PasswordAnalyzerProps) => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PasswordEvaluation | null>(null);
  const { toast } = useToast();

  const handleAnalyze = async () => {
    if (!password.trim()) {
      toast({
        title: "Error",
        description: "Please enter a password to analyze",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const evaluation = await api.evaluatePassword(password);
      // Validate response structure
      if (!evaluation || !evaluation.strength || !evaluation.classifier_probabilities) {
        throw new Error("Invalid response format from server");
      }
      setResult(evaluation);
    } catch (error) {
      console.error("Error analyzing password:", error);
      toast({
        title: "Analysis Failed",
        description: error instanceof Error ? error.message : "Failed to analyze password",
        variant: "destructive",
      });
      setResult(null); // Clear any previous result on error
    } finally {
      setLoading(false);
    }
  };

  if (!isVisible) return null;

  return (
    <motion.section
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="py-20 px-4"
      id="analyzer"
    >
      <div className="container max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold mb-4 gradient-text">
            Password Analysis
          </h2>
          <p className="text-muted-foreground text-lg">
            Comprehensive security evaluation using multi-model AI analysis
          </p>
        </motion.div>

        <div className="glass rounded-2xl p-8 space-y-8">
          {/* Input section */}
          <div className="space-y-4">
            <div className="relative">
              <Input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                placeholder="Enter password for security analysis"
                className="pr-12 h-14 text-lg bg-input border-primary/30 focus:border-primary transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            <Button
              onClick={handleAnalyze}
              disabled={loading || !password.trim()}
              variant="hero"
              size="lg"
              className="w-full h-14 text-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Analyze Password'
              )}
            </Button>
          </div>

          {/* Results section */}
          {result && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="grid md:grid-cols-2 gap-8"
            >
              {/* Left: Strength meter */}
              <div className="glass rounded-xl p-6">
                <StrengthMeter
                  strength={result.strength}
                  probabilities={result.classifier_probabilities}
                />
              </div>

              {/* Right: Additional metrics */}
              <div className="space-y-4">
                {/* Leak Risk */}
                <div className="glass rounded-xl p-6 space-y-3">
                  <h3 className="text-lg font-semibold text-primary">Leak Risk</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Risk Score</span>
                    <span className="text-2xl font-bold" style={{
                      color: result.leak_risk.score > 70 ? 'hsl(0, 84%, 60%)' : 
                             result.leak_risk.score > 40 ? 'hsl(45, 100%, 50%)' : 
                             'hsl(120, 100%, 40%)'
                    }}>
                      {result.leak_risk.score}%
                    </span>
                  </div>
                  <p className="text-sm text-foreground/70">{result.leak_risk.message}</p>
                </div>

                {/* Anomaly Detection */}
                <div className="glass rounded-xl p-6 space-y-3">
                  <h3 className="text-lg font-semibold text-secondary">Anomaly Detection</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Anomaly Score</span>
                    <span className="text-2xl font-bold text-secondary">
                      {result.anomaly_detection.score.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-sm text-foreground/70">
                    {result.anomaly_detection.is_anomaly ? 'Unusual pattern detected' : 'Normal pattern'}
                  </p>
                </div>

                {/* Feedback */}
                {result.feedback.length > 0 && (
                  <div className="glass rounded-xl p-6 space-y-3">
                    <h3 className="text-lg font-semibold">Recommendations</h3>
                    <ul className="space-y-2">
                      {result.feedback.map((item, index) => (
                        <li key={index} className="text-sm text-foreground/80 flex items-start gap-2">
                          <span className="text-primary mt-1">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.section>
  );
};
