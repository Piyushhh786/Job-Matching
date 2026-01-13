import re
from bs4 import BeautifulSoup, NavigableString, Tag
import string
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords # it will remove stop words
exlude = string.punctuation # english punctuation list
import html
import json


# from textblob import TextBlob # use for spell correction TextBlob(text).correct().string
NOISE_PATTERNS = [
    # Original list
    "about", "company", "we", "our","is","are",
    "openings", "worker type","community","us",
    "opportunity", "what","future","you",
    "culture", "values","motivated","fair","policy","success",
    
    # Legal & EEO
    "affirmative action", "disability", "veteran status", 
    "gender identity", "sexual orientation", "religion",
    "national origin", "reasonable accommodation", "equal employment",
    "protected", "qualified individuals", "disabled","veteran",
    "minorities", "women", "e-verify", "eeo employer",
    "equal opportunity employer", "eoe", "aa/eeo", "m/f/d/v",
    "without regard to race", "age", "color", "creed",
    "marital status", "pregnancy", "genetic information",
    "citizenship","status", "uniformed service", "protected class",
    "ada compliant", "title vii", "adea", "federal contractor",
    "does not discriminate", "prohibits discrimination",
    "fair chance employer", "ban the box", "second chance",
    
    # Benefits & Logistics
    "benefits", "401k", "medical", "dental", "vision", 
    "compensation", "salary range", "unlimited pto", 
    "requisition", "job id", "employment type", "work authorization",
    "health insurance", "life insurance", "flexible spending",
    "retirement plan", "pension", "stock options","hiring",
    "equity", "rsu", "profit sharing", "bonus structure","Note",
    "paid time off", "vacation days", "sick leave", "parental leave",
    "maternity leave", "paternity leave", "tuition reimbursement",
    "professional development", "gym membership", "wellness program","recruiters",
    "employee assistance", "commuter benefits", "remote work",
    "hybrid work", "relocation assistance", "signing bonus",
    "performance bonus", "annual bonus", "quarterly bonus",
    "insurance coverage", "disability insurance", "pet insurance",
    "competitive salary", "compensation package", "total rewards",
    
    # Marketing & Narrative
    "fast-paced", "cutting edge", "innovative", "leader",
    "proven track record", "passionate", "thrive in",
    "dynamic environment", "collaborative team", "rockstar",
    "ninja", "guru", "wizard", "unicorn", "superstar",
    "world-class", "best-in-class", "industry leading",
    "game changer", "disruptive", "revolutionary",
    "groundbreaking", "exciting opportunity", "unique opportunity",
    "be part of", "make an impact",
    "change the world", "transform", "reimagine",
    "wear many hats", "hit the ground running",
    "self-starter", "go-getter", "team player",
    "work hard play hard", "fun environment", "startup mentality",
    "entrepreneurial spirit", "move fast", "fail fast",
    "growth mindset", "customer obsessed", "data driven",
    "mission driven", "purpose driven", "values driven","hiring",
    
    # Company History & Background
    "founded", "established", "headquarters", "headquartered",
    "location", "offices worldwide", "global presence",
    "series", "series b", "series c", "funding round", "venture backed",
    "backed", "investors",
    "revenue", "customers worldwide", "user", "client",
    "fortune", "fortune 1000", "inc 5000", "forbes",
    "award","winning", "recognized", "ranked", "certified",
    "fastest", "industry awards", "accolades","growing","grow"
    "publicly traded", "nasdaq", "nyse", "private company",
    "billion dollar", "million users", "market leader",
    
    # Application Instructions
    "how to apply", "application process", "submit resume",
    "cover letter", "portfolio", "work samples",
    "references", "background check", "drug test",
    "application deadline", "no agencies", "no recruiters",
    "direct applicants only", "must be authorized",
    "sponsorship not available", "sponsor",
    "local candidates only", "must be willing to relocate",
    "relocation required", "onsite required",
    "in office", "return to office", "apply now",
    "interested candidates", "send resume to",
    
    # Diversity & Inclusion Statements
    "diversity", "inclusion", "belonging", "equity",
    "diverse workforce", "inclusive workplace", "all backgrounds",
    "underrepresented", "diverse perspectives", "committed to diversity",
    "celebrate diversity", "embrace differences",
    "inclusive culture", "safe space", "welcoming environment",
    "equal access", "accessibility", "accommodation available",
    
    # Job Posting Metadata
    "posted on", "date posted", "closing date", "open until filled",
    "position type", "employment status", "full time", "part time",
    "contract", "temporary", "permanent", "seasonal",
    "internship", "co-op", "apprenticeship",
    "entry level", "mid level", "senior level", "executive",
    "remote eligible", "location", "reports to",
    "department", "division", "team size", "job summary",
    "position summary", "role summary", "overview",
    "job description", "position description",
    
    # COVID-related
    "vaccination required", "vaccine mandate", "covid policy",
    "health and safety", "pandemic", "contactless",
    "social distancing", "mask policy","engaging","community",
    
    # Vague Responsibilities
    "other duties as assigned", "additional responsibilities",
    "ad hoc projects", "as needed", "from time to time",
    "occasionally", "may be required to", "could include",
    "miscellaneous tasks", "various duties",
    
    # Company Perks Fluff
    "free lunch", "catered meals", "snacks", "coffee",
    "beer on tap", "ping pong", "foosball", "game room",
    "standing desks", "ergonomic",
    "macbook", "choice of equipment", "home office stipend",
    "learning budget", "conference attendance", "book club",
    "happy hours", "team outings", "offsites", "retreats",
    "volunteer days", "charity matching", "giving back",
    "casual dress", "dress code", "flexible hours",
    "check",
    
    # # Buzzwords & Jargon
    # "synergy", "leverage", "utilize", "optimize", "maximize",
    # "streamline", "scalable", "agile", "lean", "iterative",
    # "holistic", "ecosystem", "platform", "end-to-end",
    # "turnkey", "plug and play", "seamless", "robust",
    # "enterprise grade", "mission critical", "strategic",
    # "tactical", "proactive", "reactive", "paradigm",
    # "bandwidth", "circle back", "touch base", "reach out",
    # "deep dive", "drill down", "unpack", "move the needle",
    # "low hanging fruit", "quick win", "north star",
    # "pivoting", "disrupt", "empower", "enable",
    
    # Disclaimers
    "subject to change", "at", "reserves","rights"
    "not all inclusive", "representative only", "may vary",
    "confidential information", "proprietary", "trade secrets",
    "without notice", "subject to approval",
    
    # Contact & Social
    "social media","growing","grow"
    "linkedin", "twitter", "facebook", "instagram",
    "website", "at",
    "contact", "email", "phone", "address",
    "careers page", "jobs site",
    
    # Experience level fluff  
    # "years of experience", "or more years", "minimum of",
    # "at least", "prefer", "strongly prefer", "highly desired",
    # "required experience", "background required",
    
    # Soft skills fluff (generic)
    # "excellent communication", "strong communication",""
    # "written and verbal", "interpersonal skills",
    # "attention to detail", "multitask", "prioritize",
    # "time management", "organizational skills",
    # "critical thinking", "analytical",
    # "work independently", "self-motivated", "driven",
    # "results oriented", "goal oriented", "deadline driven",
    # "positive attitude", "can-do attitude", "energetic",
    # "flexible", "adaptable", "resilient","organisation",
    
    # # Section Headers
    # "job summary", "position summary", "about the role",
    # "what you'll do", "responsibilities include",
    # "requirements", "qualifications", "what we're looking for",
    # "about you", "you have", "what you bring",
    # "what we offer", "why join us", "perks and benefits",
    # "compensation and benefits", "the role", "the position",
    # "job details", "position details", "role details"
]
TECH_KEYWORDS = [
    # Original
    "python", "java", "c#", "sql", "csharp", ".net", "linux", "cassandra", "net",
    "aws", "docker", "kubernetes", "html", "javascript", "nosql", "erp","win","win 32",

    # Programming Languages
    "golang", "rust", "typescript", "javascript", "ruby", "php", "swift", "c/c++",
    "kotlin", "scala", "c++", "cpp", "objective-c", "perl", "bash", 
    "powershell", "shell", "ruby", "matlab", "sas", "dart", "elixir", 
    "clojure", "haskell", "f#", "fsharp", "groovy", "lua", "julia",
    "vb.net", "vba", "assembly", "cobol", "fortran",

    # Frontend Frameworks & Libraries
    "react", "reactjs", "nextjs", "next.js", "angular", "angularjs",
    "vuejs", "vue.js", "vue", "svelte", "sveltekit", "ember", "backbone",
    "jquery", "tailwind", "tailwindcss", "bootstrap", "material-ui", "mui",
    "sass", "scss", "less", "styled-components", "css3", "html5",
    "webpack", "vite", "parcel", "rollup", "gulp", "grunt",
    "redux", "mobx", "recoil", "zustand", "rxjs",
    
    # Backend Frameworks
    "django", "flask", "fastapi", "spring", "spring boot", "node.js", 
    "nodejs", "express", "expressjs", "koa", "hapi", "nestjs",
    "laravel", "symfony", "rails", "ruby on rails", "sinatra",
    "asp.net", "asp.net core", ".net core", ".net framework",
    "entity framework", "ef core", "wcf", "wpf", "winforms",
    "servlet", "jsp", "struts", "hibernate", "play framework",
    
    # API & Architecture
    "graphql", "rest", "rest api", "restful", "soap", "grpc",
    "microservices", "api gateway", "swagger", "openapi",
    "json", "xml", "protobuf", "thrift", "avro",
    "webhook", "websocket", "oauth", "jwt", "saml",
    
    # Cloud Platforms & Services
    "azure", "gcp", "google cloud", "google cloud platform",
    "aws", "amazon web services", "ec2", "s3", "rds", "lambda",
    "cloudformation", "cloudfront", "route53", "elasticbeanstalk",
    "dynamodb", "sqs", "sns", "kinesis", "emr", "redshift",
    "devops", "azure functions", "storage",
    "cloud", "app engine", "compute engine",
    "firebase", "heroku","storage",
    "digitalocean", "linode", "vultr", "cloudflare",
    
    # DevOps & CI/CD
    "terraform", "terragrunt", "ansible", "puppet", "chef", "salt",
    "jenkins", "gitlab ci", "github actions", "circleci", "travis ci",
    "bamboo", "teamcity", "pipelines", "argo cd", "flux",
    "ci/cd", "continuous integration", "continuous deployment",
    "docker", "docker compose", "podman", "containerd",
    "kubernetes", "k8s", "helm", "kustomize", "istio", "linkerd",
    "prometheus", "grafana", "datadog", "new relic", "splunk",
    "elk", "elasticsearch", "logstash", "kibana", "fluentd",
    
    # Databases - SQL
    "sql",
    "postgresql", "postgres", "mysql", "mariadb", "oracle",
    "sql server", "mssql", "t-sql", "pl/sql", "sqlite",
    "db2", "sybase", "informix", "cockroachdb", "aurora",
    
    # Databases - 
    "nosql",
    "mongodb", "mongo", "couchdb", "couchbase", "cassandra",
    "redis", "memcached", "dynamodb", "neo4j", "arangodb",
    "orientdb", "riak", "hbase", "accumulo",
    
    # Data Engineering & Big Data
    "spark", "apache spark", "pyspark", "hadoop", "hdfs",
    "hive", "pig", "sqoop", "flume", "nifi", "airflow",
    "kafka", "apache kafka", "pulsar", "rabbitmq", "activemq",
    "flink", "storm", "beam", "databricks", "snowflake",
    "bigquery", "redshift", "athena", "presto", "trino",
    "dbt", "looker", "tableau", "power bi", "powerbi", "qlik",
    
    # Machine Learning & AI
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn",
    "jupyter", "notebook", "mlflow", "kubeflow", "sagemaker",
    "xgboost", "lightgbm", "catboost", "hugging",
    "transformers", "bert", "gpt", "llm", "nlp", "cv","computer vision",
    "opencv", "yolo", "detectron", "spacy", "nltk","statistics",
    
    # Mobile Development
    "android", "ios", "react native", "flutter", "xamarin",
    "cordova", "phonegap", "ionic", "swift", "swiftui",
    "objective-c", "kotlin", "java android", "jetpack compose",
    
    # Testing & Quality
    "selenium", "cypress", "playwright", "puppeteer", "testcafe",
    "jest", "mocha", "jasmine", "junit", "testng", "pytest",
    "unittest", "rspec", "cucumber", "behave", "postman",
    "jmeter", "gatling", "locust", "k6", "sonarqube",
    "unit testing", "integration testing", "e2e testing",
    
    # Version Control & Collaboration
    "git", "github", "gitlab", "bitbucket", "svn", "mercurial",
    "jira", "confluence", "trello", "asana", "monday",
    "slack", "teams", "zoom", "notion",
    
    # Operating Systems & Infrastructure
    "linux", "unix", "ubuntu", "centos", "rhel", "debian",
    "windows", "windows server", "macos", "freebsd",
    "nginx", "apache", "iis", "haproxy", "envoy", "traefik",
    "loadbalancer", "cdn", "cloudflare", "akamai",
    
    # Security
    "owasp", "penetration testing", "vulnerability assessment",
    "siem", "waf", "ids", "ips", "ssl", "tls", "pki",
    "vault", "secrets management", "kms", "encryption",
    
    # Methodologies & Practices
    "agile", "scrum", "kanban", "waterfall", "devops",
    "sre", "tdd", "bdd", "ddd", "clean code", "solid",
    "design patterns", "microservices", "monolith",
    "event-driven", "cqrs", "saga pattern",
    
    # ERP & Business Software
    "sap", "oracle erp", "netsuite", "microsoft dynamics",
    "dynamics 365", "nav", "microsoft nav", "navision",
    "salesforce", "crm", "workday", "servicenow",
    "peoplesoft", "jd edwards", "epicor",
    
    # Web Servers & Protocols
    "http", "https", "tcp/ip", "udp", "dns", "dhcp",
    "ftp", "sftp", "ssh", "smtp", "imap", "pop3",
    
    # Markup & Data Formats
    "html", "html5", "css", "css3", "xml", "json", "yaml",
    "toml", "markdown", "latex", "svg",
    
    # Other Technologies
    "blockchain", "ethereum", "solidity", "web3",
    "iot", "mqtt", "zigbee", "raspberry pi",
    "arduino", "embedded systems", "rtos",
    "unity", "unreal engine", "godot", "game development",
    "opengl", "vulkan", "directx", "webgl", "three.js",
    "d3.js", "chart.js", "plotly", "highcharts"
]
RESP_VERBS = {
    # Original
    "develop", "design", "implement", "create", "maintain", 
    "manage", "analyze", "evaluate", "deliver", "provide", 
    "support", "coordinate", "participate", "plan", "write", "observe",

    # Construction & Engineering
    "architect", "build", "code", "deploy", "debug", "engineer", 
    "integrate", "configure", "automate", "refactor", "optimize", 
    "prototype", "scale", "test", "validate", "script",
    "compile", "construct", "assemble", "synthesize", "craft",
    "program", "migrate", "upgrade", "patch", "release",
    
    # Strategy & Leadership
    "lead", "mentor", "supervise", "oversee", "spearhead", "drive", 
    "define", "roadmap", "prioritize", "influence", "guide", 
    "champion", "transform", "empower", "delegate", "direct",
    "orchestrate", "command", "govern", "steer", "pilot",
    "establish", "initiate", "launch", "pioneer",
    
    # Collaboration & Liaison
    "collaborate", "partner", "liaise", "present", "facilitate", 
    "consult", "advise", "train", "onboard", "align", "brief",
    "communicate", "engage", "interface", "network", "connect",
    "coordinate with", "work with", "team up", "cooperate",
    "sync", "share", "disseminate", "educate", "coach",
    
    # Operational & Analytical
    "monitor", "troubleshoot", "audit", "investigate", "resolve", 
    "refine", "enhance", "streamline", "modernize", "assess", 
    "forecast", "interpret", "measure", "track", "document",
    "diagnose", "identify", "detect", "discover", "uncover",
    "examine", "inspect", "review", "survey", "study",
    "quantify", "calculate", "compute", "estimate", "project",
    
    # Maintenance & Support
    "fix", "repair", "update", "maintain", "service",
    "sustain", "preserve", "uphold", "secure", "protect",
    "backup", "restore", "recover", "salvage",
    
    # Communication & Documentation
    "report", "document", "record", "log", "catalog",
    "publish", "communicate", "articulate", "explain",
    "describe", "specify", "detail", "outline", "draft",
    "prepare", "compile", "summarize", "synthesize",
    
    # Process & Workflow
    "execute", "perform", "conduct", "carry out", "run",
    "operate", "handle", "process", "administer", "control",
    "regulate", "standardize", "normalize", "systematize",
    "organize", "structure", "arrange", "order",
    
    # Improvement & Optimization
    "improve", "enhance", "optimize", "increase", "boost",
    "accelerate", "expedite", "advance", "elevate", "maximize",
    "minimize", "reduce", "decrease", "eliminate", "mitigate",
    "consolidate", "simplify", "rationalize",
    
    # Research & Innovation
    "research", "explore", "experiment", "investigate", "innovate",
    "ideate", "conceptualize", "brainstorm", "hypothesize",
    "discover", "invent", "formulate", "devise", "originate",
    
    # Quality & Compliance
    "ensure", "verify", "confirm", "certify", "approve",
    "enforce", "comply", "adhere", "follow", "meet",
    "satisfy", "fulfill", "achieve", "attain", "accomplish",
    
    # Data & Analytics
    "gather", "collect", "aggregate", "consolidate",
    "parse", "extract", "transform", "load", "etl",
    "visualize", "model", "simulate", "predict",
    "correlate", "cluster", "classify", "segment",
    
    # Deployment & Release
    "deploy", "release", "rollout", "ship", "deliver",
    "distribute", "install", "provision", "allocate",
    "stage", "promote", "push", "publish",
    
    # Security & Risk
    "secure", "protect", "safeguard", "defend", "shield",
    "encrypt", "authenticate", "authorize", "validate",
    "sanitize", "scan", "penetration test", "harden",
    
    # Acquisition & Procurement
    "acquire", "obtain", "procure", "source", "purchase",
    "negotiate", "contract", "vendor manage",
    
    # Review & Approval
    "review", "approve", "sign-off", "authorize", "endorse",
    "critique", "evaluate", "judge", "rate", "assess"
}
# from nltk.corpus import stopwords # for removing stoping words such as a,an,the,is from sentences which does not contribute to the meaning
from nltk.stem.porter import PorterStemmer 
ps = PorterStemmer()
stop_words = set(stopwords.words('english'))
def process_sentence(s): # we use this after getting the sentences...
    description = s.split()
    clean_description = [ps.stem(word) for word in description if not word in stop_words]
    clean_description = ' '.join(clean_description)
    return clean_description


