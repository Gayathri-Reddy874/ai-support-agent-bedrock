import uuid
from datetime import datetime

# ------------------ TICKET ------------------
def create_ticket(user_query):
    ticket_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        f"✅ Ticket Created Successfully!\n\n"
        f"🆔 Ticket ID: {ticket_id}\n"
        f"🕒 Time: {timestamp}\n"
        f"📝 Issue: {user_query}\n\n"
        f"Our support team will contact you shortly."
    )


# ------------------ FAQ ------------------
def get_faq_answer(query):
    query = query.lower()

    faq = {
        "refund": "Refunds are processed within 5–7 business days.",
        "delivery": "Delivery usually takes 3–5 business days.",
        "track": "You can track your order using the tracking link sent to your email.",
        "order status": "Check your email or account dashboard for order status updates."
    }

    for key, answer in faq.items():
        if key in query:
            return f"📌 {answer}"

    return None


# ------------------ EMAIL ------------------
def send_email(query):
    return (
        "📧 Your request has been emailed to our support team.\n"
        "They will get back to you within 24 hours."
    )


# ------------------ INTENT DETECTION ------------------
def detect_intent(query):
    query = query.lower()

    complaint_keywords = [
        "not delivered", "damaged", "failed", "issue",
        "complaint", "delayed", "problem", "broken"
    ]

    email_keywords = [
        "email", "send email", "contact support", "mail"
    ]

    for word in email_keywords:
        if word in query:
            return "EMAIL"

    for word in complaint_keywords:
        if word in query:
            return "TICKET"

    return "GENERAL"


