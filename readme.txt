project requirements step by step:
===================================
create new frontend and backend files
instal https://pypi.org/project/langgraph-checkpoint-sqlite/
pip install langgraph-checkpoint-sqlite (for longterm mem)


implement database in backend
chat in multiple threads
intall and visualize
integrate to frontend

integrate langsmith for observability and moritoring


UV :
=====
uv venv
.venv\Scripts\Activate.ps1 (if needed)
uvx pipreqs . (generate the requirements.txt file if not avaialble)
uv pip install -r requirements.txt

Deploy in Streamlit:
=========================

1) Organize Your Project Files
ProjectName/
│
├── frontend.py            <-- Your Streamlit file (contains st.title, etc.)
├── backend_logic.py       <-- Your backend logic file
└── requirements.txt       <-- Tells the cloud what to install
2) Push Your Code to GitHub
git add .
git commit -m "Switching frontend to Streamlit"
git push origin main
3)Make it Live on Streamlit Cloud
    (i)Go to share.streamlit.io and log in using your GitHub account.

    (ii)Click the "Create app" button in the top right corner.

    (iii)Fill in the deployment details (Streamlit will auto-suggest these if your GitHub is linked):

        Repository: Choose your TalentScreen repository.

        Branch: Select main.

        Main file path: Type frontend.py (tells it which file starts the app).

    (iv)(Optional) If your backend needs hidden API keys, look for the Advanced settings gear icon on that screen, and paste them into the Secrets box like this:
        "Ini, TOML
    OPENAI_API_KEY = "your-api-key-here""
    (v)Click "Deploy!"