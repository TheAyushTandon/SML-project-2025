import { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check, Loader2, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface GeneratorPanelProps {
  isVisible: boolean;
}

export const GeneratorPanel = ({ isVisible }: GeneratorPanelProps) => {
  const [baseWord, setBaseWord] = useState('');
  const [mode, setMode] = useState<'balanced' | 'memorable' | 'hacker-proof'>('balanced');
  const [loading, setLoading] = useState(false);
  const [passwords, setPasswords] = useState<string[]>([]);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const { toast } = useToast();

  const modes = [
    { id: 'balanced' as const, label: 'Balanced', description: 'Optimal security and usability' },
    { id: 'memorable' as const, label: 'Memorable', description: 'Enhanced memorability' },
    { id: 'hacker-proof' as const, label: 'Maximum Security', description: 'Highest security level' },
  ];

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const result = await api.generatePassword({
        base: baseWord || undefined,
        mode,
      });
      setPasswords(result.passwords);
    } catch (error) {
      toast({
        title: "Generation Failed",
        description: error instanceof Error ? error.message : "Failed to generate passwords",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (password: string, index: number) => {
    try {
      await navigator.clipboard.writeText(password);
      setCopiedIndex(index);
      toast({
        title: "Copied!",
        description: "Password copied to clipboard",
      });
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (error) {
      toast({
        title: "Copy Failed",
        description: "Failed to copy password",
        variant: "destructive",
      });
    }
  };

  if (!isVisible) return null;

  return (
    <motion.section
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="py-20 px-4"
      id="generator"
    >
      <div className="container max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold mb-4 gradient-text">
            Password Generator
          </h2>
          <p className="text-muted-foreground text-lg">
            AI-generated secure passwords with customizable security profiles
          </p>
        </motion.div>

        <div className="glass rounded-2xl p-8 space-y-8">
          {/* Input section */}
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block text-foreground/80">
                Base Word or Phrase
              </label>
              <Input
                value={baseWord}
                onChange={(e) => setBaseWord(e.target.value)}
                placeholder="Optional: Enter a base word or phrase"
                className="h-12 bg-input border-primary/30 focus:border-primary"
              />
            </div>

            {/* Mode selection */}
            <div>
              <label className="text-sm font-medium mb-3 block text-foreground/80">
                Security Profile
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {modes.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => setMode(m.id)}
                    className={`p-4 rounded-xl transition-all ${
                      mode === m.id
                        ? 'glass border-2 border-primary neon-glow'
                        : 'glass border border-primary/20 hover:border-primary/50'
                    }`}
                  >
                    <div className="text-sm font-semibold mb-1">{m.label}</div>
                    <div className="text-xs text-muted-foreground">{m.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <Button
              onClick={handleGenerate}
              disabled={loading}
              variant="hero"
              size="lg"
              className="w-full h-14 text-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  Generate Passwords
                </>
              )}
            </Button>
          </div>

          {/* Generated passwords */}
          {passwords.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-3"
            >
              <h3 className="text-lg font-semibold text-primary mb-4">Generated Passwords</h3>
              {passwords.map((password, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="glass rounded-xl p-4 flex items-center justify-between gap-4 group hover:border-primary/50 transition-all"
                >
                  <code className="text-lg font-mono flex-1 text-primary break-all">
                    {password}
                  </code>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => copyToClipboard(password, index)}
                    className="shrink-0"
                  >
                    {copiedIndex === index ? (
                      <Check className="w-5 h-5 text-green-500" />
                    ) : (
                      <Copy className="w-5 h-5" />
                    )}
                  </Button>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </div>
    </motion.section>
  );
};
