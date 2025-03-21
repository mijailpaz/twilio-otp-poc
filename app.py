import streamlit as st
from twilio.rest import Client
import time

# --- Twilio configuration from Streamlit secrets ---
try:
    TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_VERIFY_SERVICE_SID = st.secrets["TWILIO_VERIFY_SERVICE_SID"]
except Exception as e:
    st.error(f"Error loading Twilio secrets: {e}")
    st.info("Please configure Twilio credentials in .streamlit/secrets.toml")

# Initialize Twilio client if credentials are available
client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# --- Functions to handle Twilio Verify calls ---
def start_verification(phone_number: str) -> bool:
    """Initiate OTP verification by sending an OTP to the provided phone number."""
    if not client:
        st.error("Twilio client not configured. Please check your secrets configuration.")
        return False
    
    try:
        verification = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
            .verifications \
            .create(to=phone_number, channel='sms')
        return verification.status == "pending"
    except Exception as e:
        st.error(f"Error sending OTP: {e}")
        return False

def check_verification(phone_number: str, otp_code: str) -> bool:
    """Check the OTP code entered by the user."""
    if not client:
        st.error("Twilio client not configured. Please check your secrets configuration.")
        return False
    
    try:
        verification_check = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
            .verification_checks \
            .create(to=phone_number, code=otp_code)
        return verification_check.status == "approved"
    except Exception as e:
        st.error(f"Error verifying OTP: {e}")
        return False

# Initialize session state variables
if "form_filled" not in st.session_state:
    st.session_state.form_filled = False
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "verified" not in st.session_state:
    st.session_state.verified = False
if "submit_clicked" not in st.session_state:
    st.session_state.submit_clicked = False
if "verify_clicked" not in st.session_state:
    st.session_state.verify_clicked = False
if "reset_clicked" not in st.session_state:
    st.session_state.reset_clicked = False

# Callback functions for button clicks
def on_form_submit():
    st.session_state.submit_clicked = True

def on_send_otp():
    st.session_state.send_otp_clicked = True

def on_verify_code():
    st.session_state.verify_clicked = True

def on_reset():
    st.session_state.reset_clicked = True
    for key in ['form_filled', 'form_data', 'otp_sent', 'verified', 'submit_clicked', 'verify_clicked', 'reset_clicked', 'send_otp_clicked']:
        if key in st.session_state:
            st.session_state[key] = False
    if 'form_data' in st.session_state:
        st.session_state.form_data = {}

# --- Streamlit App ---
st.title("Twilio Verify OTP Integration POC for Sympla")

# Add POC explanation
st.markdown("""
### Project Overview
In this proof-of-concept, we explore the integration of Twilio Verify to enhance security within the Sympla event registration platform. 
With the increasing need for robust data protection during ticket purchases and user sign-ups, this solution introduces a seamless OTP verification step to authenticate users before they proceed with sensitive transactions. 
By embedding this additional layer of security into the registration flow, Sympla can further safeguard sensitive information, reduce fraud risk, and bolster user confidence, ultimately creating a more secure and reliable experience for event organizers and attendees alike.
""")

# Process form submission
if st.session_state.submit_clicked and not st.session_state.form_filled:
    if all(field in st.session_state for field in ['bank_account', 'account_holder', 'amount', 'phone_number']):
        if (st.session_state.bank_account and st.session_state.account_holder and 
            st.session_state.amount > 0 and st.session_state.phone_number):
            
            st.session_state.form_filled = True
            st.session_state.form_data = {
                "bank_account": st.session_state.bank_account,
                "account_holder": st.session_state.account_holder,
                "amount": st.session_state.amount,
                "phone_number": st.session_state.phone_number
            }
            st.session_state.submit_clicked = False
            st.rerun()

# Process OTP verification
if st.session_state.verify_clicked and not st.session_state.verified and st.session_state.otp_sent:
    if 'otp_code' in st.session_state and st.session_state.otp_code:
        verified = check_verification(st.session_state.form_data['phone_number'], st.session_state.otp_code)
        if verified:
            st.session_state.verified = True
            st.session_state.verify_clicked = False
            st.rerun()

# Process OTP sending
if 'send_otp_clicked' in st.session_state and st.session_state.send_otp_clicked and not st.session_state.otp_sent:
    sent = start_verification(st.session_state.form_data['phone_number'])
    if sent:
        st.session_state.otp_sent = True
        st.session_state.send_otp_clicked = False
        st.rerun()

# Process reset button
if st.session_state.reset_clicked:
    st.rerun()

# Step 1: Show the sensitive form first
if not st.session_state.form_filled:
    st.header("Step 1: Enter Sensitive Information")
    st.write("Please fill out the following information for your transaction:")
    
    with st.form(key="sensitive_form"):
        st.text_input("Bank Account Number:", key="bank_account")
        st.text_input("Account Holder Name:", key="account_holder")
        st.number_input("Amount (BRL):", min_value=0.0, step=0.01, key="amount")
        st.text_input("Your Phone Number (with country code for verification):", value="+55", key="phone_number")
        st.form_submit_button("Proceed to Verification", on_click=on_form_submit)
    
    if st.session_state.submit_clicked:
        if not all(field in st.session_state and st.session_state[field] for field in ['bank_account', 'account_holder', 'phone_number']) or not (st.session_state.amount > 0):
            st.error("Please fill in all fields with valid information.")

# Step 2: Verify the user with OTP
elif not st.session_state.verified:
    st.header("Step 2: Verify Your Identity")
    st.write("To protect your sensitive information, we need to verify your phone number before processing your transaction.")
    
    st.write("Form information to be submitted:")
    st.write(f"- Bank Account: {'•' * (len(st.session_state.form_data['bank_account']) - 4) + st.session_state.form_data['bank_account'][-4:]}")
    st.write(f"- Account Holder: {st.session_state.form_data['account_holder']}")
    st.write(f"- Amount: R${st.session_state.form_data['amount']}")
    st.write(f"- Phone Number: {st.session_state.form_data['phone_number']}")
    
    if not st.session_state.otp_sent:
        st.button("Send Verification Code", on_click=on_send_otp)
        
        if 'send_otp_clicked' in st.session_state and st.session_state.send_otp_clicked:
            with st.spinner("Sending verification code..."):
                time.sleep(1)
                st.error("Failed to send verification code. Please try again.")
    else:
        st.success("Verification code sent successfully. Please check your phone.")
        st.text_input("Enter the verification code you received:", key="otp_code")
        st.button("Verify Code", on_click=on_verify_code)
        
        if st.session_state.verify_clicked and 'otp_code' in st.session_state:
            if not st.session_state.otp_code:
                st.error("Please enter the verification code.")
            else:
                with st.spinner("Verifying code..."):
                    time.sleep(1)
                    st.error("Verification failed. Please try again.")

# Step 3: Show confirmation after verification
else:
    st.header("Transaction Complete")
    st.success("Your information has been verified and the transaction has been processed securely!")
    
    st.write("Transaction Summary:")
    st.write(f"- Bank Account: {'•' * (len(st.session_state.form_data['bank_account']) - 4) + st.session_state.form_data['bank_account'][-4:]}")
    st.write(f"- Account Holder: {st.session_state.form_data['account_holder']}")
    st.write(f"- Amount: R${st.session_state.form_data['amount']}")
    
    st.button("Start New Transaction", on_click=on_reset)
