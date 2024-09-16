import * as React from "react";
import { motion } from "framer-motion";

const variants = {
  open: {
    y: 0,
    opacity: 1,
    transition: {
      y: { stiffness: 1000, velocity: -100 },
    },
  },
  closed: {
    y: 50,
    opacity: 0,
    transition: {
      y: { stiffness: 1000 },
    },
  },
};

const colors = ["#FF008C", "#D309E1", "#9C1AFF", "#7700FF", "#4400FF"];

const MenuItem = ({ i, onClick, isSelected }: any) => {
  const style = { border: `2px solid ${colors[i]}` };
  return (
    <motion.li
      variants={variants}
      whileHover={{ scale: 1.01, x: 10 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`w-72 h-20 flex items-center justify-center text-center font-medium rounded-2xl cursor-pointer transition-colors duration-300 hover:bg-[#FAFEFF] border-[1.5px]
        ${isSelected ? "bg-[#EAFEFF] border-[#e6f4f1]" : "bg-[#FFF] border-[#e6f4f1]"}`}
    >
      <div>{i}</div>
    </motion.li>
  );
};

export default MenuItem;
