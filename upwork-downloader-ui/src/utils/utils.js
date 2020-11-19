import config from "../config";
import moment from 'moment';

export const sortByDate = (a, b) => {

  if (moment(a.date_created).isBefore(b.date_created)) {
    return 1;
  }
  if (moment(a.date_created).isAfter(b.date_created)) {
    return -1;
  }
  return 0;
};

export const get_endpoint = () => {
  if (!process.env.NODE_ENV || process.env.NODE_ENV === "development") {
    return config.DEV_ENDPOINT;
  } else {
    return config.PROD_ENDPOINT;
  }
};
