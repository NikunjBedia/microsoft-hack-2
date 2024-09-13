import React, { useState } from "react";
import FileUploadButton from "./upload";
import FloatingSVG from "./asset/floating-svg";
import InterActiveScreen from "./interactive-screen";

const Home = () => {
  const [isUploadSuccessful, setIsUploadSuccessful] = useState(false);

  const handleFileUpload = async (files: File | null) => {
    if (files) {
      console.log("File uploaded");
      const formData = new FormData();
      formData.append("file", files);

      setTimeout(() => {
        setIsUploadSuccessful(true);
      }, 1000);

      // try {
      //   const response = await fetch('/upload-endpoint', {
      //     method: 'POST',
      //     body: formData,
      //   });
      //   const result = await response.json();
      //   console.log('Upload success:', result);
      // } catch (error) {
      //   console.error('Upload error:', error);
      // }
    }
  };
  return (
    <div className="relative h-screen w-screen overflow-hidden">
      {!isUploadSuccessful ? (
        <div className="font-medium relative h-full w-full flex items-center justify-center items-center">
          <FloatingSVG />
          <div className="relative z-10 flex flex-col items-center justify-center items-center h-full">
            <div className="text-7xl font-medium text-center">
              Lorem Ipsum Dolor <br /> Sit Amet
            </div>
            <FileUploadButton onUpload={handleFileUpload} />
          </div>
        </div>
      ) : (
        <InterActiveScreen />
      )}
    </div>
  );
};

export default Home;
