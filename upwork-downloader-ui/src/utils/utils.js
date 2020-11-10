import config from "../config";

export const sortByDate = (a, b) => {
  if (a.date_created < b.date_created) {
    return 1;
  }
  if (a.date_created > b.date_created) {
    return -1;
  }
  return 0;
};

export const get_endpoint = () => {
  let ENDPOINT;
  if (!process.env.NODE_ENV || process.env.NODE_ENV === "development") {
    return config.DEV_ENDPOINT;
  } else {
    return config.PROD_ENDPOINT;
  }
};
