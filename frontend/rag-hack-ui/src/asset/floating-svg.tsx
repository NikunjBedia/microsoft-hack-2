import { motion } from "framer-motion";
import React from "react";

const FloatingSVG = () => {
  return (
    <motion.svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 400 400"
      width="800"
      height="800"
      className="absolute z-0"
      initial={{ y: 0 }}
      animate={{
        y: [0, -10, 0],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      <defs>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="10" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <circle cx="200" cy="200" r="200" fill="#FAFEFF" filter="url(#glow)" />
      <circle cx="200" cy="200" r="160" fill="#EAFAFF" filter="url(#glow)" />
      <circle cx="200" cy="200" r="120" fill="#DAF7FF" filter="url(#glow)" />
      <circle cx="200" cy="200" r="80" fill="#CAF6FF" filter="url(#glow)" />
      <circle cx="200" cy="200" r="40" fill="#BAF4FF" filter="url(#glow)" />
    </motion.svg>
  );
};

export default FloatingSVG;
