import { motion } from "framer-motion";
import React from "react";

const InterActiveScreen = () => {
  return (
    <div className="h-full w-full">
      <motion.div
        className="top-full bg-black h-full w-full flex items-center justify-center"
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 80, damping: 20 }}
      ></motion.div>
    </div>
  );
};

export default InterActiveScreen;
