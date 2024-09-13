import React from "react";
import FileUploadButton from "./upload";

const Home = () => {
  const handleFileUpload = async (data: { file: File | null; duration: string | null }) => {
    if (data.file && data.duration) {
      const formData = new FormData();
      formData.append('file', data.file);
      formData.append('duration', data.duration);

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
    <div className="h-screen w-screen flex flex-col justify-center items-center">
      <div className="text-8xl">Cur.io</div>
      <FileUploadButton onUpload={handleFileUpload} />
    </div>
  );
};

export default Home;
