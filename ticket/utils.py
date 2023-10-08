import requests
from core.utils import send_notification
from .models import Notification  # Import the Notification model if not already imported
from django.core.mail import send_mail
import paystackapi
from .models import *


def is_ticket_available(event, ticket_type):
    # Get all tickets associated with the event and matching the requested ticket type
    matching_tickets = event.tickets.filter(category=ticket_type, is_sold=False)

    # Check if there are any available tickets
    if matching_tickets.exists():
        return True  # There are available tickets for the requested type
    else:
        return False  # No available tickets for the requested type



def validate_payment(payment_info):
    # Define the URL of your payment gateway's API
    payment_gateway_url = 'YOUR_PAYMENT_GATEWAY_API_URL'

    try:
        # Send a POST request to the payment gateway's API with the payment_info
        response = requests.post(payment_gateway_url, json=payment_info)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Assuming the payment gateway's API returns a JSON response
            response_data = response.json()

            # Check if the payment status in the response indicates success
            if response_data.get('status') == 'success':
                return True  # Payment was successful
            else:
                return False  # Payment failed
        else:
            return False  # Request to payment gateway failed
    except requests.exceptions.RequestException:
        return False  # Exception occurred during the request

    return False  # Default to payment failure if an error occurs


def payment_successful(payment_info):
    # Check if the 'status' field exists in the payment_info dictionary
    if 'status' in payment_info:
        # Check if the value of the 'status' field indicates a successful payment
        if payment_info['status'] == 'success':
            return True  # Payment was successful
        else:
            return False  # Payment was not successful
    else:
        return False  # 'status' field not found in payment_info




def send_event_owner_notification(event_owner, purchaser, event_title, ticket_type):
    # Create a notification message to send to the event owner
    message = f"{purchaser.username} has purchased a {ticket_type} ticket for your event: {event_title}"

    # Create a new notification with the event owner as the recipient
    notification = Notification(
        recipient=event_owner,
        sender=purchaser,
        message=message,
        notification_type='Purchase',  # You can specify a notification type if needed
    )
    notification.save()

    # You can also implement the logic to send a push notification or email to the event owner if needed.
     # Send an email to the event owner
    subject = f"Ticket Purchase Notification for Event: {event_title}"
    message = f"{purchaser.username} has purchased a {ticket_type} ticket for your event: {event_title}"
    from_email = "your@email.com"  # Use your email address
    recipient_list = [event_owner.email]  # Event owner's email address

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)


def refund_ticket_purchase(purchase):
    # Check if the payment_status is 'Successful' before attempting a refund
    if purchase.payment_status == 'Successful':
        # Calculate the refund amount based on the ticket price (modify this as needed)
        refund_amount = purchase.ticket.price * 100  # Amount in kobo (100 kobo = 1 Naira)

        # Replace 'YOUR_PAYSTACK_SECRET_KEY' with your actual Paystack secret key
        paystackapi.secret_key = 'YOUR_PAYSTACK_SECRET_KEY'

        # Create a refund request
        refund_request = paystackapi.Refund.create(
            transaction=purchase.payment_details.transaction_reference,
            amount=refund_amount
        )

        if refund_request.status:
            # The refund request was successful
            # Update the purchase record to mark it as refunded
            purchase.payment_status = 'Refunded'
            purchase.save()

            # Send a notification to the user about the refund
            send_notification(
                purchase.user,
                f"Ticket purchase for event '{purchase.event.title}' has been refunded successfully."
            )
        else:
            # Handle refund failure
            # Update the purchase record to mark it as 'Refund Failed'
            purchase.payment_status = 'Refund Failed'
            purchase.save()

            # Send a notification to the user about the refund failure
            send_notification(
                purchase.user,
                f"Ticket purchase for event '{purchase.event.title}' refund has failed. Please contact support."
            )
    else:
        # The payment_status is not 'Successful', so no refund is possible
        pass



def generate_withdrawal_history(user, amount, status='Successful'):
    # Create a WithdrawalHistory record
    withdrawal_history = WithdrawalHistory(user=user, amount=amount, status=status)
    withdrawal_history.save()
    
    # Send a notification to the user about the withdrawal request status
    if status == 'Successful':
        message = f"Your withdrawal request for NGN {amount} was successful."
    else:
        message = f"Your withdrawal request for NGN {amount} failed."

    send_notification(user, message)


import requests
from django.conf import settings

def perform_withdrawal(withdrawal_request):
    # Check if the user has a valid payout method (e.g., bank account info)
    if not has_valid_payout_method(withdrawal_request.user):
        withdrawal_request.status = 'Failed'
        withdrawal_request.save()
        return False  # Withdrawal failed due to invalid payout method

    # Calculate the withdrawal amount and perform the withdrawal
    withdrawal_amount = withdrawal_request.amount

    # Make an API request to Paystack to initiate the withdrawal
    paystack_api_url = 'https://api.paystack.co/transfer/create'
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'source': 'balance',  # Withdraw from Paystack balance
        'amount': withdrawal_amount * 100,  # Amount in kobo (multiply by 100)
        'recipient': withdrawal_request.user.paystack_recipient_code,  # User's Paystack recipient code
        'reason': 'Withdrawal request',
    }

    response = requests.post(paystack_api_url, json=payload, headers=headers)

    if response.status_code == 200:
        # Withdrawal initiated successfully, update the request status
        withdrawal_request.status = 'Successful'
        withdrawal_request.save()
        return True
    else:
        # Withdrawal request failed
        withdrawal_request.status = 'Failed'
        withdrawal_request.save()
        return False  # Withdrawal failed

def has_valid_payout_method(user):
    # Implement logic to check if the user has a valid payout method
    # This could involve checking if the user has a Paystack recipient code or bank account info
    return hasattr(user, 'paystack_recipient_code')  # Check if user has a Paystack recipient code
