import os

import requests
import streamlit as st


st.set_page_config(
    page_title="OSM Agentic Lead Finder",
    page_icon="🗺️",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def get_backend_url() -> str:
    # Allow overriding via env var in Docker / local
    return os.getenv("BACKEND_URL", "http://localhost:8000")


def trigger_agent(query: str) -> bool:
    try:
        resp = requests.post(
            f"{get_backend_url().rstrip('/')}/run",
            params={"query": query},
            timeout=5,
        )
        return resp.ok
    except Exception:
        return False


def main() -> None:
    st.title("🧠 OSM Agentic AI — Lead Discovery")
    st.caption(
        "Search OpenStreetMap for businesses, enrich with AI, "
        "deduplicate using embeddings, and push to Google Sheets."
    )

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        backend_url = st.text_input(
            "Backend API URL",
            value=get_backend_url(),
            help="FastAPI endpoint that exposes the `/run` route.",
        )
        if backend_url != get_backend_url():
            # Note: this only affects current session requests
            os.environ["BACKEND_URL"] = backend_url

        st.markdown("---")
        st.subheader("ℹ️ How it works")
        st.markdown(
            "- Uses **Nominatim (OSM)** to search for businesses\n"
            "- Cleans & normalizes data via **LLM (Ollama)**\n"
            "- Detects duplicates using **FAISS + embeddings**\n"
            "- Appends final leads into **Google Sheets**"
        )

    col_main, col_meta = st.columns([2.2, 1.3])

    with col_main:
        st.subheader("🔍 Lead Search")
        st.write(
            "Describe the businesses you want to find. "
            "Examples: `dentists in San Francisco`, `coffee shops near Times Square`, "
            "`IT consultancies in Berlin`."
        )

        query = st.text_input(
            "Business Search Query",
            placeholder="e.g. dentists in Los Angeles",
        )

        col_run, col_clear = st.columns([1, 1])
        run_clicked = col_run.button("🚀 Run Agent", type="primary", use_container_width=True)
        clear_clicked = col_clear.button("🧹 Clear", use_container_width=True)

        if clear_clicked:
            st.experimental_rerun()

        if run_clicked:
            if not query.strip():
                st.error("Please enter a business search query.")
            else:
                with st.spinner("Starting agent in the background..."):
                    ok = trigger_agent(query.strip())

                if ok:
                    st.success(
                        "✅ Agent started successfully.\n\n"
                        "You can continue using this UI while the agent enriches "
                        "and sends leads to Google Sheets."
                    )
                else:
                    st.error(
                        "❌ Failed to contact the backend API.\n\n"
                        "- Ensure the FastAPI service is running\n"
                        "- If using Docker, check `docker-compose ps`\n"
                        "- Verify the **Backend API URL** in the sidebar"
                    )

    with col_meta:
        st.subheader("📊 Status & Tips")
        st.info(
            "Leads are appended directly to your configured Google Sheet. "
            "Open the sheet in a separate tab to monitor progress in real‑time."
        )

        st.markdown("#### ✅ Best practices")
        st.markdown(
            "- Start with **narrow queries** (one city / area)\n"
            "- Avoid overly generic terms (e.g. just `restaurants`)\n"
            "- Respect Nominatim usage policy and avoid rapid repeated runs"
        )

        st.markdown("#### 🔍 Debugging")
        st.markdown(
            "- If nothing appears in Sheets, inspect backend logs\n"
            "- Validate that your `credentials.json` and `SPREADSHEET_ID` are correct\n"
            "- Check Ollama is running and reachable from the API container"
        )


if __name__ == "__main__":
    main()

