import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, request

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key == "":
  sys.stderr.write("""
    You haven't set up your API key yet.

    If you don't have an API key yet, visit:

    https://platform.openai.com/signup

    1. Make an account or sign in
    2. Click "View API Keys" from the top right menu.
    3. Click "Create new secret key"

    Then, open the Secrets Tool and add OPENAI_API_KEY as a secret.
    """)
  exit(1)

app = Flask(__name__)


def send_email(subject, message, from_addr, to_addr, smtp_server, smtp_port,
               username, password):
  # Create message container
  msg = MIMEMultipart()
  msg['From'] = from_addr
  msg['To'] = to_addr
  msg['Subject'] = subject

  # Attach the message to the container
  msg.attach(MIMEText(message, 'plain'))

  try:
    # Create server object with SSL option
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(username, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()
    print("Successfully sent email")
  except smtplib.SMTPException as e:
    print("Error: unable to send email")
    print(e)


@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    user_input = request.form['user_input']
    # Call OpenAI API with user input
    response = openai.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=[{
                                                  "role": "user",
                                                  "content": user_input
                                              }],
                                              temperature=0.3,
                                              max_tokens=150,
                                              top_p=0.3)
    # Send email with response
    send_email(subject="GPT-3 Response",
               message=response.choices[0].message.content,
               from_addr="lucas.hald@gmail.com",
               to_addr="lucas.hald@gmail.com",
               smtp_server="smtp.gmail.com",
               smtp_port=465,
               username="lucas.hald@gmail.com",
               password="jjhh mwbl hmmc hepl")
    return render_template('result.html',
                           user_input=user_input,
                           gpt_response=response.choices[0].message.content)
  if request.method == 'GET':
    return render_template('index.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
