import { SELECT_TOPIC, UPDATE_TOPICS } from "../lib/actionTypes";

const initialState = {
  topics: [],
  currentTopic:null
};

const topicReducer = (state = initialState, action) => {
  console.log(action);
  switch (action.type) {
    case UPDATE_TOPICS:
      return {
        ...state,
        topics: action.payload
      };
    case SELECT_TOPIC:
      return{
        ...state,
        currentTopic: action.payload
      }
    default:
      return state;
  }
};

export default topicReducer;
