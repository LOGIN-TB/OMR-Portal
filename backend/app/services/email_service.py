import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.config import AppConfig, ServerConfig

logger = logging.getLogger(__name__)

templates_dir = Path(__file__).parent.parent / "templates" / "emails"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))


def _get_smtp_server(config: AppConfig) -> ServerConfig | None:
    if not config.portal_smtp:
        return None
    for s in config.relay_servers:
        if s.id == config.portal_smtp.smtp_server_id:
            return s
    return None


async def _send_email(config: AppConfig, to_email: str, subject: str, html_body: str):
    smtp_config = config.portal_smtp
    if not smtp_config:
        logger.error("SMTP not configured")
        return

    smtp_server = _get_smtp_server(config)
    if not smtp_server:
        logger.error(f"SMTP server {smtp_config.smtp_server_id} not found")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{smtp_config.smtp_sender_name} <{smtp_config.smtp_sender}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_server.name,
            port=587,
            start_tls=True,
            username=smtp_config.smtp_username,
            password=smtp_config.smtp_password,
        )
        logger.info(f"E-Mail gesendet an {to_email}")
    except Exception as e:
        logger.error(f"E-Mail-Versand fehlgeschlagen an {to_email}: {e}")


async def send_magic_link(config: AppConfig, email: str, token: str, language: str):
    link = f"{config.base_url}/auth/verify?token={token}"
    template_name = f"magic_link_{language}.html"
    try:
        template = jinja_env.get_template(template_name)
    except Exception:
        template = jinja_env.get_template("magic_link_de.html")

    html = template.render(link=link, email=email)
    subject = "Ihr Login bei spamgo" if language == "de" else "Your spamgo login"
    await _send_email(config, email, subject, html)


async def send_warning(config: AppConfig, email: str, warning_type: str, details: dict, language: str):
    template_name = f"warning_{warning_type}_{language}.html"
    try:
        template = jinja_env.get_template(template_name)
    except Exception:
        logger.error(f"Template {template_name} nicht gefunden")
        return

    html = template.render(**details)

    subjects = {
        "quota_warning": {"de": "spamgo: Quota-Warnung", "en": "spamgo: Quota Warning"},
        "quota_critical": {"de": "spamgo: Quota kritisch", "en": "spamgo: Quota Critical"},
        "dns_problem": {"de": "spamgo: DNS-Problem erkannt", "en": "spamgo: DNS Problem Detected"},
        "rbl_listing": {"de": "spamgo: RBL-Listing erkannt", "en": "spamgo: RBL Listing Detected"},
        "high_bounce": {"de": "spamgo: Hohe Bounce-Rate", "en": "spamgo: High Bounce Rate"},
    }
    subject = subjects.get(warning_type, {}).get(language, f"spamgo: {warning_type}")
    await _send_email(config, email, subject, html)
