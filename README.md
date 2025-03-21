# Twilio Verify OTP Integration POC for Sympla

## Project Overview

This proof-of-concept (POC) demonstrates the integration of multiple authentication methods within the Sympla event registration platform. The solution introduces additional security layers that validate the user's identity before finalizing sensitive transactions, such as submitting bank account details.

![Twilio Verify Flow](https://twilio-cms-prod.s3.amazonaws.com/images/verify-flow-transparent-background.width-800.png)

## Key Features

- **Enhanced Security**: Two-factor authentication ensures that only authenticated users can submit sensitive data
- **Multiple Verification Methods**:
  - SMS OTP via Twilio Verify
  - TOTP Authentication (compatible with Google Authenticator, Authy, etc.)
- **Streamlined User Experience**: Seamless integration of verification steps within the existing registration flow
- **Multi-step Verification Process**: Clear separation of data collection and verification steps
- **Data Protection**: Sensitive information is only processed after successful verification

## How It Works

### SMS OTP Flow
1. **Form Submission**: Users enter sensitive transaction information, including bank account details
2. **OTP Verification**: A one-time password is sent to the user's phone number for verification
3. **Secure Processing**: Only after successful verification is the transaction completed

### TOTP Authentication Flow
1. **Form Submission**: Users enter sensitive transaction information, including bank account details
2. **QR Code Generation**: A unique QR code is generated for the user to scan with their authenticator app
3. **TOTP Verification**: User enters the time-based code from their authenticator app
4. **Secure Processing**: Only after successful verification is the transaction completed

## Technical Implementation

The project utilizes:
- **Streamlit**: For creating the interactive web interface
- **Twilio Verify API**: For handling SMS verification
- **PyOTP**: For implementing TOTP authentication (Google Authenticator compatibility)
- **QRCode**: For generating QR codes for TOTP setup
- **Session State Management**: For maintaining application state across steps
- **Streamlit Secrets Management**: For storing API credentials securely

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Twilio account with Verify service enabled

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/poc-twilio.git
cd poc-twilio
```

2. Install the required packages
```bash
pip install -r requirements.txt
```

3. Configure your Twilio credentials
   
   a. Create a `.streamlit` directory in the project root if it doesn't exist:
   ```bash
   mkdir -p .streamlit
   ```
   
   b. Copy the example secrets file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   
   c. Edit `.streamlit/secrets.toml` and add your actual Twilio credentials:
   ```toml
   TWILIO_ACCOUNT_SID = "your_account_sid"
   TWILIO_AUTH_TOKEN = "your_auth_token"
   TWILIO_VERIFY_SERVICE_SID = "your_verify_service_sid"
   ```

   > **IMPORTANT**: Never commit the `secrets.toml` file to version control. It's already in `.gitignore`.

### Running the Application

```bash
streamlit run app.py
```

## Security Considerations

- The application now uses Streamlit's secrets management to securely store Twilio credentials.
- This approach prevents credentials from being exposed in source code or version control.
- TOTP authentication provides enhanced security over SMS OTP, as it's not vulnerable to SIM swapping attacks.
- TOTP works offline and doesn't require cellular reception, making it more reliable in various environments.
- In production environments, consider using environment variables or a dedicated secrets management service.
- Never expose Twilio credentials in client-side code in a production environment.
- Consider implementing additional security measures like rate limiting and IP filtering.

## Comparison of Authentication Methods

| Feature | SMS OTP | TOTP (Google Authenticator) |
|---------|---------|----------------------------|
| Network Dependency | Requires cellular network | Works offline |
| Global Access | May have delivery issues internationally | Works worldwide |
| Security | Vulnerable to SIM swapping | Not vulnerable to SIM swapping |
| User Experience | Simple, familiar to most users | Requires app installation |
| Cost | Requires paid SMS service | Free after implementation |

## Future Enhancements

- Email verification as an alternative to SMS
- WhatsApp channel integration for OTP delivery
- Biometric verification options
- Integration with fraud detection systems
- Push notification authentication
- U2F/WebAuthn support (hardware security keys)

## License

[MIT License](LICENSE)

## Acknowledgments

- Twilio for providing the Verify API
- Streamlit for the web application framework
- PyOTP for the TOTP implementation
