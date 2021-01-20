import config from "../config";
import moment from "moment";

export const sortByDate = (a, b) => {
  if (a.predicted === b.predicted) {
    if (moment(a.date_created).isBefore(b.date_created)) {
      return 1;
    }
    if (moment(a.date_created).isAfter(b.date_created)) {
      return -1;
    }
  } else if ((a.predicted === "Good") & (b.predicted === "Bad")) {
    return -1;
  } else if ((a.predicted === "Good") & (b.predicted === "Maybe")) {
    return -1;
  } else if ((a.predicted === "Good") & (b.predicted === "Irrelevant")) {
    return -1;
  } else if ((a.predicted === "Maybe") & (b.predicted === "Good")) {
    return 1;
  } else if ((a.predicted === "Maybe") & (b.predicted === "Bad")) {
    return -1;
  } else if ((a.predicted === "Maybe") & (b.predicted === "Irrelevant")) {
    return -1;
  } else if ((a.predicted === "Bad") & (b.predicted === "Good")) {
    return 1;
  } else if ((a.predicted === "Bad") & (b.predicted === "Maybe")) {
    return 1;
  } else if ((a.predicted === "Bad") & (b.predicted === "Irrelevant")) {
    return -1;
  } else if ((a.predicted === "Irrelevant") & (b.predicted === "Good")) {
    return 1;
  } else if ((a.predicted === "Irrelevant") & (b.predicted === "Maybe")) {
    return 1;
  } else if ((a.predicted === "Irrelevant") & (b.predicted === "Bad")) {
    return 1;
  }
};

export const get_endpoint = () => {
  if (!process.env.NODE_ENV || process.env.NODE_ENV === "development") {
    return config.DEV_ENDPOINT;
  } else {
    return config.PROD_ENDPOINT;
  }
};
