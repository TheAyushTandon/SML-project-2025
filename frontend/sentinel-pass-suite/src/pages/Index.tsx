import { useState, useEffect } from 'react';
import { ParticleBackground } from '@/components/ParticleBackground';
import { Hero } from '@/components/Hero';
import { PasswordAnalyzer } from '@/components/PasswordAnalyzer';
import { ModelTabs } from '@/components/ModelTabs';
import { GeneratorPanel } from '@/components/GeneratorPanel';
import { AIOrb } from '@/components/AIOrb';
import { Footer } from '@/components/Footer';

const Index = () => {
  const [showAnalyzer, setShowAnalyzer] = useState(false);
  const [showGenerator, setShowGenerator] = useState(false);
  const [orbState, setOrbState] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');

  const handleAnalyze = () => {
    setShowAnalyzer(true);
    setShowGenerator(false);
    setTimeout(() => {
      document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleGenerate = () => {
    setShowGenerator(true);
    setShowAnalyzer(false);
    setTimeout(() => {
      document.getElementById('generator')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  useEffect(() => {
    // Update orb state based on activity
    const handleActivity = () => {
      setOrbState('processing');
      setTimeout(() => setOrbState('success'), 1000);
      setTimeout(() => setOrbState('idle'), 3000);
    };

    window.addEventListener('click', handleActivity);
    return () => window.removeEventListener('click', handleActivity);
  }, []);

  return (
    <div className="relative min-h-screen">
      <ParticleBackground />
      
      <main className="relative z-10">
        <Hero onAnalyze={handleAnalyze} onGenerate={handleGenerate} />
        <PasswordAnalyzer isVisible={showAnalyzer} />
        <GeneratorPanel isVisible={showGenerator} />
        <ModelTabs />
        <Footer />
      </main>

      <AIOrb state={orbState} />
    </div>
  );
};

export default Index;
