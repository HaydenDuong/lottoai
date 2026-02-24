import { motion } from 'framer-motion';

function AnimatedArrow({ direction = 'right', controls }) {
  // Define path strings for each direction
  const pathVariants = {
    right: "M 0 20 L 116 20",
    left: "M 116 20 L 0 20",
    down: "M 20 0 L 20 120",
    up: "M 20 120 L 20 0"
  };

  const isHorizontal = direction === 'right' || direction === 'left';

  return (
    <svg 
      width={isHorizontal ? "116" : "40"} 
      height={isHorizontal ? "40" : "120"} 
      className="overflow-visible"
      viewBox={isHorizontal ? "0 0 116 40" : "0 0 40 120"}
    >
      <defs>
        <linearGradient 
          id={`gradient-${direction}`} 
          x1={isHorizontal ? "0%" : "50%"} 
          y1={isHorizontal ? "50%" : "0%"} 
          x2={isHorizontal ? "100%" : "50%"} 
          y2={isHorizontal ? "50%" : "100%"}
        >
          <stop offset="0%" stopColor="rgba(255, 215, 0, 0.3)" />
          <stop offset="100%" stopColor="rgba(255, 215, 0, 1)" />
        </linearGradient>
      </defs>
      
      <motion.path
        d={pathVariants[direction]}
        stroke="#FFD700"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        animate={controls}
        initial={{ pathLength: 0, opacity: 0 }}
      />
    </svg>
  );
}

export default AnimatedArrow;