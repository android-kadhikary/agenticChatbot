from pathlib import Path
from dotenv import load_dotenv

# 1. Get the directory where THIS script is located
# (Base/backend/test/)
current_file_path = Path(__file__).resolve()

print (current_file_path)

# 2. Go up 3 levels to reach the "Base" directory
# level 1: Base/backend/
# level 2: Base/
project_root = current_file_path.parent.parent.parent

print (project_root)