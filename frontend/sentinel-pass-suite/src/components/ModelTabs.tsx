import { useState } from 'react';
import { motion } from 'framer-motion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Brain, Skull, Eye, Lock } from 'lucide-react';

export const ModelTabs = () => {
  const [activeTab, setActiveTab] = useState('classifier');

  const models = [
    {
      id: 'classifier',
      name: 'Model A',
      title: 'Supervised Classifier',
      icon: Brain,
      color: 'primary',
      description: 'Supervised learning model classifying passwords by strength using multi-feature analysis.',
      features: [
        'Multi-class classification',
        'Probability distribution',
        'Pattern recognition',
        'Real-time analysis'
      ]
    },
    {
      id: 'leak',
      name: 'Model B',
      title: 'Leak Risk Scorer',
      icon: Skull,
      color: 'destructive',
      description: 'Breach database analysis with risk scoring based on historical compromise data.',
      features: [
        'Breach database lookup',
        'Risk score calculation',
        'Historical leak data',
        'Threat assessment'
      ]
    },
    {
      id: 'anomaly',
      name: 'Model C',
      title: 'Unsupervised Detector',
      icon: Eye,
      color: 'secondary',
      description: 'Unsupervised anomaly detection identifying unusual patterns through reconstruction error analysis.',
      features: [
        'Pattern anomaly detection',
        'Reconstruction error analysis',
        'Unsupervised learning',
        'Statistical outlier detection'
      ]
    },
    {
      id: 'generator',
      name: 'Model D',
      title: 'Password Generator',
      icon: Lock,
      color: 'accent',
      description: 'AI-driven password generation with configurable security profiles and entropy optimization.',
      features: [
        'Multiple generation modes',
        'Customizable length',
        'Entropy optimization',
        'Memorable patterns'
      ]
    }
  ];

  return (
    <section className="py-20 px-4 relative">
      <div className="container max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold mb-4 gradient-text">
            AI Security Architecture
          </h2>
          <p className="text-muted-foreground text-lg">
            Four specialized models providing comprehensive security analysis
          </p>
        </motion.div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-2 lg:grid-cols-4 gap-2 bg-transparent h-auto p-2">
            {models.map((model) => {
              const Icon = model.icon;
              return (
                <TabsTrigger
                  key={model.id}
                  value={model.id}
                  className="glass data-[state=active]:bg-primary/20 data-[state=active]:neon-glow h-auto py-4 px-3"
                >
                  <div className="flex flex-col items-center gap-2">
                    <Icon className="w-6 h-6" />
                    <span className="text-xs font-semibold">{model.name}</span>
                  </div>
                </TabsTrigger>
              );
            })}
          </TabsList>

          {models.map((model) => {
            const Icon = model.icon;
            return (
              <TabsContent key={model.id} value={model.id} className="mt-8">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="glass rounded-2xl p-8"
                >
                  <div className="grid md:grid-cols-2 gap-8">
                    {/* Left: Info */}
                    <div className="space-y-6">
                      <div className="flex items-start gap-4">
                        <div className="p-3 rounded-xl glass neon-glow">
                          <Icon className="w-8 h-8 text-primary" />
                        </div>
                        <div>
                          <h3 className="text-2xl font-bold mb-2">{model.title}</h3>
                          <p className="text-sm text-primary">{model.name}</p>
                        </div>
                      </div>

                      <p className="text-foreground/80">{model.description}</p>

                      <div className="space-y-3">
                        <h4 className="text-lg font-semibold text-primary">Key Features</h4>
                        <ul className="space-y-2">
                          {model.features.map((feature, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-primary mt-1">▸</span>
                              <span className="text-foreground/80">{feature}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Right: Visualization placeholder */}
                    <div className="glass rounded-xl p-6 flex items-center justify-center bg-gradient-to-br from-primary/5 to-secondary/5">
                      <div className="text-center space-y-4">
                        <Icon className="w-24 h-24 mx-auto text-primary animate-float" />
                        <p className="text-sm text-muted-foreground">
                          Real-time analysis visualization
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </TabsContent>
            );
          })}
        </Tabs>
      </div>
    </section>
  );
};
