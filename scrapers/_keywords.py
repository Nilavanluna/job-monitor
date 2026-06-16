# Shared keyword config — imported by all scrapers
# Keep this as the single source of truth

KEYWORDS = [
    # Core engineering roles
    "software engineer", "software developer", "systems engineer",
    "cloud engineer", "devops engineer", "site reliability engineer",
    "platform engineer", "infrastructure engineer", "network engineer",
    "security engineer", "data engineer", "backend engineer",
    "fullstack engineer", "full stack engineer", "full-stack engineer",
    "solutions engineer", "support engineer", "automation engineer",
    "ml engineer", "ai engineer", "machine learning engineer",
    # Level signals (catches "Graduate Software Engineer", "Junior Cloud Engineer" etc.)
    "graduate", "junior", "intern", "internship", "entry level",
    "entry-level", "associate engineer", "associate developer",
    "early careers", "early career", "graduate programme",
    "new grad", "trainee", "apprentice",
    # Tech-specific (catches roles with these in the title)
    "kubernetes", "terraform", "devsecops", "mlops", "aiops",
    "observability", "reliability engineer",
    # Broader tech titles
    "developer", "sre", "platform", "backend", "fullstack",
    "infrastructure", "cloud", "devops",
]

HARD_EXCLUDE = [
    # Seniority
    "senior", "sr.", "sr ", "Sr.", "Sr ",
    "staff", "principal", "distinguished",
    "director", "manager", "head of", "vp ", "vice president",
    "lead ", " lead", "tech lead", "team lead",
    "architect", "consultant",
    # Non-tech engineering (civil/mechanical/electrical etc.)
    "civil engineer", "structural engineer", "mechanical engineer",
    "electrical engineer", "chemical engineer", "process engineer",
    "validation engineer", "construction", "site engineer",
    "field engineer", "power engineer", "hvac", "bms",
    "building management", "building services",
    "graduate power", "graduate electrical", "graduate civil",
    "graduate structural", "graduate mechanical",
    "graduate construction", "graduate i &", "graduate i&c",
    # Hardware/chip
    "analog", "layout engineer", "asic", "fpga", "pcb",
    "hardware engineer",
    # Other noise
    "service operations", "power apps", "sales engineer",
    "pre-sales", "presales", "account executive",
    "recruiter", "hr ", "finance", "accounting", "tax ",
    "legal", "marketing", "design", "product manager",
]

IRELAND_TERMS = [
    "ireland", "dublin", "cork", "galway", "limerick",
    "waterford", "kilkenny", "wexford", "wicklow", "kildare",
    "meath", "louth", "irl", ", ie", "(ie)", "ie ",
]

EXCLUDE_NON_IRELAND_CITIES = [
    # Catch UK cities that sometimes appear
    "london", "manchester", "edinburgh", "glasgow", "birmingham",
    # US cities
    "new york", "san francisco", "seattle", "austin", "boston",
    # Other EU
    "amsterdam", "berlin", "paris", "madrid", "stockholm",
]
