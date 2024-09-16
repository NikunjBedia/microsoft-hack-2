import * as React from "react";
import { motion } from "framer-motion";
import MenuItem from "./menuItem";
import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { selectTopic } from "../../actions/topicActions";

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
  const selectedTopic = useSelector((state: any) => state.topic);
  const dispatch = useDispatch();
  const topics = useSelector((state:any) => state.topic.topics);
  const handleClick = (topic: String) => {
    dispatch(selectTopic(topic));
  };
  return (
    <motion.ul variants={variants} className="scrollable-menu">
      {topics?.map((i: String, index: number) => (
        <MenuItem
          i={i}
          key={index}
          onClick={() => handleClick(i)} // Pass the click handler
          isSelected={selectedTopic === i} // Pass the selected state
        />
      ))}
    </motion.ul>
  );
};

export default Navigation;
