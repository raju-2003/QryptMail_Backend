from fastapi import FastAPI, File, UploadFile
from email.message import EmailMessage
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aes import aes_encrypt, aes_decrypt
import os
import base64
import smtplib
from dotenv import load_dotenv
from keyvault import Keygen
from imap_dec import imap
from pydantic import EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)



class Creds(BaseModel):
    mail : EmailStr
    pwd : str



@app.post("/get-creds")
def getCreds(creds : Creds):
    global email
    email = creds.mail
    global pwd
    pwd = creds.pwd





class SendEMail(BaseModel):
    receiver: str
    subject: str
    body: str
    security : str
    
    
    
    

@app.post("/sendmail")
def sendmail(sendemail : SendEMail):
    msg = EmailMessage()
    
    # key = Keygen()
    
    # key.connect_vault()
    
    # key_name = key.get_fresh_key()
    
    # key_value=key.get_secret(key_name.name).value
    
    # key.disable_secret(key_name.name)
    
    msg["From"] = email
    msg["To"] = sendemail.receiver
    
    
    if sendemail.security == 'level1':
        

        # Create a MIME message object
        message = MIMEMultipart()
        message["From"] = email
        message["To"] = sendemail.receiver
        message["Subject"] = sendemail.subject
        message["Api-key"] = "Null"
        message['security-method']="level1"

        # Attach the body of the email as plain text
        message.attach(MIMEText(sendemail.body, "plain"))

        # Connect to the SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email, pwd)

            # Send the email
            server.sendmail(email, sendemail.receiver, message.as_string())

    if sendemail.security == "level2":
        key = Keygen()
    
        key.connect_vault()
    
        key_name = key.get_fresh_key()
    
        key_value=key.get_secret(key_name.name).value
    
        key.disable_secret(key_name.name)
        subject_bytes = aes_encrypt(key_value, sendemail.subject)
        body_bytes = aes_encrypt(key_value, sendemail.body)
        
        subject_encoded = base64.b64encode(subject_bytes).decode('utf-8')
        body_encoded = base64.b64encode(body_bytes).decode('utf-8')
        
        msg["Subject"] = subject_encoded
        msg["Commrad-enc"] = "True"
        msg["Api-key"] = key_name.name
        msg['security-method']="level2"
        msg.set_content(body_encoded)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email, pwd)
            smtp.send_message(msg)

        return {"message": "email sent"}

    
    if sendemail.security == "level3":
        key = Keygen()
    
        key.connect_vault()
    
        key_names = key.get_keys(len(sendemail.body))
        key_value=""
        for i in key_names:

            key_value+=key.get_secret(i.name).value
    
            key.disable_secret(i.name)
            
        print(key_value)
        #append the difference in length with keys and body with subjectdo xor operation with the keys
        # subject=sendemail.subject+"-"*(len(key_value)-len(sendemail.subject))
        body=sendemail.body+"-"*(len(key_value)-len(sendemail.body))
        
        #xor operation
        # subject_bytes = bytes([a ^ b for a, b in zip(subject.encode(), key_value.encode())])
        body_bytes = bytes([a ^ b for a, b in zip(body.encode(), key_value.encode())])  
        body_encoded = base64.b64encode(body_bytes).decode('utf-8')
        subject_encoded = base64.b64encode(sendemail.subject.encode()).decode('utf-8')
        msg["Subject"] = subject_encoded
        msg["Commrad-enc"] = "True"
        msg["Api-key"] = ';'.join([i.name for i in key_names])
        msg['security-method']="level3"
        msg.set_content(body_encoded)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email, pwd)
            smtp.send_message(msg)

        return {"message": "email sent"}



@app.get("/getinbox")
def getinbox():
    i = imap()
    messages=i.get_emails(email, pwd)


    formatted_emails = []


    for msg in messages:
        formatted_email = {
            "id": msg.get("id", ""),
            "from": msg.get("sender", ""),
            "thumbnail": "",  # Add the appropriate value or leave it empty
            "subject": msg.get("subject", ""),
            "time": msg.get("date", ""),
            "To": "",  # Add the appropriate value or leave it empty
            "emailExcerpt": msg.get("body", "")[:100],  # Adjust the excerpt length as needed
            "emailContent": msg.get("body", ""),
            "unread": True,  
            "checked": False,  
            "starred": False, 
            "important": False,  
            "inbox": False, 
            "sent": False,  
            "draft": False, 
            "spam": False,  
            "trash": False,  
            "label": "Health", 
        }
        formatted_emails.append(formatted_email)

    return formatted_emails