def normalize_for_dedup(s: str) -> str:
    """Lowercase and remove special characters for matching."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"[,\[\]()]", " , ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract_sentences_from_html(html_text: str):
    """Parses HTML and breaks it down into clean, deduplicated sentences."""
    soup = BeautifulSoup(html_text, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    sentences = []

    def process_block(block):
        current = []
        for node in block.descendants:
            if isinstance(node, NavigableString):
                text = html.unescape(str(node))
                text = text.replace("\xa0", " ")
                text = re.sub(r"[•\t]", " ", text)
                current.append(text)
            elif isinstance(node, Tag) and node.name == "br":
                sent = "".join(current).strip()
                if sent: sentences.append(sent)
                current = []
        sent = "".join(current).strip()
        if sent: sentences.append(sent)

    for block in soup.find_all(["p", "li"]):
        process_block(block)

    for block in soup.find_all("div"):
        if not block.find(["p", "li"]):
            process_block(block)

    seen = set()
    final_sentences = []
    for s in sentences:
        key = normalize_for_dedup(s)
        s = s.replace("e.g.", "EG")
        if len(key) < 3: continue
        if key not in seen:
            seen.add(key)
            final_sentences.extend(
                part.strip() for part in re.split(r"\.\s+|[●•○<>;]", s) if len(part.strip()) >= 3
            )
    return final_sentences

def is_noise(s):
    for pat in NOISE_PATTERNS:
        pattern = rf"\b{re.escape(pat.lower())}\b"
        if re.search(pattern, s):
            return True
    return False

def extract_skills(sentence):
    s = normalize_for_dedup(sentence)
    skills = set()
    for tech in TECH_KEYWORDS:
        if tech.lower() in s:
            skills.add(tech)
    return list(skills)

def extract_responsibility(s):
    # s = sentence
    for verb in RESP_VERBS:
        if s.startswith(verb) or f"{verb} " in s:
            return True
    return False

def is_imp(sentence) -> bool:
    s = normalize_for_dedup(sentence)
    # print(s)

    for tech in TECH_KEYWORDS:
        pattern = rf"{re.escape(tech.lower())}\b"
        if re.search(pattern, s):
            # print(tech)
            return True
    if is_noise(s):
        return False
    return extract_responsibility(s)
# print(is_imp('experience with commercial clouds (aws, azure, gcp)'))

def get_skills_and_responsibility(sentences):
    """Main extraction logic: identifies skills and filters responsibilities."""
    extracted_skills = []
    temp_responsibility = []
    
    for s in sentences:
        if extract_responsibility(s):
            temp_responsibility.append(s)
        skills = extract_skills(s)
        extracted_skills.extend(skills)
    
    # Filter out noise from the identified responsibilities
    responsibility = [s for s in temp_responsibility if not is_noise(s)]
    
    data = {
        "skills": list(set(extracted_skills)),  # Unique skills
        "responsibility": responsibility,
    }
    return json.dumps(data, indent=4)