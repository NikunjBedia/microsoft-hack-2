import * as React from "react";
import { motion } from "framer-motion";
import MenuItem from "./menuItem";
import { useState } from "react";

const variants = {
  open: {
    transition: { staggerChildren: 0.07, delayChildren: 0.2 },
    margin: "10px",
  },
  closed: {
    transition: { staggerChildren: 0.05, staggerDirection: -1 },
  },
};

const Navigation = () => {
  const [selectedButton, setSelectedButton] = useState<number | null>(null);
  const handleClick = (index: number) => {
    setSelectedButton(index);
  };
  return (
    <motion.ul variants={variants}>
      {itemIds.map((i, index) => (
        <MenuItem
          i={i}
          key={index}
          onClick={() => handleClick(index)} // Pass the click handler
          isSelected={selectedButton === index} // Pass the selected state
        />
      ))}
    </motion.ul>
  );
};

const itemIds = [
  "Chapter 1: Resources",
  "Chapter 2: Land Resources",
  "Chapter 3: Soil Resources",
  "Chapter 4: Soil Erosion and Soil Conservation",
  "Chapter 5: Resource Planning in India",
];

export default Navigation;
