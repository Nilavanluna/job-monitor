# Shared keyword config — single source of truth for all scrapers

KEYWORDS = [
    # Core tech roles
    "software engineer", "software developer", "systems engineer",
    "cloud engineer", "devops engineer", "site reliability engineer",
    "platform engineer", "infrastructure engineer", "network engineer",
    "security engineer", "data engineer", "backend engineer",
    "fullstack engineer", "full stack engineer", "full-stack engineer",
    "solutions engineer", "support engineer", "automation engineer",
    "ml engineer", "ai engineer", "machine learning engineer",
    "reliability engineer",
    # Level signals
    "graduate", "junior", "intern", "internship", "entry level",
    "entry-level", "associate engineer", "associate developer",
    "associate software", "early careers", "early career",
    "graduate programme", "new grad", "trainee", "apprentice",
    # Tech keywords in titles
    "kubernetes", "terraform", "devsecops", "mlops", "aiops",
    "observability", "developer", "sre", "platform", "backend",
    "fullstack", "infrastructure", "cloud", "devops",
]

HARD_EXCLUDE = [
    # Seniority
    "senior", "sr.", "sr ", "Sr.", "Sr ",
    "staff", "principal", "distinguished",
    "director", "manager", "head of", "vp ", "vice president",
    "lead ", " lead", "tech lead", "team lead",
    "architect", "consultant",
    # Non-software engineering — physical/civil/mechanical
    "civil engineer", "structural engineer", "mechanical engineer",
    "electrical engineer", "chemical engineer", "process engineer",
    "validation engineer", "construction", "site engineer",
    "field engineer", "power engineer", "hvac", "bms",
    "building management", "building services",
    "graduate power", "graduate electrical", "graduate civil",
    "graduate structural", "graduate mechanical",
    "graduate construction", "graduate i &", "graduate i&c",
    "graduate csa", "graduate csa engineer",
    # Hardware
    "analog", "layout engineer", "asic", "fpga", "pcb",
    "hardware engineer",
    # Business/non-tech
    "service operations", "power apps", "sales engineer",
    "pre-sales", "presales", "account executive",
    "recruiter", "finance", "accounting", "tax ",
    "legal", "marketing",
]

IRELAND_TERMS = [
    "ireland", "dublin", "cork", "galway", "limerick",
    "waterford", "kilkenny", "wexford", "wicklow", "kildare",
    "meath", "louth", "irl", ", ie", "(ie)", "ie ",
]

EXCLUDE_NON_IRELAND_CITIES = [
    "london", "manchester", "edinburgh", "glasgow", "birmingham",
    "new york", "san francisco", "seattle", "austin", "boston",
    "amsterdam", "berlin", "paris", "madrid", "stockholm",
    "sydney", "singapore", "warsaw", "prague", "brno",
]
