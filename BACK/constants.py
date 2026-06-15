import os
from dotenv import load_dotenv
load_dotenv()

TIPOS_EVAL = {"Parcial", "Oral", "Final", "TP", "Recuperatorio"}
credenciales_email = (os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))