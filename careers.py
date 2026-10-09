"""Static catalogue: skills, careers, requirements and learning roadmaps.

Everything in this file is curated, editable content (not model output).
The required levels and weights are *judgement-based* estimates inspired by
typical entry-level job descriptions; they are not statistical results.
"""
from __future__ import annotations

LEVEL_LABELS = {1: "Beginner", 2: "Basic", 3: "Intermediate", 4: "Advanced", 5: "Expert"}

SKILLS: dict[str, str] = {
    "Python Programming": "Writing clean Python: functions, data structures, libraries.",
    "Mathematics & Statistics": "Probability, statistics, linear algebra and calculus basics.",
    "Data Analysis": "Cleaning, exploring and interpreting data (Pandas, Excel).",
    "SQL & Databases": "Querying and designing relational databases.",
    "Machine Learning": "Training, evaluating and applying ML models.",
    "Data Visualization": "Building clear charts and dashboards that support decisions.",
    "Communication": "Explaining ideas, writing, presenting and working with stakeholders.",
    "Problem Solving": "Breaking down problems, logical reasoning, debugging.",
    "Software Development": "Git, testing, APIs, project structure and deployment.",
}

RATING_GUIDE = (
    "1 = Beginner (just starting) · 2 = Basic (know the concepts) · "
    "3 = Intermediate (can do tasks with some help) · 4 = Advanced (work independently) · "
    "5 = Expert (can teach others)"
)

TECHNICAL_SKILL_OPTIONS = [
    "Python", "SQL", "Excel", "Pandas", "NumPy", "Scikit-learn", "TensorFlow / PyTorch",
    "Power BI", "Tableau", "Streamlit", "Git & GitHub", "HTML/CSS", "JavaScript",
    "R", "Statistics", "APIs", "Cloud basics", "Linux / Command line",
]
SOFT_SKILL_OPTIONS = [
    "Communication", "Teamwork", "Time management", "Leadership", "Critical thinking",
    "Creativity", "Adaptability", "Presentation", "Writing", "Negotiation",
]
EDUCATION_LEVELS = [
    "High school", "Diploma / Associate", "Undergraduate (in progress)", "Bachelor's graduate",
    "Master's (in progress)", "Master's graduate", "Other",
]
LEARNING_AREAS = [
    "Programming", "Data analysis", "Machine learning", "Databases", "Visualization",
    "Business & communication", "Software engineering", "AI product design",
]

# Task types used in roadmaps.
STUDY, EXERCISE, MINI, PORTFOLIO = "Study", "Exercise", "Mini-project", "Portfolio project"


def _mod(name: str, skill: str, tasks: list[tuple[str, str]]) -> dict:
    return {"module": name, "skill": skill, "tasks": tasks}


