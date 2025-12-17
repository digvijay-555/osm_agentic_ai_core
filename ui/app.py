# UI application

import streamlit as st
import requests

st.set_page_config(layout="wide")

query = st.text_input("Business Search Query")

if st.button("Run Agent"):
    requests.post("http://localhost:8000/run", params={"query": query})
    st.success("Agent running in background")
