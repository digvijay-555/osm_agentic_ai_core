# Email tool

import re

def extract(text):
    emails = re.findall(r"[\\w.-]+@[\\w.-]+\\.\\w+", text)
    return emails[0] if emails else "N/A"
