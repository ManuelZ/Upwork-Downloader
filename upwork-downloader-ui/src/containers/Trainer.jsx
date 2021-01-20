import React, { useState, useRef } from "react";
import { get_endpoint } from "../utils/utils";

const ENDPOINT = get_endpoint();

const Trainer = () => {
  const [fetching, setFetching] = useState(false);
  const [search, setSearch] = useState(false);
  const [classifier, setClassifier] = useState('SVC');
  const [report, setReport] = useState(null);


  const buttonRef = useRef(null);

  const handleSearchChange = (event) => {
    setSearch(!search);
  };

  const handleClassifierChange = (event) => {
    setClassifier(event.target.value);
  };

  const train = async (event) => {
    event.preventDefault();
    setFetching(true);

    if (buttonRef.current) {
      buttonRef.current.setAttribute("disabled", "disabled");
    }

    let response = await fetch(`${ENDPOINT}/train`, {
      method: "POST",
      body: JSON.stringify({
        search: search,
        classifier: classifier
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    let data = await response.json();

    console.log(classifier)
    console.log(data);

    setReport(data['results'][classifier]['pr_rec_im']); //conf_matrix_im, pr_rec_im

    
    setFetching(false);
    buttonRef.current.removeAttribute("disabled");
  };

  return (
    <div className="flex flex-col m-1 lg:m-3 p-2 lg:p-4 justify-center text-center items-center">
      <div className="lg:mb-10 sm:mt-0">
        <div className="md:grid md:grid-cols-1 md:gap-6">
          <div className="lg:mt-5 md:mt-0 md:col-span-1">
            <form className="flex flex-row" action="#" method="POST">
              <div className="shadow sm:rounded-md">
                <div className="grid grid-cols-2 md:grid-cols-3 md:grid-rows-1">
                  {/* One column */}
                  <div className="px-4 py-5 bg-white sm:p-6">
                    <div className="flex flex-col items-center">
                      <legend className="text-base font-medium text-gray-900">
                        Traininig
                      </legend>
                      <p className="text-sm text-gray-500">Training options</p>
                    </div>
                    <fieldset className="mt-5 pb-4">
                      <div className="flex items-start pb-4">
                        <div className="flex items-center h-5">
                          <input
                            id="search"
                            name="search"
                            type="checkbox"
                            checked={search}
                            onChange={handleSearchChange}
                            className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                          />
                        </div>
                        <div className="flex flex-col items-start ml-3 text-sm">
                          <label
                            htmlFor="search"
                            className="font-medium text-gray-700"
                          >
                            Search
                          </label>
                          <p className="text-gray-500 text-left">
                            Hyperparameters search
                          </p>
                        </div>
                      </div>
                    </fieldset>
                  </div>

                  {/* Second  column */}
                  <div className="px-4 py-5 bg-white sm:p-6">
                    <div className="flex flex-col items-center">
                      <legend className="text-base font-medium text-gray-900">
                        Classifier
                      </legend>
                      <p className="text-sm text-gray-500">Select a classifier</p>
                    </div>
                    <fieldset className="mt-5 pb-4">
                      <div className="flex items-start pb-4">
                        <div className="flex items-center h-5">
                          <input
                            id="SVC"
                            name="classifier"
                            type="radio"
                            value='SVC'
                            checked={classifier === 'SVC'}
                            onChange={handleClassifierChange}
                            className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                          />
                        </div>
                        <div className="flex flex-col items-start ml-3 text-sm">
                          <label
                            htmlFor="SVC"
                            className="font-medium text-gray-700"
                          >
                            SVC
                          </label>
                        </div>
                      </div>
                      <div className="flex items-start pb-4">
                        <div className="flex items-center h-5">
                          <input
                            id="LogisticRegression"
                            name="classifier"
                            type="radio"
                            value='LogisticRegression'
                            checked={classifier === 'LogisticRegression'}
                            onChange={handleClassifierChange}
                            className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                          />
                        </div>
                        <div className="flex flex-col items-start ml-3 text-sm">
                          <label
                            htmlFor="LogisticRegression"
                            className="font-medium text-gray-700"
                          >
                            Logistic Regression
                          </label>
    
                        </div>
                      </div>
                      <div className="flex items-start pb-4">
                        <div className="flex items-center h-5">
                          <input
                            id="GradientBoostingClassifier"
                            name="classifier"
                            type="radio"
                            value='GradientBoostingClassifier'
                            checked={classifier === 'GradientBoostingClassifier'}
                            onChange={handleClassifierChange}
                            className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                          />
                        </div>
                        <div className="flex flex-col items-start ml-3 text-sm">
                          <label
                            htmlFor="GradientBoostingClassifier"
                            className="font-medium text-gray-700"
                          >
                            Gradient Boosting
                          </label>
    
                        </div>
                      </div>
                      <div className="flex items-start pb-4">
                        <div className="flex items-center h-5">
                          <input
                            id="VotingClassifier"
                            name="classifier"
                            type="radio"
                            value='VotingClassifier'
                            checked={classifier === 'VotingClassifier'}
                            onChange={handleClassifierChange}
                            className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                          />
                        </div>
                        <div className="flex flex-col items-start ml-3 text-sm">
                          <label
                            htmlFor="VotingClassifier"
                            className="font-medium text-gray-700"
                          >
                            Voting
                          </label>
    
                        </div>
                      </div>
                    </fieldset>
                  </div>
                </div>
                <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
                  <button
                    type="submit"
                    onClick={train}
                    className={
                      "inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-bold rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 " +
                      (fetching ? "opacity-50 cursor-not-allowed" : "")
                    }
                    ref={buttonRef}
                  >
                    {"Train"}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div className="flex flex-col w-full items-center mt-5 ">
        <img alt="" src={`data:image/jpeg;base64,${report}`} />
      </div>
      <div className="flex flex-col w-full items-center mt-5 ">
        {}
      </div>
    </div>
  );
};

export default Trainer;
