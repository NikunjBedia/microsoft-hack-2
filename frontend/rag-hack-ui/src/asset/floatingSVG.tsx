import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useSelector } from "react-redux";
import { HOME_PAGE } from "../lib/actionTypes";

const FloatingSVG = () => {
  const page = useSelector((state: any) => state.page.currentPage);

  return (
    <motion.svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 400 400"
      width="800"
      height="800"
      className="absolute z-0"
      style={{ overflow: "visible" }} // Prevents clipping of the glow
      initial={{ scale: 1 }}
      animate={{
        scale: page !== HOME_PAGE ? 0 : [1, 1.15, 1], // Scale to 0 if shrinking, else float
      }}
      transition={{
        duration: 2,
        ease: "easeInOut",
        repeat: page !== HOME_PAGE ? 0 : Infinity, // Stop repeating when shrinking
      }}
    >
      <defs>
        <filter id="glow" x="-200%" y="-200%" width="400%" height="400%">
          <feGaussianBlur stdDeviation="30" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <motion.g
        initial="hidden"
        animate="visible"
        variants={{
          visible: {
            transition: {
              staggerChildren: 0.2, // Stagger the children by 0.2 seconds
            },
          },
        }}
      >
        {[
          // { r: 200, fill: "#FAFEFF" },
          { r: 160, fill: "#EAFAFF" },
          { r: 120, fill: "#DAF7FF" },
          { r: 80, fill: "#CAF6FF" },
          { r: 40, fill: "#BAF4FF" },
        ].map(({ r, fill }, index) => (
          <motion.circle
            key={index}
            cx="200"
            cy="200"
            r={r}
            fill={fill}
            filter="url(#glow)"
            animate={{ scale: page !== HOME_PAGE ? 0 : 1.2 }}
            transition={{
              duration: 2,
              ease: "easeInOut",
            }}
          />
        ))}
      </motion.g>
    </motion.svg>
  );
};

export default FloatingSVG;
