# File where the API key is stored
API_KEY_FILENAME = '../api_key.secret'

# File where the access token and secret will be stored when authenticated
ACCESS_TOKEN_FILENAME = '../access_token.secret'

# Where to save all the downloaded jobs' data
DATABASE = '../data/jobs_db.sqlite3'

MODEL_FILENAME = 'model.pkl'

TABLE_NAME = 'jobs'

# 'id' must be the first field
FIELDS_NAMES = [
  'id',
  'title',
  'snippet',
  'job_type',
  'budget',
  'job_status',
  'category2',
  'subcategory2',
  'url',
  'workload',
  'duration',
  'date_created',
  'skills',
  'client.feedback',
  'client.reviews_count',
  'client.jobs_posted',
  'client.payment_verification_status',
  'client.past_hires',
  'client.country',
  'label'
]

JOB_FIELDS = [
  'op_title',                # Job title
  'op_description',          # Job snippet
  'amount',                  # May be also op_amount
  'ui_opening_status',       # Active or closed
  'job_type',                # Job type, "Hourly" or "Fixed"
  'engagement_weeks',        # 
  'op_job_category_v2',      # 
  'op_tot_feedback',         # Total number of feedbacks
  'op_contractor_tier',      #
  'op_required_skills',      #
  'op_tot_feedback',         #
  'op_low_hourly_rate_all',  # The lowest proposed rate
  'op_high_hourly_rate_all', # The highest proposed rate
  'op_pref_hourly_rate_max', # Client preferred maximum hourly rate
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