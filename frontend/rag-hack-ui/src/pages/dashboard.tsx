import * as React from "react";
import { useRef } from "react";
import { motion, useCycle } from "framer-motion";
import { useDimensions } from "../lib/useDimensions";
import MenuToggle from "../components/ui/menuToggle";
import Navigation from "../components/ui/Navigation";
import { DASHBOARD_PAGE } from "../lib/actionTypes";
import { useSelector } from "react-redux";
import { Pause, Mic, ChevronLeft, ChevronRight } from "lucide-react";
import VoiceVisualizer from "../components/ui/voiceVisualizer";

const sidebar = {
  open: (height = 525) => ({
    clipPath: `circle(${height * 2 + 200}px at 40px 40px)`,
    borderRadius: "16px",
    margin: "10px",
    transition: {
      type: "spring",
      stiffness: 20,
      restDelta: 2,
    },
    boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)",
  }),
  closed: {
    clipPath: "circle(30px at 40px 40px)",
    margin: "0px",
    transition: {
      delay: 0.5,
      type: "spring",
      stiffness: 400,
      damping: 40,
    },
  },
};

const Dashboard = () => {
  const page = useSelector((state: any) => state.page.currentPage);
  const [isOpen, toggleOpen] = useCycle(false, true);
  const containerRef = useRef(null);
  const { height } = useDimensions(containerRef);
  React.useEffect(() => {
    if (page === DASHBOARD_PAGE) {
      setTimeout(() => {
        toggleOpen();
      }, 1000);
    }
  }, [page]);

  return (
    <div
      className={`page bg-gray-100 ${
        page === DASHBOARD_PAGE && "dashboard-show"
      }`}
    >
      <motion.nav
        initial={false}
        animate={isOpen ? "open" : "closed"}
        custom={height}
        ref={containerRef}
        style={{ zIndex: isOpen ? 60 : 50 }}
      >
        <motion.div
          className="background"
          variants={sidebar}
          initial={{ background: "F3F3F4", backgroundSize: "0%" }}
          animate={{
            backgroundImage: "linear-gradient(to right, #DAF7FF, transparent)",
            backgroundSize: isOpen ? "100%" : "0%", // Transition the gradient size
            backgroundPosition: "left", // Ensure the gradient starts from the left
            backgroundRepeat: "no-repeat", // Avoid repeating the gradient
          }}
          transition={{ duration: 0.5 }}
        />
        <motion.div
          className="background"
          variants={sidebar}
          initial={{ background: "F3F3F4", backgroundSize: "0%" }}
          animate={{
            backgroundColor: "#FFFFFF",
            backgroundSize: isOpen ? "100%" : "0%", // Transition the gradient size
            backgroundPosition: "left", // Ensure the gradient starts from the left
            backgroundRepeat: "no-repeat", // Avoid repeating the gradient
          }}
          transition={{ duration: 0.5 }}
        />
        <Navigation />
        <MenuToggle toggle={() => toggleOpen()} />
      </motion.nav>
      <div className="flex flex-col h-screen bg-gray-100 p-4">
        <div className="audio-container h-1/3 flex justify-center items-center">
          <VoiceVisualizer />
        </div>
        <div className="flex justify-center items-center mb-5">
        <button 
          className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 mr-3"
        >
          <Pause size={25} />
        </button>
        <button 
          className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 ml-3"
        >
          <Mic size={25} />
        </button>
        </div>
        <div className="flex-grow bg-white w-100 rounded-lg shadow-md p-4 mb-4 overflow-y-auto"></div>
        <div
          className="flex justify-between items-center"
          style={{ zIndex: 55 }}
        >
          <button className="p-2 bg-white text-black rounded-full shadow-md hover:shadow-lg">
            <ChevronLeft size={20} />
          </button>
          <p className="text-2xl text-center">{"Title of the chapter"}</p>
          <button className="p-2 bg-white text-black rounded-full shadow-md hover:shadow-lg">
            <ChevronRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
