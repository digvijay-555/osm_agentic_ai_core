# Email tool

import re

def extract(text):
    # Fixed regex pattern - was using escaped backslashes incorrectly
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(pattern, text)
    return emails[0] if emails else "N/A"
