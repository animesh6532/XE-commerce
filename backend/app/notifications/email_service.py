import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

from app.monitoring.logs import app_logger, error_logger

load_dotenv()


class EmailService:

    def __init__(self):

        self.smtp_server = os.getenv(
            "SMTP_SERVER",
            "smtp.gmail.com"
        )

        self.smtp_port = int(
            os.getenv(
                "SMTP_PORT",
                587
            )
        )

        self.sender_email = os.getenv(
            "EMAIL_ADDRESS"
        )

        self.sender_password = os.getenv(
            "EMAIL_PASSWORD"
        )

    # =====================================================
    # Generic Email Sender
    # =====================================================

    def send_email(
            self,
            recipient_email: str,
            subject: str,
            body: str
    ):

        try:

            message = MIMEMultipart()

            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject

            message.attach(
                MIMEText(
                    body,
                    "plain"
                )
            )

            with smtplib.SMTP(
                    self.smtp_server,
                    self.smtp_port
            ) as server:

                server.starttls()

                server.login(
                    self.sender_email,
                    self.sender_password
                )

                server.sendmail(
                    self.sender_email,
                    recipient_email,
                    message.as_string()
                )

            app_logger.info(
                f"Email sent to {recipient_email}"
            )

            return {
                "success": True,
                "message": "Email sent successfully"
            }

        except Exception as e:

            error_logger.error(
                f"Email sending failed: {str(e)}"
            )

            return {
                "success": False,
                "message": str(e)
            }

    # =====================================================
    # Welcome Email
    # =====================================================

    def send_welcome_email(
            self,
            email,
            username
    ):

        subject = "Welcome to Xecommerce"

        body = f"""
Hello {username},

Welcome to Xecommerce!

Thank you for creating an account.

Enjoy AI-powered shopping with:
✔ Personalized recommendations
✔ AI Deal Score
✔ Smart Wishlist
✔ Price Drop Alerts

Happy Shopping!

Team Xecommerce
"""

        return self.send_email(
            email,
            subject,
            body
        )

    # =====================================================
    # Order Confirmation
    # =====================================================

    def send_order_confirmation(
            self,
            email,
            order_id,
            amount
    ):

        subject = "Order Confirmation"

        body = f"""
Your order has been placed successfully.

Order ID: {order_id}

Total Amount: ₹{amount}

Thank you for shopping with Xecommerce.
"""

        return self.send_email(
            email,
            subject,
            body
        )

    # =====================================================
    # Shipping Update
    # =====================================================

    def send_shipping_update(
            self,
            email,
            order_id,
            status
    ):

        subject = "Shipping Update"

        body = f"""
Order ID: {order_id}

Current Status:
{status}

Track your order on Xecommerce.
"""

        return self.send_email(
            email,
            subject,
            body
        )

    # =====================================================
    # Delivery Notification
    # =====================================================

    def send_delivery_notification(
            self,
            email,
            order_id
    ):

        subject = "Order Delivered"

        body = f"""
Order {order_id} has been delivered successfully.

Thank you for shopping with Xecommerce.
"""

        return self.send_email(
            email,
            subject,
            body
        )

    # =====================================================
    # Password Reset
    # =====================================================

    def send_password_reset(
            self,
            email,
            reset_link
    ):

        subject = "Password Reset"

        body = f"""
Click the link below to reset your password:

{reset_link}

If you didn't request this, ignore this email.
"""

        return self.send_email(
            email,
            subject,
            body
        )

    # =====================================================
    # Price Drop Alert
    # =====================================================

    def send_price_drop_alert(
            self,
            email,
            product_name,
            old_price,
            new_price
    ):

        subject = "Price Drop Alert"

        body = f"""
Great news!

{product_name}

Old Price: ₹{old_price}

New Price: ₹{new_price}

Grab the deal before it ends!
"""

        return self.send_email(
            email,
            subject,
            body
        )

    # =====================================================
    # AI Recommendation Email
    # =====================================================

    def send_recommendation_email(
            self,
            email,
            recommendations
    ):

        subject = "Recommended Products For You"

        body = "Products selected by our AI engine:\n\n"

        for item in recommendations:

            body += (
                f"- {item}\n"
            )

        return self.send_email(
            email,
            subject,
            body
        )

    # =====================================================
    # Admin Alert
    # =====================================================

    def send_admin_alert(
            self,
            message
    ):

        admin_email = os.getenv(
            "ADMIN_EMAIL"
        )

        return self.send_email(
            admin_email,
            "Xecommerce Admin Alert",
            message
        )