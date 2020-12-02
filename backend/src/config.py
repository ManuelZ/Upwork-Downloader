# File where the API key is stored
API_KEY_FILENAME = '../api_key.secret'

# File where the access token and secret will be stored when authenticated
ACCESS_TOKEN_FILENAME = '../access_token.secret'

# Where to save all the downloaded jobs' data
DATABASE = '../data/jobs_db.sqlite3'

MODEL_FILENAME = 'model.pkl'

TABLE_NAME = 'jobs'

# Job fields returned byt the "Search for jobs" API
FIELDS_NAMES = [
    'id',                                 # 'id' must be the first field
    'title',                              # Job title
    'snippet',                            # Job description
    'job_type',                           # Job type. 'hourly' or 'fixed price'
    'budget',                             # Job budget
    'job_status',                         # 'open', 'completed' or 'cancelled'
    'category2',                          # Related category 
    'subcategory2',                       # Related subcategory
    'url',                                # Job url
    'workload',                           # Requested work hours per week
    'duration',                           # Job duration
    'date_created',                       # Date job was created
    'skills',                             # List of required skills
    'client.feedback',                    # Feedback score
    'client.reviews_count',               # Number of reviews
    'client.jobs_posted',                 # Number of jobs posted by the client
    'client.payment_verification_status', # Payment verification status
    'client.past_hires',                  # Num of past hires made by the client
    'client.country',                     # Client's country
    'op_pref_hourly_rate_min',            # Client preferred minimum hourly rate
    'op_pref_hourly_rate_max',            # Client preferred maximum hourly rate
    'label'                               # MY OWN CLASSIFICATION LABEL
]

# Fields available through the "Get job profile" API
JOB_FIELDS = [
    #############################################################################
    # Fields that I currently have access to throug the "Search for jobs" API
    #############################################################################
    'op_title',                # Job title
    'op_description',          # Job snippet
    'amount',                  # Budget. Docs say "op_amount", but it's "amount"
    'job_type',                # Job type, "Hourly" or "Fixed"
    'op_tot_feedback',         # Total number of feedbacks
    'ui_opening_status',       # Active or closed
    'op_adjusted_score',       # Client's feedback score
    'op_country',              # Client country
    'job_category_level_one',  # Undocumented. But seems like "category2"
    'job_category_level_two',  # Undocumented. But seems like "subcategory2"
    'op_cny_upm_verified',     # Flag. Whether payment method is verified

    #############################################################################
    # Fields that look interesting
    #############################################################################
    'op_pref_hourly_rate_min', # Client preferred minimum hourly rate
    'op_pref_hourly_rate_max', # Client preferred maximum hourly rate
    'op_tot_charge',           # Total amount ever spent by this client
    'op_low_hourly_rate_all',  # The lowest proposed rate. Default 0 apparently
    'op_high_hourly_rate_all', # The highest proposed rate. Default 0 apparently
    'op_contractor_tier',      # Client's preferred freelancer tier 
                               # (1=beginner, 2=intermediate, 3=expert) 
    'candidates',              # -> ciphertext and create_date_ts !!!!!!!!!!
    
    #############################################################################
    # Other available fields (non-exhaustive)
    #############################################################################
    # Note to self: "assignments" refers to other jobs opened by the client, 
    # can include jobs that have already started or that are already finished
    'op_other_jobs',           # Other open jobs by this client
    'engagement_weeks',        # ??????????
    'op_job_category_v2',      # Job category (V2)
    'op_required_skills',      # -> op_required_skill -> skill: Skill name
    'op_tot_jobs_posted',      # Total jobs posted
    'op_tot_jobs_filled',      # Total jobs filled
    'op_tot_jobs_open',        # Total jobs open 
    'op_tot_asgs',             # Total assignments  ???????
    'op_tot_fp_asgs',          # Total fixed price assignments
    'op_tot_hours',            # Total number of buyer's hours
    'op_contract_date',        # Member since
    'op_engagement',           # Estimate duration description
]

SEARCH_TERMS = [
    'machine learning',
    'python',
    'artificial intelligence',
    'opencv',
    'time series',
    'computer vision',
    'optimization algorithm',
    'raspberry pi',
    'arduino',
    'supervised learning',
    "product matching",
    "ml model",
    "ml",
    "ai",
    "segmentation",
    "path",
    "reinforcement learning",
    "data science",
    "aws batch"
    ]

MAX_ENTRIES_PER_TERM = 20
ENTRIES_PER_RESULT_PAGE = 100 # Do not increase more than 100
DAYS_BACK_TO_SEARCH = 3

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S%z"