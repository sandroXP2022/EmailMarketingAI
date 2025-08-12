import csv
import smtplib
import requests
import json
import argparse
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables from .env
load_dotenv()

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Mistral AI API Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# Read emails from CSV
def read_emails_from_csv(filename="emails.csv"):
    emails = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    emails.append(row[0])  # Assumes the email is in the first column
        return emails
    except FileNotFoundError:
        print("Email file not found.")
        return []

# Generate email content using Mistral AI
def generate_email_content(context_file="context.txt", user_input=""):
    try:
        with open(context_file, "r", encoding="utf-8") as file:
            context = file.read()
    except FileNotFoundError:
        print("Context file not found.")
        return None

    prompt = f"Context: {context}\n\nUser request: {user_input}\n"

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": "You are an assistant that generates professional emails."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("Mistral API error:", response.text)
        return None

# Send email function
def send_email(to_email, subject, content):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(content, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())

        print(f"Email sent to {to_email}")

    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")

# Main function
def main():
    parser = argparse.ArgumentParser(description="AI-Powered Email Generator and Sender")
    parser.add_argument("--preview", action="store_true", help="Only generate email content and show it in the terminal, without sending")
    
    args = parser.parse_args()

    user_input = input("Describe the main content of the email: ")
    email_content = generate_email_content(user_input=user_input)

    if not email_content:
        print("Failed to generate email content.")
        return

    if args.preview:
        print("\n=== EMAIL PREVIEW ===\n")
        print(email_content)
        print("\n=== END OF PREVIEW ===\n")
        return

    emails = read_emails_from_csv()
    if not emails:
        print("No emails found.")
        return

    subject = input("Enter the subject of the email: ")

    for email in emails:
        send_email(email, subject, email_content)

if __name__ == "__main__":
    main()

