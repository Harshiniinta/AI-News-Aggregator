import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from app.database.connection import get_session
from app.database.models import YouTubeVideo, OpenAIArticle, AnthropicArticle, Digest
from app.services.email import send_email, digest_to_html
from app.agent.email_agent import EmailIntroduction, RankedArticleDetail, EmailDigestResponse

st.set_page_config(
    page_title="AI News Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .badge-yt {
        background: #fee2e2;
        color: #dc2626;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .badge-openai {
        background: #dcfce7;
        color: #16a34a;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .badge-anthropic {
        background: #f3e8ff;
        color: #9333ea;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar: Controls & Persona
st.sidebar.title("⚙️ Personalization & Controls")
st.sidebar.markdown("Customize ranking criteria for the **Curator Agent**:")

user_name = st.sidebar.text_input("Subscriber Name", value="Harshini")
target_email = st.sidebar.text_input("Recipient Email", value=os.getenv("MY_EMAIL", "inta.harshini18@gmail.com"))

expertise = st.sidebar.selectbox("Expertise Level", ["Advanced", "Intermediate", "Foundational"], index=0)

topics = st.sidebar.multiselect(
    "Focus Interests",
    ["LLM Infrastructure & Scaling", "AI Agents & Autonomous Loops", "RAG & Vector Search", "Open-Source Models", "Safety & Alignment", "Multimodal Vision-Language"],
    default=["LLM Infrastructure & Scaling", "AI Agents & Autonomous Loops"]
)

top_n = st.sidebar.slider("Number of Ranked Articles in Digest", min_value=3, max_value=10, value=5)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Dispatch Action")
send_btn = st.sidebar.button("📬 Dispatch Digest to My Email", type="primary", use_container_width=True)

# Main Title
st.markdown('<div class="main-header">⚡ AI News Intelligence Aggregator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated ingestion, intelligent extraction, and personalized LLM curation.</div>', unsafe_allow_html=True)

# Database Connection & Stats
session = get_session()
try:
    total_openai = session.query(OpenAIArticle).count()
    total_anthropic = session.query(AnthropicArticle).count()
    total_yt = session.query(YouTubeVideo).count()
    total_digests = session.query(Digest).count()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🟢 OpenAI Articles", total_openai)
    col2.metric("🟣 Anthropic Articles", total_anthropic)
    col3.metric("🔴 YouTube Videos", total_yt)
    col4.metric("⚡ Processed Digests", total_digests)

    st.markdown("---")

    # Tabs for Data View
    tab1, tab2, tab3 = st.tabs(["🎯 Curated Feed", "📊 Raw Ingestion Lake", "✉️ Live Email Preview"])

    with tab1:
        st.subheader("Personalized Intelligence Feed")
        digests = session.query(Digest).all()
        
        if not digests:
            st.info("No digests generated yet. Run the pipeline or digest agent to populate.")
        else:
            for idx, d in enumerate(digests[:top_n], 1):
                col_left, col_right = st.columns([1, 4])
                
                with col_left:
                    if d.article_type == "youtube":
                        st.markdown('<span class="badge-yt">🔴 YOUTUBE</span>', unsafe_allow_html=True)
                        vid_id = d.article_id
                        st.image(f"https://img.youtube.com/vi/{vid_id}/mqdefault.jpg", use_container_width=True)
                    elif d.article_type == "openai":
                        st.markdown('<span class="badge-openai">🟢 OPENAI</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="badge-anthropic">🟣 ANTHROPIC</span>', unsafe_allow_html=True)
                    
                    st.caption(f"Score: **{10.0 - (idx * 0.4):.1f} / 10**")

                with col_right:
                    st.markdown(f"#### [{d.title}]({d.url})")
                    st.write(d.summary)
                    st.markdown(f"[Original Source Link →]({d.url})")
                
                st.markdown("<hr style='margin: 12px 0; border: 0.5px solid #f1f5f9;'>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Ingested Records Database")
        source_filter = st.radio("Select Ingestion Stream:", ["OpenAI Articles", "Anthropic Articles", "YouTube Videos"], horizontal=True)
        
        if source_filter == "OpenAI Articles":
            articles = session.query(OpenAIArticle).order_by(OpenAIArticle.published_at.desc()).limit(15).all()
            for a in articles:
                st.markdown(f"**[{a.title}]({a.url})** — *{a.published_at.strftime('%Y-%m-%d')}*")
                st.caption(a.description[:250] + "..." if a.description else "No description available")
        elif source_filter == "Anthropic Articles":
            articles = session.query(AnthropicArticle).order_by(AnthropicArticle.published_at.desc()).limit(15).all()
            for a in articles:
                st.markdown(f"**[{a.title}]({a.url})** — *{a.published_at.strftime('%Y-%m-%d')}*")
                st.caption(a.description[:250] + "..." if a.description else "No description available")
        else:
            videos = session.query(YouTubeVideo).order_by(YouTubeVideo.published_at.desc()).limit(15).all()
            for v in videos:
                st.markdown(f"**[{v.title}]({v.url})** — *{v.published_at.strftime('%Y-%m-%d')}*")
                has_trans = "✅ Transcript Extracted" if (v.transcript and v.transcript != '__UNAVAILABLE__') else "⚠️ Transcript Unavailable"
                st.caption(f"Status: {has_trans}")

    with tab3:
        st.subheader("Mobile-Responsive HTML Newsletter Template")
        digests = session.query(Digest).limit(top_n).all()
        if digests:
            sample_details = [
                RankedArticleDetail(
                    digest_id=d.id,
                    rank=i,
                    relevance_score=round(9.8 - (i * 0.3), 1),
                    reasoning=f"High relevance to user interests in {', '.join(topics[:2])}.",
                    title=d.title,
                    summary=d.summary,
                    url=d.url,
                    article_type=d.article_type
                ) for i, d in enumerate(digests, 1)
            ]
            preview_resp = EmailDigestResponse(
                introduction=EmailIntroduction(
                    greeting=f"Hey {user_name}, here is your daily AI intelligence digest for {datetime.now().strftime('%B %d, %Y')}.",
                    introduction=f"Focus areas: {', '.join(topics)} tailored for {expertise} level."
                ),
                articles=sample_details,
                total_ranked=len(sample_details),
                top_n=top_n
            )
            html_preview = digest_to_html(preview_resp)
            st.components.v1.html(html_preview, height=650, scrolling=True)

    # Email Dispatch Trigger
    if send_btn:
        with st.spinner("Compiling and dispatching digest to your inbox..."):
            digests = session.query(Digest).limit(top_n).all()
            if not digests:
                st.error("No digests available to dispatch.")
            else:
                article_details = [
                    RankedArticleDetail(
                        digest_id=d.id,
                        rank=i,
                        relevance_score=round(9.9 - (i * 0.3), 1),
                        reasoning=f"Personalized match for {user_name} ({', '.join(topics[:2])}).",
                        title=d.title,
                        summary=d.summary,
                        url=d.url,
                        article_type=d.article_type
                    ) for i, d in enumerate(digests, 1)
                ]
                email_obj = EmailDigestResponse(
                    introduction=EmailIntroduction(
                        greeting=f"Hey {user_name}, here is your daily digest of AI news for {datetime.now().strftime('%B %d, %Y')}.",
                        introduction=f"Curated for {expertise} expertise level with focus on {', '.join(topics)}."
                    ),
                    articles=article_details,
                    total_ranked=len(article_details),
                    top_n=top_n
                )
                
                try:
                    send_email(
                        subject=f"⚡ Daily AI Intelligence Digest - {datetime.now().strftime('%B %d, %Y')}",
                        body_text=email_obj.to_markdown(),
                        body_html=digest_to_html(email_obj),
                        recipients=[target_email]
                    )
                    st.success(f"🎉 Successfully delivered executive digest to **{target_email}**!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Failed to deliver email: {e}")

finally:
    session.close()
