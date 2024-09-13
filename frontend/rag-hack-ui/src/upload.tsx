import React, { useState } from "react";
import { PlusIcon } from "@radix-ui/react-icons";
import { Button } from "./components/ui/button";

interface FileUploadWithDurationProps {
  onUpload: (data: { file: File | null; duration: string | null }) => void;
}

const durations = ["Lorem", "Ipsum", "Dolor"];

const FileUploadWithDuration: React.FC<FileUploadWithDurationProps> = ({
  onUpload,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedDuration, setSelectedDuration] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files ? event.target.files[0] : null;
    setSelectedFile(file);
  };

  const handleDurationClick = (duration: string) => {
    setSelectedDuration(duration);
  };

  const handleUploadClick = () => {
    if (selectedFile && selectedDuration) {
      onUpload({ file: selectedFile, duration: selectedDuration });
    } else {
      alert("Please select a file and a duration.");
    }
  };

  return (
    <div>
      <input
        type="file"
        id="file-upload"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      <Button onClick={() => document.getElementById("file-upload")?.click()}>
        <PlusIcon /> Add Document
      </Button>

      {selectedFile && <p>Selected file: {selectedFile.name}</p>}

      <div className="flex flex-row justify-center items-center">
        <span>Duration:</span>
        {durations.map((duration) => (
          <Button
            key={duration}
            className={`mx-2 p-2 border ${
              selectedDuration === duration
                ? "bg-blue-500 text-white"
                : "bg-gray-200"
            }`}
            onClick={() => handleDurationClick(duration)}
          >
            {duration}
          </Button>
        ))}
      </div>

      <Button
        onClick={handleUploadClick}
        className="mt-4 p-2 bg-green-500 text-white"
      >
        Upload
      </Button>
    </div>
  );
};

export default FileUploadWithDuration;
