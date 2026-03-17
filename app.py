import streamlit as st
from core.mock_data import agencies
from core.agent import run_trust_agent

st.set_page_config(
    page_title="JSO Trust Agent",
    page_icon="🔍",
    layout="centered"
)

st.title("JSO Agency Trust Agent")
st.caption("AI-powered agency reputation analysis")

# Agency selection
st.subheader("Select an Agency to Analyze")

agency_names = [a["name"] for a in agencies]
selected_name = st.selectbox("Choose agency", agency_names)

selected_agency = next(a for a in agencies if a["name"] == selected_name)

if st.button("Analyze Agency", type="primary"):
    with st.spinner("Agent is analyzing agency..."):
        result = run_trust_agent(selected_agency)

    # Score color
    score = result["score"]
    if score >= 70:
        score_color = "green"
    elif score >= 40:
        score_color = "orange"
    else:
        score_color = "red"

    # Recommendation color
    rec = result["recommendation"]
    if rec == "TRUSTED":
        rec_color = "green"
    elif rec == "CAUTION":
        rec_color = "orange"
    else:
        rec_color = "red"

    st.divider()

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(result["agency_name"])
        st.caption(f"Confidence: {result['confidence']}")
    with col2:
        st.metric("Trust Score", f"{score}/100")

    # Recommendation badge
    st.markdown(
        f"**Recommendation:** :{rec_color}[{rec}]"
    )

    st.divider()

    # Explanation
    st.subheader("Agent Analysis")
    st.write(result["explanation"])

    # Sentiment
    st.subheader("Review Sentiment")
    st.write(result["sentiment"])

    # Red flags
    if result["red_flags"]:
        st.subheader("⚠️ Red Flags")
        for flag in result["red_flags"]:
            st.error(flag)

    # Score breakdown
    st.subheader("Score Breakdown")
    breakdown = result["breakdown"]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Placement Rate", f"{breakdown['placement_score']}/100", help="40% weight")
        st.progress(breakdown["placement_score"] / 100)

        st.metric("Reviews", f"{breakdown['review_score']}/100", help="30% weight")
        st.progress(breakdown["review_score"] / 100)

    with col2:
        st.metric("Response Time", f"{breakdown['response_score']}/100", help="20% weight")
        st.progress(breakdown["response_score"] / 100)

        st.metric("Verification", f"{breakdown['verification_score']}/100", help="10% weight")
        st.progress(breakdown["verification_score"] / 100)

    # Flagged reviews warning
    if result["flagged_reviews"] > 0:
        st.warning(
            f"⚠️ {result['flagged_reviews']} suspicious review(s) detected and excluded from scoring"
        )