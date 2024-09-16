import React, { useState } from "react";
import { motion } from "framer-motion";

interface FileUploadButtonProps {
  onUpload: (files: File | null) => void;
  isLoading: boolean | null;
}

const FileUploadButton: React.FC<FileUploadButtonProps> = ({
  onUpload,
  isLoading,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files ? event.target.files[0] : null;
    setError(null);
    if (file) {
      if (file.type !== "application/pdf") {
        setError("Please upload only PDF files.");
        setSelectedFile(null);
        return;
      }

      const maxFileSize = 2 * 1024 * 1024;
      if (file.size > maxFileSize) {
        setError("File size should not exceed 2MB.");
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      onUpload(file);
    }
  };

  return (
    <div className="flex flex-col justify-center items-center p-8">
      <input
        type="file"
        id="file-upload"
        accept="application/pdf"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      <motion.button
        onClick={() => document.getElementById("file-upload")?.click()}
        className="bg-[#0F172A] text-white rounded-full font-medium flex items-center justify-center"
        initial={false}
        animate={{
          width: isLoading ? "50px" : "125px",
          height: isLoading ? "50px" : "45px",
          transition: { duration: 0.3, ease: "easeInOut" },
        }}
      >
        {isLoading ? (
          <motion.div
            className="border-t-2 border-white border-solid rounded-full"
            style={{ width: "20px", height: "20px" }}
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1 }}
          />
        ) : (
          "Upload File"
        )}
      </motion.button>

      {selectedFile && (
        <p className="p-4">Selected file: {selectedFile.name}</p>
      )}
      {error && <p className="text-red-500 p-2">{error}</p>}
    </div>
  );
};

export default FileUploadButton;
