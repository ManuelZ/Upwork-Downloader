import React from "react";

const Pager = ({ totalJobs, jobsPerPage, currentPage, setPage }) => {
  
  const createNum = (num, isDot, hiddable,) => {
    let highlight = "";
    if (currentPage === num) {
      highlight = "bg-indigo-200 hover:bg-indigo-200 font-bold "
    } else {
      highlight = "hover:bg-gray-50 ";
    }
    
    let extra = "";
    if (hiddable) {
      extra = "sm:hidden ";
    }
    
    let numShown = num;
    if (isDot) {
      numShown = "...";
    }

    return (
      <button
        key={num}
        className={
          "relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 " +
          highlight + extra
        }
        onClick={() => num === numShown ? setPage(num) : ""}
      >
        {numShown}
      </button>
    );
  };

  let maxPages = Math.ceil(totalJobs/jobsPerPage);
  let nums = [];
  let isDot = false;
  let hiddable = false;
  
  for (let i = 1; i <= maxPages; i++) {

    let x = 3;
    let n;
    if ((i > x) && (i < (currentPage - x))) {
      hiddable = isDot ? true : false;
      isDot = true;
    } else if ((i > x) && (i < currentPage)) {
      hiddable = false;
      isDot = false;
    } else if ((i > currentPage) && (i <= (currentPage + x))) {
      isDot = false;
      hiddable = false;
    } else if ( (i > currentPage) && (i <= (maxPages - x))) {
      hiddable = isDot ? true : false;
      isDot = true;
    } else if (i >= (maxPages - x)) {
      isDot = false;
      hiddable = false;
    } 

    n = createNum(i, isDot, hiddable);
    nums.push(n);
  }

  return (
    <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
      <div className="flex-1 flex justify-between sm:hidden">
        <button
          className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:text-gray-500"
          onClick={() => setPage(currentPage - 1)}
        >
          Previous
        </button>
        <button
          className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:text-gray-500"
          onClick={() => setPage(currentPage + 1)}
        >
          Next
        </button>
      </div>
      <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-gray-700">
            Showing{" "}
            <span className="font-medium">{(currentPage-1)*jobsPerPage+1}{" "}</span>
            to{" "}
            <span className="font-medium">{Math.min(currentPage*jobsPerPage, totalJobs)}{" "}</span>
            of{" "}
            <span className="font-medium">{totalJobs}{" "}</span>
            results{" "}
          </p>
        </div>
        <div>
          <nav
            className="relative z-0 inline-flex shadow-sm -space-x-px"
            aria-label="Pagination"
          >
            <button
              onClick={() => setPage(currentPage - 1)}
              className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
            >
              <span className="">Previous</span>
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
            {nums}
      
      
            <button
                className={
                  "relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 " +
                  (maxPages < 20
                    ? "hidden "
                    : " ") 
                }
                
              >
                {"..."}
              </button>


            <button
              onClick={() => setPage(currentPage + 1)}
              className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
            >
              <span className="">Next</span>
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
};

export default Pager;
