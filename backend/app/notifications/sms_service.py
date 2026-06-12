from datetime import datetime
import random

from app.monitoring.logs import (
    app_logger,
    error_logger
)


class SMSService:

    # ==========================================
    # Generic SMS Sender
    # ==========================================
    def send_sms(
            self,
            phone_number: str,
            message: str
    ):

        try:

            sms_data = {
                "phone_number": phone_number,
                "message": message,
                "timestamp": datetime.utcnow()
            }

            app_logger.info(
                f"SMS sent: {sms_data}"
            )

            return {
                "success": True,
                "sms": sms_data
            }

        except Exception as e:

            error_logger.error(
                f"SMS sending failed: {str(e)}"
            )

            return {
                "success": False,
                "message": str(e)
            }

    # ==========================================
    # Generate OTP
    # ==========================================
    def generate_otp(self):

        return str(
            random.randint(
                100000,
                999999
            )
        )

    # ==========================================
    # OTP Verification SMS
    # ==========================================
    def send_otp(
            self,
            phone_number: str
    ):

        otp = self.generate_otp()

        message = (
            f"Your Xecommerce OTP is {otp}. "
            f"Do not share it with anyone."
        )

        self.send_sms(
            phone_number,
            message
        )

        return {
            "success": True,
            "otp": otp
        }

    # ==========================================
    # Password Reset OTP
    # ==========================================
    def password_reset_otp(
            self,
            phone_number
    ):

        otp = self.generate_otp()

        message = (
            f"Password reset OTP: {otp}"
        )

        self.send_sms(
            phone_number,
            message
        )

        return otp

    # ==========================================
    # Order Confirmation
    # ==========================================
    def order_confirmation(
            self,
            phone_number,
            order_id
    ):

        return self.send_sms(
            phone_number,
            f"Order #{order_id} placed successfully."
        )

    # ==========================================
    # Shipping Update
    # ==========================================
    def shipping_update(
            self,
            phone_number,
            order_id,
            status
    ):

        return self.send_sms(
            phone_number,
            f"Order #{order_id} status: {status}"
        )

    # ==========================================
    # Delivery Notification
    # ==========================================
    def delivery_notification(
            self,
            phone_number,
            order_id
    ):

        return self.send_sms(
            phone_number,
            f"Order #{order_id} delivered successfully."
        )

    # ==========================================
    # Price Drop Alert
    # ==========================================
    def price_drop_alert(
            self,
            phone_number,
            product_name,
            old_price,
            new_price
    ):

        return self.send_sms(
            phone_number,
            f"{product_name} dropped from ₹{old_price} to ₹{new_price}"
        )

    # ==========================================
    # Wishlist Alert
    # ==========================================
    def wishlist_alert(
            self,
            phone_number,
            product_name
    ):

        return self.send_sms(
            phone_number,
            f"{product_name} is back in stock."
        )

    # ==========================================
    # Promotional SMS
    # ==========================================
    def promotional_sms(
            self,
            phone_number,
            offer
    ):

        return self.send_sms(
            phone_number,
            offer
        )

    # ==========================================
    # Recommendation Alert
    # ==========================================
    def recommendation_sms(
            self,
            phone_number,
            product_name
    ):

        return self.send_sms(
            phone_number,
            f"Recommended for you: {product_name}"
        )

    # ==========================================
    # Deal Score Alert
    # ==========================================
    def deal_score_alert(
            self,
            phone_number,
            product_name,
            score
    ):

        return self.send_sms(
            phone_number,
            f"{product_name} has an AI Deal Score of {score}/100"
        )

    # ==========================================
    # Admin Alert
    # ==========================================
    def admin_alert(
            self,
            phone_number,
            message
    ):

        return self.send_sms(
            phone_number,
            message
        )

    # ==========================================
    # Drift Detection Alert
    # ==========================================
    def drift_alert(
            self,
            phone_number,
            model_name
    ):

        return self.send_sms(
            phone_number,
            f"Drift detected in {model_name}. Retraining required."
        )

    # ==========================================
    # Health Check
    # ==========================================
    def health(self):

        return {
            "status": "healthy",
            "service": "sms_service"
        }