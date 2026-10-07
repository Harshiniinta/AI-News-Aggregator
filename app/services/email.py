import os
import smtplib
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import markdown

load_dotenv()

MY_EMAIL = os.getenv("MY_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def send_email(subject: str, body_text: str, body_html: str = None, recipients: list = None):
    if recipients is None:
        if not MY_EMAIL:
            raise ValueError("MY_EMAIL environment variable is not set")
        recipients = [MY_EMAIL]
    
    recipients = [r for r in recipients if r is not None]
    if not recipients:
        raise ValueError("No valid recipients provided")
    
    if not MY_EMAIL:
        raise ValueError("MY_EMAIL environment variable is not set")
    if not APP_PASSWORD:
        raise ValueError("APP_PASSWORD environment variable is not set")
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = MY_EMAIL
    msg["To"] = ", ".join(recipients)
    
    part1 = MIMEText(body_text, "plain")
    msg.attach(part1)
    
    if body_html:
        part2 = MIMEText(body_html, "html")
        msg.attach(part2)
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(MY_EMAIL, APP_PASSWORD)
        smtp.sendmail(MY_EMAIL, recipients, msg.as_string())


def markdown_to_html(markdown_text: str) -> str:
    html = markdown.markdown(markdown_text, extensions=['extra', 'nl2br'])
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }}
        h2 {{
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 24px;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        h3 {{
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 20px;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        p {{
            margin: 8px 0;
            color: #4a4a4a;
        }}
        strong {{
            font-weight: 600;
            color: #1a1a1a;
        }}
        em {{
            font-style: italic;
            color: #666;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e5e5e5;
            margin: 20px 0;
        }}
        .greeting {{
            font-size: 16px;
            font-weight: 500;
            color: #1a1a1a;
            margin-bottom: 12px;
        }}
        .introduction {{
            color: #4a4a4a;
            margin-bottom: 20px;
        }}
        .article-link {{
            display: inline-block;
            margin-top: 8px;
            color: #0066cc;
            font-size: 14px;
        }}
    </style>
</head>
<body>
{html}
</body>
</html>"""


def digest_to_html(digest_response) -> str:
    from app.agent.email_agent import EmailDigestResponse
    
    if not isinstance(digest_response, EmailDigestResponse):
        return markdown_to_html(digest_response.to_markdown() if hasattr(digest_response, 'to_markdown') else str(digest_response))
    
    greeting_html = markdown.markdown(digest_response.introduction.greeting, extensions=['extra', 'nl2br'])
    introduction_html = markdown.markdown(digest_response.introduction.introduction, extensions=['extra', 'nl2br'])
    
    article_cards = []
    for article in digest_response.articles:
        # Determine source badge styling
        source_type = (article.article_type or "article").lower()
        if source_type == "youtube":
            badge_bg = "#fee2e2"
            badge_color = "#dc2626"
            badge_label = "🔴 YouTube Video"
            # Extract video ID for thumbnail if youtube
            video_id = ""
            if "watch?v=" in article.url:
                video_id = article.url.split("watch?v=")[1].split("&")[0]
            elif "youtu.be/" in article.url:
                video_id = article.url.split("youtu.be/")[1].split("?")[0]
            thumbnail_html = f'<div style="margin-bottom:12px;"><a href="{html.escape(article.url)}"><img src="https://img.youtube.com/vi/{video_id}/mqdefault.jpg" style="width:100%; border-radius:8px; display:block;" alt="Thumbnail" /></a></div>' if video_id else ""
        elif source_type == "openai":
            badge_bg = "#dcfce7"
            badge_color = "#15803d"
            badge_label = "🟢 OpenAI Research"
            thumbnail_html = ""
        elif source_type == "anthropic":
            badge_bg = "#f3e8ff"
            badge_color = "#7e22ce"
            badge_label = "🟣 Anthropic Blog"
            thumbnail_html = ""
        else:
            badge_bg = "#e0f2fe"
            badge_color = "#0369a1"
            badge_label = f"📰 {source_type.capitalize()}"
            thumbnail_html = ""
        
        score_badge = f'<span style="background:#f1f5f9; color:#475569; font-size:12px; font-weight:600; padding:3px 8px; border-radius:12px; margin-left:6px;">⭐ {article.relevance_score:.1f}/10</span>' if hasattr(article, 'relevance_score') and article.relevance_score else ""
        summary_html = markdown.markdown(article.summary, extensions=['extra', 'nl2br'])
        
        card = f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:20px; margin-bottom:20px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="margin-bottom:12px;">
                <span style="background:{badge_bg}; color:{badge_color}; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; padding:3px 10px; border-radius:12px;">{badge_label}</span>
                {score_badge}
            </div>
            {thumbnail_html}
            <h3 style="margin:0 0 10px 0; font-size:18px; font-weight:700; line-height:1.35; color:#0f172a;">
                <a href="{html.escape(article.url)}" style="color:#0f172a; text-decoration:none;">{html.escape(article.title)}</a>
            </h3>
            <div style="font-size:14px; line-height:1.6; color:#334155; margin-bottom:14px;">
                {summary_html}
            </div>
            <div style="text-align:right;">
                <a href="{html.escape(article.url)}" style="display:inline-block; background:#0ea5e9; color:#ffffff; font-size:13px; font-weight:600; text-decoration:none; padding:8px 16px; border-radius:6px;">View Original →</a>
            </div>
        </div>
        """
        article_cards.append(card)
    
    cards_html = "\n".join(article_cards)
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color:#f8fafc; margin:0; padding:24px 12px; color:#1e293b;">
    <div style="max-width:620px; margin:0 auto;">
        <!-- Header Banner -->
        <div style="background:linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius:14px; padding:28px 24px; color:#ffffff; margin-bottom:24px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
            <div style="font-size:12px; font-weight:700; letter-spacing:1px; color:#38bdf8; text-transform:uppercase; margin-bottom:6px;">Intelligence Feed</div>
            <h1 style="margin:0 0 12px 0; font-size:24px; font-weight:800; letter-spacing:-0.5px;">Daily AI News Digest</h1>
            <div style="font-size:14px; line-height:1.5; color:#cbd5e1; margin-bottom:12px;">{greeting_html}</div>
            <div style="font-size:13px; line-height:1.5; color:#94a3b8; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">{introduction_html}</div>
        </div>
        
        <!-- Articles Feed -->
        {cards_html}
        
        <!-- Footer -->
        <div style="text-align:center; padding:20px; font-size:12px; color:#94a3b8;">
            AI News Aggregator • Curated automatically with LLM agents
        </div>
    </div>
</body>
</html>"""


def send_email_to_self(subject: str, body: str):
    if not MY_EMAIL:
        raise ValueError("MY_EMAIL environment variable is not set. Please set it in your .env file.")
    send_email(subject, body, recipients=[MY_EMAIL])


if __name__ == "__main__":
    send_email_to_self("Test from Python", "Hello from my script.")