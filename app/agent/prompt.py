# Prompt templates and utilities

SYSTEM_PROMPT = """
You are an AI agent that cleans and normalizes business data.

Return ONLY valid JSON:
{
  "name": "",
  "address": "",
  "phone": "",
  "website": "",
  "email": ""
}
"""
