import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const VoiceVisualizer = () => {
  const [levels, setLevels] = useState(new Array(5).fill(5)); // Increased number of bars
  const [clicked, setClicked] = useState(false);

  useEffect(() => {
    // Simulate audio input for the visualizer
    const interval = setInterval(() => {
      setLevels(levels.map(() => Math.random() * 100)); // Generate random values for each bar
    }, 200); // Faster updates for a more responsive look

    return () => clearInterval(interval);
  }, [levels]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '200px',
      width: '200px',
      borderRadius: '50%',
      backgroundColor: 'black',
      position: 'relative',
    }}
    onClick={()=>{setClicked(!clicked)}}
    >
      <div style={{
        display: 'flex',
        justifyContent:'space-between',
        alignItems: 'center',
        width: '100px', // Adjust based on the number of bars for proper spacing
        height: '100px',
        position: 'relative',
      }}>
        {levels.map((level, index) => (
          <motion.div
            key={index}
            className='bar'
            initial={{ height: '5px' }}
            animate={!clicked?{ height: `${level}%` }:{ scaleY: [0.4, 1, 0.4] }}
            transition={{ duration: !clicked?0.3:2, ease: 'easeInOut', delay:!clicked?0:0.1*index, repeat:Infinity}} // Faster transitions for smoother movement
            style={{
              width: '5px', // Thinner bars for a sleek look
              background: `linear-gradient(180deg, #00F260, #0575E6)`, // Gradient color for each bar
              borderRadius: '2px',
              transformOrigin: !clicked?'bottom':'center',
              height:clicked?"50px":undefined
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default VoiceVisualizer;

// const SoundwaveVisualizer = () => {
//   const [isClicked, setIsClicked] = useState(false);

//   const bars = [0, 1, 2, 3, 4]; // Five bars for the wave

//   return (
//     <div
//       style={{
//         display: 'flex',
//         justifyContent: 'center',
//         alignItems: 'center',
//         height: '200px',
//         width: '200px',
//         borderRadius: '50%',
//         backgroundColor: 'black',
//         position: 'relative',
//       }}
//       onClick={() => setIsClicked(!isClicked)} // Toggle click state
//     >
//       <div
//         style={{
//           display: 'flex',
//           justifyContent: 'center',
//           alignItems: 'center',
//         }}
//       >
//         {bars.map((_, index) => (
//           <motion.div
//             key={index}
//             className="bar"
//             animate={} // Create wave effect
//             transition={{
//               duration: 1,
//               ease: 'easeInOut',
//               repeat: Infinity, // Infinite loop for the wave effect
//               delay: index * 0.1, // Stagger the delay for each bar
//             }}
//             style={{
//               width: '10px',
//               height: '50px',
//               backgroundColor: '#3498db',
//               margin: '0 5px',
//               borderRadius: '5px',
//             }}
//           />
//         ))}
//       </div>
//     </div>
//   );
// };

// import React, { useEffect, useState } from 'react';
// import { motion } from 'framer-motion';

// const VoiceVisualizer = () => {
//   const [levels, setLevels] = useState(new Array(5).fill(5)); // Initial levels
//   const [clicked, setClicked] = useState(false); // Toggle between normal and wave animation

//   useEffect(() => {
//     if (!clicked) {
//       // Simulate audio input for the visualizer when not in wave mode
//       const interval = setInterval(() => {
//         setLevels(levels.map(() => Math.random() * 100)); // Random bar heights
//       }, 200);

//       return () => clearInterval(interval);
//     }
//   }, [clicked, levels]);

//   return (
//     <div
//       style={{
//         display: 'flex',
//         justifyContent: 'center',
//         alignItems: 'center',
//         height: '200px',
//         width: '200px',
//         borderRadius: '50%',
//         backgroundColor: 'black',
//         position: 'relative',
//       }}
//       onClick={() => setClicked(!clicked)} // Toggle animation on click
//     >
//       <div
//         style={{
//           display: 'flex',
//           justifyContent: 'space-between',
//           alignItems: 'center',
//           width: '100px', // Adjust based on the number of bars for proper spacing
//           height: '100px',
//           position: 'relative',
//         }}
//       >
//         {levels.map((level, index) => (
//           <motion.div
//             key={index}
//             className="bar"
//             initial={{ height: '5px' }}
//             animate={
//               !clicked
//                 ? { height: `${level}%` } // Animate bar heights based on levels
//                 : { scaleY: [0.4, 1, 0.4] } // Wave animation
//             }
//             transition={{
//               duration: !clicked ? 0.3 : 2, // Different speeds for each state
//               ease: 'easeInOut',
//               delay: !clicked ? 0 : 0.1 * index, // Staggered delay for wave animation
//               repeat: clicked ? Infinity : 0, // Only repeat in wave mode
//             }}
//             style={{
//               width: '5px',
//               background: 'linear-gradient(180deg, #00F260, #0575E6)', // Gradient color for each bar
//               borderRadius: '2px',
//               transformOrigin: clicked ? 'center' : 'bottom', // Change origin for wave vs height animation
//               margin: '0 3px',
//               height: clicked ? '50px' : undefined, // Set fixed height for wave mode
//             }}
//           />
//         ))}
//       </div>
//     </div>
//   );
// };

// export default VoiceVisualizer;
