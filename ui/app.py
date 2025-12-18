import io
import os
import time
from typing import Any, Dict, List

import pandas as pd
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


def fetch_leads() -> List[Dict]:
    try:
        resp = requests.get(
            f"{get_backend_url().rstrip('/')}/leads",
            timeout=8,
        )
        if not resp.ok:
            return []
        data = resp.json()
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def get_leads_df() -> pd.DataFrame:
    leads = fetch_leads()
    if not leads:
        return pd.DataFrame(
            columns=["uuid", "name", "address", "phone", "website", "email"]
        )
    return pd.DataFrame(leads)


def fetch_stats() -> Dict[str, Any]:
    try:
        resp = requests.get(
            f"{get_backend_url().rstrip('/')}/stats",
            timeout=5,
        )
        if not resp.ok:
            return {}
        data = resp.json()
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}


def ensure_session_state() -> None:
    defaults = {
        "last_query": "",
        "is_running": False,
        "run_started_at": None,
        "baseline_count": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def main() -> None:
    ensure_session_state()

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
            help="FastAPI endpoint that exposes the `/run` and `/leads` routes.",
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

    col_main, col_side = st.columns([2.2, 1.4])

    # ── Main column: query, progress, results ─────────────────────────────
    with col_main:
        st.subheader("🔍 Lead Search")
        st.write(
            "Describe the businesses you want to find. "
            "Examples: `dentists in San Francisco`, `coffee shops near Times Square`, "
            "`IT consultancies in Berlin`."
        )

        query = st.text_input(
            "Business Search Query",
            value=st.session_state.get("last_query", ""),
            placeholder="e.g. dentists in Los Angeles",
        )

        col_run, col_clear = st.columns([1, 1])
        run_clicked = col_run.button(
            "🚀 Run Agent", type="primary", use_container_width=True
        )
        clear_clicked = col_clear.button("🧹 Clear", use_container_width=True)

        if clear_clicked:
            st.session_state["last_query"] = ""
            st.session_state["is_running"] = False
            st.session_state["run_started_at"] = None
            st.session_state["baseline_count"] = None
            st.experimental_rerun()

        # Initial data load for metrics and table
        leads_df = get_leads_df()
        total_leads = len(leads_df)

        if run_clicked:
            if not query.strip():
                st.error("Please enter a business search query.")
            else:
                st.session_state["last_query"] = query.strip()
                st.session_state["is_running"] = True
                st.session_state["run_started_at"] = time.time()
                st.session_state["baseline_count"] = total_leads

                with st.spinner("Starting agent in the background..."):
                    ok = trigger_agent(query.strip())

                if ok:
                    st.success(
                        "✅ Agent started successfully.\n\n"
                        "You can continue using this UI while the agent enriches "
                        "and sends leads to Google Sheets."
                    )
                else:
                    st.session_state["is_running"] = False
                    st.error(
                        "❌ Failed to contact the backend API.\n\n"
                        "- Ensure the FastAPI service is running\n"
                        "- If using Docker, check `docker-compose ps`\n"
                        "- Verify the **Backend API URL** in the sidebar"
                    )

        st.markdown("### ⏳ Live Progress")
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        stats = fetch_stats()
        status = stats.get("status") or ("running" if st.session_state.get("is_running") else "idle")

        if status == "running" and st.session_state.get("run_started_at"):
            # Use pages_processed as a simple proxy for progress (no strict upper bound).
            pages = int(stats.get("pages_processed") or 0)
            pct = max(5, min(pages * 10, 95))  # 10% per page, cap at 95%
            progress_placeholder.progress(pct, text=f"Agent running... ~{pct}%")

            # Re-fetch leads to detect growth since run started
            leads_df = get_leads_df()
            current_count = len(leads_df)
            baseline = st.session_state.get("baseline_count") or 0
            new_since_start = max(current_count - baseline, 0)

            status_placeholder.info(
                f"Status: **{status}**  ·  "
                f"Pages processed: **{int(stats.get('pages_processed') or 0)}**  ·  "
                f"New leads this run: **{new_since_start}**"
            )
        else:
            # Mark run as finished in UI if backend reports done or error.
            if status in {"done", "error"}:
                st.session_state["is_running"] = False

            progress_placeholder.progress(
                100 if status == "done" else 0,
                text="Agent finished" if status == "done" else "Agent idle",
            )
            status_placeholder.info(
                f"Status: **{status}**  ·  "
                f"Current total leads in Google Sheets: **{total_leads}**"
            )

        st.markdown("### 📋 Results")
        st.caption("Preview of leads currently stored in Google Sheets.")

        if leads_df.empty:
            st.warning("No leads found yet. Run the agent to start collecting data.")
        else:
            # Ensure standard column order if these fields exist
            preferred_cols = ["uuid", "name", "address", "phone", "website", "email"]
            cols = [c for c in preferred_cols if c in leads_df.columns] + [
                c for c in leads_df.columns if c not in preferred_cols
            ]
            leads_df = leads_df[cols]

            st.dataframe(
                leads_df,
                use_container_width=True,
                hide_index=True,
            )

            # Export options
            st.markdown("#### 📤 Export")

            csv_buf = io.StringIO()
            leads_df.to_csv(csv_buf, index=False)
            st.download_button(
                "⬇️ Download CSV",
                data=csv_buf.getvalue(),
                file_name="osm_agentic_leads.csv",
                mime="text/csv",
            )

            json_buf = io.StringIO()
            json_buf.write(leads_df.to_json(orient="records", force_ascii=False))
            st.download_button(
                "⬇️ Download JSON",
                data=json_buf.getvalue(),
                file_name="osm_agentic_leads.json",
                mime="application/json",
            )

    # ── Side column: metrics, dedup stats, tips ───────────────────────────
    with col_side:
        st.subheader("📊 Metrics")
        if "leads_df" not in locals():
            leads_df = get_leads_df()
        total_leads = len(leads_df)
        unique_names = leads_df["name"].nunique() if "name" in leads_df else 0
        unique_emails = leads_df["email"].nunique() if "email" in leads_df else 0

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Total leads", total_leads)
        with c2:
            st.metric("Unique emails", unique_emails)

        c3, c4 = st.columns(2)
        with c3:
            st.metric("Unique names", unique_names)
        with c4:
            avg_per_name = round(total_leads / unique_names, 2) if unique_names else 0
            st.metric("Avg leads / name", avg_per_name)

        st.markdown("### 🧠 Dedup stats")
        if not leads_df.empty and "email" in leads_df:
            dup_counts = leads_df["email"].value_counts()
            duplicate_emails = dup_counts[dup_counts > 1]
            num_dup_groups = len(duplicate_emails)
            num_dup_rows = int(duplicate_emails.sum() - num_dup_groups)

            st.write(
                f"- Duplicate groups by email: **{num_dup_groups}**  \n"
                f"- Extra rows beyond first occurrence: **{num_dup_rows}**"
            )

            with st.expander("Show duplicate email groups"):
                dup_df = leads_df[leads_df["email"].isin(duplicate_emails.index)]
                st.dataframe(
                    dup_df.sort_values("email"),
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("No deduplication stats yet (need at least one `email` column).")

        st.markdown("### 💡 Tips")
        st.markdown(
            "- Start with **narrow, location-specific queries**\n"
            "- Avoid hammering Nominatim with many rapid runs\n"
            "- Keep your Google Sheet open to watch new rows appear in real‑time"
        )


if __name__ == "__main__":
    main()


