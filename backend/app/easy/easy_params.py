import os

from dotenv import load_dotenv

load_dotenv()

IS_LOCAL = True

OUTLOOK_ID = os.getenv("OUTLOOK_ID")
OUTLOOK_SECRET = os.getenv("OUTLOOK_SECRET")

EMAIL = "asier.tena.zu@outlook.com"
# EMAIL = "alberdi.autom@outlook.com"
# EMAIL = "asier.tena.zu@ammonitammonit.onmicrosoft.com"
