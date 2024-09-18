import React, { useEffect, useState } from "react";
import FileUploadButton from "../components/ui/upload";
import FloatingSVG from "../asset/floatingSVG";
import { useSelector, useDispatch } from "react-redux";
import actions from "../actions";
import { HOME_PAGE } from "../lib/actionTypes";
import useAxios from "../hooks/useAxios";

const Home = () => {
  const { data, loading, error, refetch } = useAxios<any>('/document', 'POST', null,{headers: {'Content-Type': 'multipart/form-data'}});
  const page = useSelector((state: any) => state.page.currentPage);
  const dispatch = useDispatch();
  useEffect(()=>{
    if(loading === false && data !== null){
      dispatch(actions.topicActions.updateTopics(data));
      dispatch(actions.topicActions.selectTopic(data[0]));
      dispatch(actions.pageActions.dashboard());
    }
  },[loading])
  const handleFileUpload = async (files: File | null) => {
    if (files) {
      const formData = new FormData();
      formData.append("file", files);
      refetch(formData);
    }
  };
  return (
    <div className="font-medium gradient-container relative h-full w-full flex items-center justify-center  items-center" style={{ pointerEvents:page === HOME_PAGE?"all":"none"}}>
      <FloatingSVG />
      <div
        id="home-body"
        className={`relative z-10 flex flex-col items-center justify-center items-center h-full ${
          page !== HOME_PAGE && "home-dissappear"
        }`}
      >
        <div className={`text-7xl font-medium text-center`}>
          Curio <br /> <p className="font-small"> The future of learning is here!</p>
        </div>
        <FileUploadButton onUpload={handleFileUpload} isLoading={loading} />
      </div>
    </div>
  );
};

export default Home;
