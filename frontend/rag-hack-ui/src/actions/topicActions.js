import { SELECT_TOPIC, UPDATE_TOPICS } from "../lib/actionTypes";

export const updateTopics = (data) => ({
  type: UPDATE_TOPICS,
  payload: data
});

export const selectTopic = (data) => ({
  type: SELECT_TOPIC,
  payload: data
});