import { combineReducers } from "redux";
import pageReducer from "./pageReducer";
import topicReducer from "./topicReducer";

const rootReducer = combineReducers({
  page: pageReducer,
  topic: topicReducer
});

export default rootReducer;
