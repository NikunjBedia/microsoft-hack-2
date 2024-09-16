import React, { useState } from "react";
import FileUploadButton from "../upload";
import FloatingSVG from "../asset/floatingSVG";
import { useSelector, useDispatch } from "react-redux";
import actions from "../actions";
import { HOME_PAGE } from "../lib/actionTypes";

const Home = () => {
  const page = useSelector((state: any) => state.page.currentPage);
  const dispatch = useDispatch();
  const handleFileUpload = async (files: File | null) => {
    if (files) {
      console.log("File uploaded");
      const formData = new FormData();
      formData.append("file", files);

      setTimeout(() => {
        dispatch(actions.pageActions.dashboard());
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
    <div className="font-medium relative h-full w-full flex items-center justify-center items-center" style={{ pointerEvents:page === HOME_PAGE?"all":"none"}}>
      <FloatingSVG />
      <div
        id="home-body"
        className={`relative z-10 flex flex-col items-center justify-center items-center h-full ${
          page !== HOME_PAGE && "home-dissappear"
        }`}
      >
        <div className={`text-7xl font-medium text-center`}>
          Lorem Ipsum Dolor <br /> Sit Amet
        </div>
        <FileUploadButton onUpload={handleFileUpload} />
      </div>
    </div>
  );
};

export default Home;
