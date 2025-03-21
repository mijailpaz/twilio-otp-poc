import streamlit as st
from twilio.rest import Client
import time
import pyotp
import qrcode
from io import BytesIO
from PIL import Image

# --- Twilio configuration from Streamlit secrets ---
try:
    TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_VERIFY_SERVICE_SID = st.secrets["TWILIO_VERIFY_SERVICE_SID"]
except Exception as e:
    st.error(f"Error loading Twilio secrets: {e}")
    st.info("Please configure Twilio credentials in .streamlit/secrets.toml")
    TWILIO_ACCOUNT_SID = ""
    TWILIO_AUTH_TOKEN = ""
    TWILIO_VERIFY_SERVICE_SID = ""

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

# --- Functions for TOTP (Google Authenticator) ---
def generate_totp_secret():
    """Generate a new TOTP secret key"""
    return pyotp.random_base32()

def get_totp_qr_code(secret, user_email):
    """Generate a QR code for the TOTP secret"""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(user_email, issuer_name="Sympla POC")
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def verify_totp(secret, token):
    """Verify a TOTP token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

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
    
# TOTP session state variables
if "totp_secret" not in st.session_state:
    st.session_state.totp_secret = None
if "totp_setup_complete" not in st.session_state:
    st.session_state.totp_setup_complete = False
if "totp_verified" not in st.session_state:
    st.session_state.totp_verified = False
if "totp_form_data" not in st.session_state:
    st.session_state.totp_form_data = {}
if "totp_submit_clicked" not in st.session_state:
    st.session_state.totp_submit_clicked = False
if "totp_verify_clicked" not in st.session_state:
    st.session_state.totp_verify_clicked = False
if "totp_reset_clicked" not in st.session_state:
    st.session_state.totp_reset_clicked = False

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

# TOTP callback functions
def on_totp_form_submit():
    st.session_state.totp_submit_clicked = True

def on_setup_totp():
    st.session_state.totp_secret = generate_totp_secret()
    st.rerun()

def on_verify_totp():
    st.session_state.totp_verify_clicked = True

def on_totp_reset():
    st.session_state.totp_reset_clicked = True
    for key in ['totp_setup_complete', 'totp_verified', 'totp_form_data', 'totp_submit_clicked', 'totp_verify_clicked', 'totp_reset_clicked', 'totp_secret']:
        if key in st.session_state:
            if key == 'totp_form_data':
                st.session_state[key] = {}
            elif key == 'totp_secret':
                st.session_state[key] = None
            else:
                st.session_state[key] = False
    st.rerun()

# --- Streamlit App ---
st.title("Twilio Verify OTP Integration POC for Sympla")

# Add POC explanation
st.markdown("""
### Project Overview
In this proof-of-concept, we explore the integration of Twilio Verify to enhance security within the Sympla event registration platform. 
With the increasing need for robust data protection during ticket purchases and user sign-ups, this solution introduces a seamless OTP verification step to authenticate users before they proceed with sensitive transactions. 
By embedding this additional layer of security into the registration flow, Sympla can further safeguard sensitive information, reduce fraud risk, and bolster user confidence, ultimately creating a more secure and reliable experience for event organizers and attendees alike.
""")

# Create tabs for different authentication methods
tab1, tab2 = st.tabs(["SMS OTP Verification", "TOTP Authentication (Google Authenticator)"])

with tab1:
    # Process form submission for SMS OTP
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

with tab2:
    # Process TOTP form submission
    if st.session_state.totp_submit_clicked and not st.session_state.totp_setup_complete:
        if all(field in st.session_state for field in ['totp_bank_account', 'totp_account_holder', 'totp_amount', 'totp_email']):
            if (st.session_state.totp_bank_account and st.session_state.totp_account_holder and 
                st.session_state.totp_amount > 0 and st.session_state.totp_email):
                
                st.session_state.totp_setup_complete = True
                st.session_state.totp_form_data = {
                    "bank_account": st.session_state.totp_bank_account,
                    "account_holder": st.session_state.totp_account_holder,
                    "amount": st.session_state.totp_amount,
                    "email": st.session_state.totp_email
                }
                # Generate a TOTP secret if one doesn't exist
                if not st.session_state.totp_secret:
                    st.session_state.totp_secret = generate_totp_secret()
                st.session_state.totp_submit_clicked = False
                st.rerun()

    # Process TOTP verification
    if st.session_state.totp_verify_clicked and not st.session_state.totp_verified and st.session_state.totp_setup_complete:
        if 'totp_code' in st.session_state and st.session_state.totp_code:
            verified = verify_totp(st.session_state.totp_secret, st.session_state.totp_code)
            if verified:
                st.session_state.totp_verified = True
                st.session_state.totp_verify_clicked = False
                st.rerun()

    # Process TOTP reset
    if st.session_state.totp_reset_clicked:
        st.rerun()

    # Explanation about TOTP
    st.header("TOTP Authentication with Google Authenticator")
    st.markdown("""
    Time-based One-Time Password (TOTP) authentication provides a more secure alternative to SMS-based verification. 
    Instead of receiving a code via SMS, users scan a QR code with an authenticator app like Google Authenticator, 
    which then generates time-based codes that change every 30 seconds.
    
    This method offers several advantages:
    - **No reliance on cellular networks**: Works even without cellular reception
    - **Offline operation**: Generates codes without internet connection
    - **Greater security**: Less vulnerable to SIM swapping attacks
    - **Global access**: Works internationally without SMS costs
    """)
    
    # Step 1: Show the sensitive form for TOTP flow
    if not st.session_state.totp_setup_complete:
        st.header("Step 1: Enter Sensitive Information")
        st.write("Please fill out the following information for your transaction:")
        
        with st.form(key="totp_form"):
            st.text_input("Bank Account Number:", key="totp_bank_account")
            st.text_input("Account Holder Name:", key="totp_account_holder")
            st.number_input("Amount (BRL):", min_value=0.0, step=0.01, key="totp_amount")
            st.text_input("Your Email Address:", key="totp_email")
            st.form_submit_button("Proceed to TOTP Setup", on_click=on_totp_form_submit)
        
        if st.session_state.totp_submit_clicked:
            if not all(field in st.session_state and st.session_state[field] for field in ['totp_bank_account', 'totp_account_holder', 'totp_email']) or not (st.session_state.totp_amount > 0):
                st.error("Please fill in all fields with valid information.")

    # Step 2: Set up TOTP with the user
    elif not st.session_state.totp_verified:
        st.header("Step 2: Set Up Authenticator App")
        st.write("To protect your sensitive information, we'll use an authenticator app for verification.")
        
        st.write("Form information to be submitted:")
        st.write(f"- Bank Account: {'•' * (len(st.session_state.totp_form_data['bank_account']) - 4) + st.session_state.totp_form_data['bank_account'][-4:]}")
        st.write(f"- Account Holder: {st.session_state.totp_form_data['account_holder']}")
        st.write(f"- Amount: R${st.session_state.totp_form_data['amount']}")
        st.write(f"- Email: {st.session_state.totp_form_data['email']}")
        
        # Display QR code for TOTP setup
        st.subheader("Set up your authenticator app")
        st.markdown("""
        1. Open your authenticator app (Google Authenticator, Authy, etc.)
        2. Tap the + button to add a new account
        3. Scan the QR code below
        4. Enter the 6-digit code from your app to verify
        """)
        
        # Generate and display QR code
        qr_code = get_totp_qr_code(st.session_state.totp_secret, st.session_state.totp_form_data['email'])
        st.image(qr_code, caption="Scan this QR code with your authenticator app", width=300)
        
        # Provide the secret as text for manual entry
        with st.expander("Can't scan the code?"):
            st.code(st.session_state.totp_secret)
            st.write("Enter this code manually in your authenticator app.")
        
        # Verify the TOTP code
        st.text_input("Enter the 6-digit code from your authenticator app:", key="totp_code")
        st.button("Verify Code", on_click=on_verify_totp)
        
        if st.session_state.totp_verify_clicked and 'totp_code' in st.session_state:
            if not st.session_state.totp_code:
                st.error("Please enter the verification code from your authenticator app.")
            else:
                with st.spinner("Verifying code..."):
                    time.sleep(1)
                    if not verify_totp(st.session_state.totp_secret, st.session_state.totp_code):
                        st.error("Verification failed. Please make sure you entered the correct code and try again.")

    # Step 3: Show confirmation after TOTP verification
    else:
        st.header("Transaction Complete")
        st.success("Your information has been verified using TOTP authentication and the transaction has been processed securely!")
        
        st.write("Transaction Summary:")
        st.write(f"- Bank Account: {'•' * (len(st.session_state.totp_form_data['bank_account']) - 4) + st.session_state.totp_form_data['bank_account'][-4:]}")
        st.write(f"- Account Holder: {st.session_state.totp_form_data['account_holder']}")
        st.write(f"- Amount: R${st.session_state.totp_form_data['amount']}")
        
        st.button("Start New Transaction", on_click=on_totp_reset, key="totp_reset_button")
