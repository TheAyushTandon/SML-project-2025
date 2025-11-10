import { motion } from 'framer-motion';

interface AIOrbProps {
  state: 'idle' | 'processing' | 'success' | 'error';
}

export const AIOrb = ({ state }: AIOrbProps) => {
  const getColor = () => {
    switch (state) {
      case 'idle': return 'hsl(180, 100%, 50%)';
      case 'processing': return 'hsl(45, 100%, 50%)';
      case 'success': return 'hsl(120, 100%, 40%)';
      case 'error': return 'hsl(0, 84%, 60%)';
    }
  };

  const getMessage = () => {
    switch (state) {
      case 'idle': return 'Ready to analyze';
      case 'processing': return 'Processing...';
      case 'success': return 'Analysis complete!';
      case 'error': return 'Something went wrong';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      className="fixed bottom-8 right-8 z-50"
    >
      <div className="relative group cursor-pointer">
        {/* Orb */}
        <motion.div
          animate={{
            boxShadow: [
              `0 0 20px ${getColor()}80`,
              `0 0 40px ${getColor()}60`,
              `0 0 20px ${getColor()}80`,
            ],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="w-16 h-16 rounded-full flex items-center justify-center glass"
          style={{
            backgroundColor: `${getColor()}20`,
            border: `2px solid ${getColor()}`,
          }}
        >
          <motion.div
            animate={{
              scale: state === 'processing' ? [1, 1.2, 1] : 1,
            }}
            transition={{
              duration: 1,
              repeat: state === 'processing' ? Infinity : 0,
            }}
            className="w-8 h-8 rounded-full"
            style={{
              backgroundColor: getColor(),
            }}
          />
        </motion.div>

        {/* Tooltip */}
        <div className="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          <div className="glass rounded-lg px-4 py-2 whitespace-nowrap">
            <p className="text-sm font-medium">{getMessage()}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
