"""
Email service for password reset and user notifications
"""
import smtplib
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from typing import List, Optional
import os
from flask import current_app, render_template_string

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@optura.nl')
        self.from_name = os.getenv('FROM_NAME', 'Landscape Architecture Tool')
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None, attachments: List = None):
        """Send email with HTML and optional text body"""
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text part if provided
            if text_body:
                text_part = MimeText(text_body, 'plain')
                msg.attach(text_part)
            
            # Add HTML part
            html_part = MimeText(html_body, 'html')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            if self.smtp_username and self.smtp_password:
                # Use SMTP authentication
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                server.quit()
            else:
                # Use local SMTP without authentication
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.send_message(msg)
                server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _add_attachment(self, msg, attachment_path: str):
        """Add attachment to email"""
        try:
            with open(attachment_path, "rb") as attachment:
                part = MimeBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(attachment_path)}'
            )
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Failed to add attachment {attachment_path}: {str(e)}")
    
    def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str):
        """Send password reset email"""
        reset_url = f"{current_app.config.get('FRONTEND_URL', 'https://optura.nl')}/reset-password?token={reset_token}"
        
        subject = "Password Reset Request - Landscape Architecture Tool"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9fafb; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #2563eb; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 6px; 
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                .warning {{ background-color: #fef3c7; padding: 15px; border-radius: 6px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>We received a request to reset your password for your Landscape Architecture Tool account.</p>
                    <p>Click the button below to reset your password:</p>
                    <a href="{reset_url}" class="button">Reset Password</a>
                    <p>Or copy and paste this link into your browser:</p>
                    <p><a href="{reset_url}">{reset_url}</a></p>
                    <div class="warning">
                        <strong>Important:</strong>
                        <ul>
                            <li>This link will expire in 24 hours</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>For security, never share this link with anyone</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>This email was sent from the Landscape Architecture Tool system.</p>
                    <p>If you have any questions, please contact your system administrator.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request - Landscape Architecture Tool
        
        Hello {user_name},
        
        We received a request to reset your password for your Landscape Architecture Tool account.
        
        Please visit the following link to reset your password:
        {reset_url}
        
        Important:
        - This link will expire in 24 hours
        - If you didn't request this reset, please ignore this email
        - For security, never share this link with anyone
        
        If you have any questions, please contact your system administrator.
        """
        
        return self.send_email(user_email, subject, html_body, text_body)
    
    def send_welcome_email(self, user_email: str, user_name: str, username: str, temporary_password: str = None):
        """Send welcome email to new user"""
        login_url = f"{current_app.config.get('FRONTEND_URL', 'https://optura.nl')}/login"
        
        subject = "Welcome to Landscape Architecture Tool"
        
        password_info = ""
        if temporary_password:
            password_info = f"""
            <div class="warning">
                <strong>Temporary Password:</strong> {temporary_password}
                <br>
                <em>Please change this password after your first login for security.</em>
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #059669; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9fafb; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #059669; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 6px; 
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                .warning {{ background-color: #fef3c7; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                .info {{ background-color: #dbeafe; padding: 15px; border-radius: 6px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Landscape Architecture Tool</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Your account has been created successfully! You can now access the Landscape Architecture Tool.</p>
                    
                    <div class="info">
                        <strong>Your Login Details:</strong><br>
                        Username: {username}<br>
                        Email: {user_email}
                    </div>
                    
                    {password_info}
                    
                    <p>Click the button below to access the application:</p>
                    <a href="{login_url}" class="button">Login to Application</a>
                    
                    <p><strong>Features you can access:</strong></p>
                    <ul>
                        <li>Project management and tracking</li>
                        <li>Plant database and recommendations</li>
                        <li>Client and supplier management</li>
                        <li>Reporting and analytics</li>
                        <li>Invoice and quote generation</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>If you have any questions, please contact your system administrator.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to Landscape Architecture Tool
        
        Hello {user_name},
        
        Your account has been created successfully! You can now access the Landscape Architecture Tool.
        
        Your Login Details:
        Username: {username}
        Email: {user_email}
        {"Temporary Password: " + temporary_password if temporary_password else ""}
        
        Please visit: {login_url}
        
        {"Please change your temporary password after first login for security." if temporary_password else ""}
        
        If you have any questions, please contact your system administrator.
        """
        
        return self.send_email(user_email, subject, html_body, text_body)
    
    def send_bulk_import_report(self, admin_email: str, admin_name: str, created_users: List[str], errors: List[str]):
        """Send bulk import report to admin"""
        subject = f"Bulk User Import Report - {len(created_users)} users created"
        
        error_section = ""
        if errors:
            error_list = "<br>".join([f"• {error}" for error in errors])
            error_section = f"""
            <div class="warning">
                <h3>Errors ({len(errors)}):</h3>
                {error_list}
            </div>
            """
        
        success_section = ""
        if created_users:
            user_list = "<br>".join([f"• {user}" for user in created_users])
            success_section = f"""
            <div class="info">
                <h3>Successfully Created Users ({len(created_users)}):</h3>
                {user_list}
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bulk Import Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #7c3aed; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9fafb; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                .warning {{ background-color: #fef3c7; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                .info {{ background-color: #dbeafe; padding: 15px; border-radius: 6px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Bulk User Import Report</h1>
                </div>
                <div class="content">
                    <h2>Hello {admin_name},</h2>
                    <p>Your bulk user import has been completed.</p>
                    
                    <h3>Summary:</h3>
                    <ul>
                        <li><strong>Total Users Created:</strong> {len(created_users)}</li>
                        <li><strong>Total Errors:</strong> {len(errors)}</li>
                    </ul>
                    
                    {success_section}
                    {error_section}
                </div>
                <div class="footer">
                    <p>This report was generated automatically by the Landscape Architecture Tool.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(admin_email, subject, html_body)

# Global email service instance
email_service = EmailService()