CAREERS: dict[str, dict] = {
    "Data Analyst": {
        "category": "Data",
        "overview": (
            "Data Analysts turn raw data into insight. They query databases, clean datasets, "
            "build dashboards and explain findings so teams can make better decisions."
        ),
        # skill: (required level 1-5, importance weight 1-3)
        "required_skills": {
            "Data Analysis": (4, 3), "SQL & Databases": (4, 3), "Data Visualization": (4, 2),
            "Mathematics & Statistics": (3, 2), "Python Programming": (3, 2),
            "Communication": (4, 2), "Problem Solving": (3, 1),
        },
        "tools": ["Excel", "SQL", "Python (Pandas)", "Power BI / Tableau", "Plotly", "Jupyter"],
        "projects": [
            "Sales performance dashboard from a public retail dataset",
            "Customer churn exploratory analysis with written recommendations",
            "SQL case study: answer 15 business questions on a sample database",
        ],
        "roadmap": [
            _mod("Data Foundations with Spreadsheets", "Data Analysis", [
                (STUDY, "Learn data types, tidy data and basic cleaning rules"),
                (EXERCISE, "Clean a messy CSV in Excel (duplicates, blanks, formats)"),
                (MINI, "Build a pivot-table summary of a small sales dataset"),
            ]),
            _mod("SQL for Analysts", "SQL & Databases", [
                (STUDY, "SELECT, WHERE, GROUP BY, ORDER BY and aggregate functions"),
                (EXERCISE, "Practise JOINs on three related tables"),
                (EXERCISE, "Write window-function queries (ranking, running totals)"),
                (MINI, "Answer 10 business questions on a sample database"),
            ]),
            _mod("Python for Data Analysis", "Python Programming", [
                (STUDY, "Python basics and the Pandas DataFrame"),
                (EXERCISE, "Load, filter, group and merge datasets in Pandas"),
                (MINI, "Exploratory analysis notebook on a public dataset"),
            ]),
            _mod("Statistics for Decisions", "Mathematics & Statistics", [
                (STUDY, "Descriptive statistics, distributions and sampling"),
                (EXERCISE, "Run and interpret a hypothesis test (t-test / chi-square)"),
                (MINI, "A/B test analysis write-up with confidence intervals"),
            ]),
            _mod("Dashboards & Data Storytelling", "Data Visualization", [
                (STUDY, "Chart selection principles and colour/readability basics"),
                (EXERCISE, "Recreate three charts in Plotly or Power BI"),
                (PORTFOLIO, "Publish an interactive dashboard with a short insights summary"),
                (EXERCISE, "Present your findings in a 5-minute walkthrough"),
            ]),
        ],
    },
    "Machine Learning Engineer": {
        "category": "Engineering",
        "overview": (
            "Machine Learning Engineers build, evaluate and deploy models. They combine "
            "programming, mathematics and software engineering to put ML into production."
        ),
        "required_skills": {
            "Python Programming": (4, 3), "Mathematics & Statistics": (4, 3),
            "Machine Learning": (4, 3), "Data Analysis": (3, 2), "Software Development": (3, 2),
            "Problem Solving": (4, 2), "SQL & Databases": (3, 1),
        },
        "tools": ["Python", "Scikit-learn", "PyTorch / TensorFlow", "Git", "Docker", "MLflow", "FastAPI"],
        "projects": [
            "End-to-end tabular prediction project with proper train/test evaluation",
            "Image or text classifier with an honest error analysis",
            "Model served through an API and a small Streamlit front-end",
        ],
        "roadmap": [
            _mod("Python & Engineering Basics", "Python Programming", [
                (STUDY, "Functions, OOP, virtual environments and packaging"),
                (EXERCISE, "Refactor a notebook into reusable modules"),
                (MINI, "Command-line tool that cleans and summarises a CSV"),
            ]),
            _mod("Mathematics for Machine Learning", "Mathematics & Statistics", [
                (STUDY, "Linear algebra: vectors, matrices, dot products"),
                (STUDY, "Probability and statistics essentials"),
                (EXERCISE, "Implement linear regression with NumPy only"),
            ]),
            _mod("Core Machine Learning", "Machine Learning", [
                (STUDY, "Supervised vs unsupervised learning, bias-variance trade-off"),
                (EXERCISE, "Train regression and classification models in scikit-learn"),
                (EXERCISE, "Compare models with cross-validation and a baseline"),
                (MINI, "Predict a target on a public dataset and document limitations"),
            ]),
            _mod("Data Preparation & Evaluation", "Data Analysis", [
                (STUDY, "Feature engineering, leakage and class imbalance"),
                (EXERCISE, "Build a scikit-learn Pipeline with preprocessing"),
                (MINI, "Error analysis report: where and why does the model fail?"),
            ]),
            _mod("Deployment & Collaboration", "Software Development", [
                (STUDY, "Git workflow, unit tests and basic CI"),
                (EXERCISE, "Save a model with Joblib and write an inference function"),
                (PORTFOLIO, "Deploy a model behind an API or Streamlit app with a README"),
            ]),
        ],
    },
    "Python Developer": {
        "category": "Engineering",
        "overview": (
            "Python Developers design and build software: back-end services, automation "
            "tools and applications, with a focus on clean, tested and maintainable code."
        ),
        "required_skills": {
            "Python Programming": (5, 3), "Software Development": (4, 3),
            "Problem Solving": (4, 2), "SQL & Databases": (3, 2),
            "Communication": (3, 1), "Data Analysis": (2, 1),
        },
        "tools": ["Python", "Git & GitHub", "pytest", "FastAPI / Flask", "SQLite / PostgreSQL", "Docker"],
        "projects": [
            "Command-line task manager with persistent storage and tests",
            "REST API with authentication-free CRUD endpoints and documentation",
            "Web scraper or automation script that saves results to a database",
        ],
        "roadmap": [
            _mod("Core Python", "Python Programming", [
                (STUDY, "Data types, control flow, comprehensions and error handling"),
                (EXERCISE, "Solve 20 beginner coding exercises"),
                (MINI, "Build a text-based quiz game with file storage"),
            ]),
            _mod("Algorithms & Problem Solving", "Problem Solving", [
                (STUDY, "Lists, dictionaries, sets, stacks, queues, Big-O basics"),
                (EXERCISE, "Solve 15 easy/medium problems on a coding practice site"),
                (EXERCISE, "Debug three broken programs using a debugger and tests"),
            ]),
            _mod("OOP, Testing & Git", "Software Development", [
                (STUDY, "Classes, modules, type hints and project structure"),
                (EXERCISE, "Write unit tests with pytest for an existing module"),
                (MINI, "Publish a small library to GitHub with a README and tests"),
            ]),
            _mod("Databases & APIs", "SQL & Databases", [
                (STUDY, "Relational design, SQL basics and parameterised queries"),
                (EXERCISE, "Use sqlite3 to build a CRUD layer"),
                (MINI, "Consume a public API and store results in SQLite"),
            ]),
            _mod("Build & Ship a Web App", "Software Development", [
                (STUDY, "HTTP basics and a web framework (FastAPI, Flask or Streamlit)"),
                (EXERCISE, "Add input validation and error handling"),
                (PORTFOLIO, "Deploy a full application with tests and documentation"),
            ]),
        ],
    },
    "Business Analyst": {
        "category": "Business",
        "overview": (
            "Business Analysts connect business needs with data and technology. They gather "
            "requirements, analyse processes and KPIs, and communicate recommendations."
        ),
        "required_skills": {
            "Communication": (5, 3), "Data Analysis": (4, 3), "SQL & Databases": (3, 2),
            "Data Visualization": (4, 2), "Problem Solving": (4, 2),
            "Mathematics & Statistics": (3, 1), "Python Programming": (2, 1),
        },
        "tools": ["Excel", "SQL", "Power BI / Tableau", "Jira / Trello", "Process mapping (BPMN)", "PowerPoint"],
        "projects": [
            "Requirements document and process map for a campus or small-business workflow",
            "KPI dashboard for a fictional retail company",
            "Cost-benefit analysis with a recommendation presentation",
        ],
        "roadmap": [
            _mod("Business Analysis Foundations", "Communication", [
                (STUDY, "BA lifecycle, stakeholders and requirement types"),
                (EXERCISE, "Write five user stories with acceptance criteria"),
                (MINI, "Interview a classmate and produce a requirements summary"),
            ]),
            _mod("Data Analysis for Business", "Data Analysis", [
                (STUDY, "KPIs, metrics and funnel thinking"),
                (EXERCISE, "Analyse a sales dataset in Excel or Pandas"),
                (MINI, "Identify three business insights with supporting evidence"),
            ]),
            _mod("SQL for Business Questions", "SQL & Databases", [
                (STUDY, "Joins, aggregations and filtering for reporting"),
                (EXERCISE, "Translate 10 business questions into SQL"),
            ]),
            _mod("Dashboards & KPIs", "Data Visualization", [
                (STUDY, "Dashboard design for executives"),
                (EXERCISE, "Build a KPI dashboard in Power BI, Tableau or Plotly"),
                (MINI, "Add commentary explaining what actions the numbers suggest"),
            ]),
            _mod("Process Improvement Case Study", "Problem Solving", [
                (STUDY, "Process mapping and root-cause analysis (5 Whys, fishbone)"),
                (EXERCISE, "Map an as-is and to-be process"),
                (PORTFOLIO, "Full case study: problem, analysis, recommendation, presentation"),
            ]),
        ],
    },
    "AI Product Builder": {
        "category": "Product",
        "overview": (
            "AI Product Builders design and ship useful AI-powered tools. They combine "
            "product thinking, light programming and responsible use of AI services."
        ),
        "required_skills": {
            "Python Programming": (3, 2), "Machine Learning": (3, 2),
            "Software Development": (3, 2), "Communication": (4, 2),
            "Problem Solving": (4, 2), "Data Analysis": (3, 1), "Data Visualization": (3, 1),
        },
        "tools": ["Python", "Streamlit", "LLM APIs", "Git & GitHub", "Prompt design", "Figma (optional)"],
        "projects": [
            "AI-assisted study planner with a simple Streamlit interface",
            "Document question-answering prototype with documented limitations",
            "Usability test report for an AI feature you built",
        ],
        "roadmap": [
            _mod("AI Concepts & Use-Case Discovery", "Machine Learning", [
                (STUDY, "What ML and generative AI can and cannot do"),
                (EXERCISE, "Write a one-page problem statement for an AI tool"),
                (MINI, "Compare 3 existing AI products: value, risks, limitations"),
            ]),
            _mod("Working with AI APIs", "Python Programming", [
                (STUDY, "HTTP APIs, JSON and keeping secrets out of code"),
                (EXERCISE, "Call an AI API from Python and handle errors"),
                (MINI, "Build a command-line assistant for one narrow task"),
            ]),
            _mod("Prototype with Streamlit", "Software Development", [
                (STUDY, "Streamlit layout, state and forms"),
                (EXERCISE, "Turn the command-line tool into a web interface"),
                (MINI, "Add input validation and a feedback form"),
            ]),
            _mod("Evaluate Responsibly", "Data Analysis", [
                (STUDY, "Evaluation sets, failure modes, bias and privacy basics"),
                (EXERCISE, "Create a 20-question test set and score your prototype"),
                (MINI, "Write a limitations and safety section for your README"),
            ]),
            _mod("Product Thinking & Communication", "Communication", [
                (STUDY, "User research, MVP scoping and prioritisation"),
                (EXERCISE, "Run a 3-person usability test"),
                (PORTFOLIO, "Publish the product with a demo link, README and short demo video"),
            ]),
        ],
    },
}

CATEGORIES = sorted({c["category"] for c in CAREERS.values()})
CAREER_NAMES = list(CAREERS)
