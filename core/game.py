import os 
import asyncio
import google.generativeai as gen
from dotenv import load_dotenv

from core.crisis import CRISES
from core.advisor import Council

load_dotenv()
gen.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = gen.GenerativeModel("gemini-2.5-flash-preview-05-20")