import os
import dotenv
from datetime import datetime

dotenv.load_dotenv()

a = datetime.strptime(os.getenv("DATE_FROM"), "%Y-%m-%dT%H:%M:%S.000Z")
print(a.strftime("%Y-%m"))
