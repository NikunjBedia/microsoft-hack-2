import React from 'react';
import { motion } from 'framer-motion';

const NavigationIcon = ({ direction }: any) => {
  const isLeft = direction === 'left';

  return (
    <motion.svg
      width="48"
      height="48"
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      whileHover="hover"
    >
      <motion.path
        d={isLeft ? "M44 24H4M24 4L4 24L24 44" : "M4 24H44M24 4L44 24L24 44"}
        stroke="currentColor"
        strokeWidth="1"
        strokeLinecap="round"
        strokeLinejoin="round"
        variants={{
          hover: {
            d: isLeft ? "M48 24H4M24 4L4 24L24 44" : "M0 24H48M24 4L44 24L24 44",
            transition: { duration: 0.3 }
          }
        }}
      />
    </motion.svg>
  );
};

export default NavigationIcon;
