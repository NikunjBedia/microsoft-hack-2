import React, { useState } from "react";
import { Button } from "./components/ui/button";

interface FileUploadButtonProps {
  onUpload: (files: File | null) => void;
}

const FileUploadButton: React.FC<FileUploadButtonProps> = ({ onUpload }) => {
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

      <Button
        onClick={() => document.getElementById("file-upload")?.click()}
        className="rounded-full"
      >
        Upload File
      </Button>

      {selectedFile && (
        <p className="p-2">Selected file: {selectedFile.name}</p>
      )}
      {error && <p className="text-red-500 p-2">{error}</p>}
    </div>
  );
};

export default FileUploadButton;
