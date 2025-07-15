from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, validator
from app.services.email_service import email_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["contact"])

class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str = ""
    category: str = ""
    message: str
    urgency: str = "medium"
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters long')
        return v.strip()

class ContactFormResponse(BaseModel):
    success: bool
    message: str

async def send_contact_email(form_data: ContactFormRequest):
    """Send contact form email in background"""
    try:
        # Create email content
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .content {{ padding: 20px; }}
                    .field {{ margin-bottom: 15px; }}
                    .label {{ font-weight: bold; color: #555; }}
                    .value {{ margin-left: 10px; }}
                    .urgent {{ color: #dc3545; font-weight: bold; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>New Contact Form Submission</h2>
                    <p>A new message has been received through the PDF Table Extractor contact form.</p>
                </div>
                
                <div class="content">
                    <div class="field">
                        <span class="label">From:</span>
                        <span class="value">{form_data.name} ({form_data.email})</span>
                    </div>
                    
                    <div class="field">
                        <span class="label">Subject:</span>
                        <span class="value">{form_data.subject or 'No subject provided'}</span>
                    </div>
                    
                    <div class="field">
                        <span class="label">Category:</span>
                        <span class="value">{form_data.category.title() if form_data.category else 'General'}</span>
                    </div>
                    
                    <div class="field">
                        <span class="label">Urgency:</span>
                        <span class="value{' urgent' if form_data.urgency in ['high', 'critical'] else ''}">{form_data.urgency.title()}</span>
                    </div>
                    
                    <div class="field">
                        <span class="label">Message:</span>
                        <div style="margin-top: 10px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
                            {form_data.message.replace(chr(10), '<br>')}
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>This message was sent through the PDF Table Extractor contact form.</p>
                    <p>Reply to this email to respond directly to the sender.</p>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        plain_content = f"""
        New Contact Form Submission
        
        From: {form_data.name} ({form_data.email})
        Subject: {form_data.subject or 'No subject provided'}
        Category: {form_data.category.title() if form_data.category else 'General'}
        Urgency: {form_data.urgency.title()}
        
        Message:
        {form_data.message}
        
        ---
        This message was sent through the PDF Table Extractor contact form.
        Reply to this email to respond directly to the sender.
        """
        
        # Send to support email
        success = await email_service.send_email(
            to_email=settings.FROM_EMAIL,  # Send to our support email
            to_name="PDF Extractor Support",
            subject=f"[Contact Form] {form_data.urgency.upper()} - {form_data.subject or 'New Message'}",
            html_content=html_content,
            plain_content=plain_content
        )
        
        if success:
            # Send confirmation to user
            user_confirmation = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .header {{ background-color: #28a745; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                        .content {{ padding: 20px; }}
                        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>Thank You for Contacting Us!</h2>
                    </div>
                    
                    <div class="content">
                        <p>Hi {form_data.name},</p>
                        
                        <p>Thank you for reaching out to PDF Table Extractor support. We've received your message and will respond as soon as possible.</p>
                        
                        <p><strong>Your message:</strong></p>
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            {form_data.message.replace(chr(10), '<br>')}
                        </div>
                        
                        <p>Based on your urgency level ({form_data.urgency}), you can expect a response within:</p>
                        <ul>
                            <li><strong>Low:</strong> 2-3 business days</li>
                            <li><strong>Medium:</strong> 12-24 hours</li>
                            <li><strong>High:</strong> 4-6 hours</li>
                            <li><strong>Critical:</strong> 1-2 hours</li>
                        </ul>
                        
                        <p>If you have any additional questions, feel free to reply to this email.</p>
                        
                        <p>Best regards,<br>PDF Table Extractor Support Team</p>
                    </div>
                    
                    <div class="footer">
                        <p>PDF Table Extractor - AI-Powered Table Extraction</p>
                    </div>
                </body>
            </html>
            """
            
            await email_service.send_email(
                to_email=form_data.email,
                to_name=form_data.name,
                subject="Thank you for contacting PDF Table Extractor",
                html_content=user_confirmation,
                plain_content=f"Hi {form_data.name},\n\nThank you for contacting us. We've received your message and will respond soon.\n\nBest regards,\nPDF Table Extractor Support"
            )
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending contact email: {str(e)}")
        return False

@router.post("/submit", response_model=ContactFormResponse)
async def submit_contact_form(
    form_data: ContactFormRequest,
    background_tasks: BackgroundTasks
) -> ContactFormResponse:
    """Submit contact form and send email"""
    
    try:
        # Add email sending to background tasks
        background_tasks.add_task(send_contact_email, form_data)
        
        return ContactFormResponse(
            success=True,
            message="Thank you for your message! We'll get back to you soon."
        )
        
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to submit contact form. Please try again."
        )