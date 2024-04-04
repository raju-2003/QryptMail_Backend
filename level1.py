import imaplib
import email
from email.header import decode_header
import os
from keyvault import Keygen
from aes import aes_decrypt
import base64
# Gmail IMAP settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

class Level:
# Connect to the server
    def __init__(self):
        self.mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)


# Search for all emails in the selected mailbox
    def get_emails(self,EMAIL_ADDRESS,PASSWORD,count=10):

# Log in to your account
        self.mail.login(EMAIL_ADDRESS, PASSWORD)

# Select the mailbox you want to access (e.g., 'inbox')
        self.mail.select(readonly=True)
        status, messages = self.mail.search(None, 'ALL')

        # Get the list of email IDs
        email_ids = messages[0].split()

        # Loop through the email IDs and fetch the corresponding emails
        email_data=[]


        for email_id in email_ids[::-1][:10]:
            # Fetch the email by ID
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')
            
            m={}
            # Parse the email content
            msg = email.message_from_bytes(msg_data[0][1])

            # Extract information (e.g., subject and sender)
            subject, encoding = decode_header(msg.get('Subject'))[0]
            
            # Decode the subject and sender
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8')
            m['subject']=subject

            sender, encoding = decode_header(msg.get('From'))[0]
            if isinstance(sender, bytes):
                sender = sender.decode(encoding or 'utf-8')
            m['sender']=sender

            date, encoding = decode_header(msg.get('Date'))[0]
            if isinstance(date, bytes):
                date = date.decode(encoding or 'utf-8')
            m['date']=date

            #get body only if text/plain
            body=""
            if msg.is_multipart():
                for part in msg.walk():
                    # print(part.get_content_type())
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        # print(body)
                        break

            else:
                body = msg.get_payload(decode=True).decode()
            m['body']=body

            # print(msg.keys())

            if msg.get('Api-Key'):
                api_id, encoding = decode_header(msg.get('Api-Key'))[0]
                if isinstance(api_id, bytes):
                    api_id = api_id.decode(encoding or 'utf-8')
                m['api-key']="null"
                print(m)
                vault=Keygen()
                vault.connect_vault()
                secret=vault.get_secret(api_id).value
                print(secret)
                secret=secret[9:]
                body_bytes = base64.b64decode(
                    m['body']
                    .encode('utf-8'))
                # decrypted_body=aes_decrypt(secret,body_bytes)
                m['body']=body_bytes
                subject_bytes = base64.b64decode(
                    m['subject']
                    .encode('utf-8'))
                # decrypted_subject=aes_decrypt(secret,subject_bytes)
                m['subject']=subject_bytes
                # ADD DECREPTION
            
            else:
                continue

                # vault.delete_secret(api_id)

            #get mail id
            id, encoding = decode_header(msg.get('Message-ID'))[0]
            if isinstance(id, bytes):
                id = id.decode(encoding or 'utf-8')
            m['id']=id

            # m['body']
            print(m)

            email_data.append(m)
            
        print("Subject: ",email_data)
        return email_data
        
# if __name__=="__main__":
#     from dotenv import load_dotenv
#     load_dotenv()
#     i=imap()