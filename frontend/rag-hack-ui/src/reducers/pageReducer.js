import { HOME_PAGE, DASHBOARD_PAGE } from "../lib/actionTypes";

const initialState = {
  currentPage: HOME_PAGE,
};

const pageReducer = (state = initialState, action) => {
  switch (action.type) {
    case HOME_PAGE:
      return {
        ...state,
        currentPage: HOME_PAGE,
      };

    case DASHBOARD_PAGE:
      return {
        ...state,
        currentPage: DASHBOARD_PAGE,
      };
    default:
      return state;
  }
};

export default pageReducer;
