# Twilio Verify OTP Integration POC for Sympla

## Project Overview

This proof-of-concept (POC) demonstrates the integration of Twilio Verify for One-Time Password (OTP) authentication within the Sympla event registration platform. The solution introduces an additional security layer that validates the user's phone number before finalizing sensitive transactions, such as submitting bank account details.

![Twilio Verify Flow](https://twilio-cms-prod.s3.amazonaws.com/images/verify-flow-transparent-background.width-800.png)

## Key Features

- **Enhanced Security**: OTP-based verification ensures that only authenticated users can submit sensitive data.
- **Streamlined User Experience**: Seamless integration of OTP verification within the existing registration flow.
- **Multi-step Verification Process**: Clear separation of data collection and verification steps.
- **Data Protection**: Sensitive information is only processed after successful phone verification.

## How It Works

1. **Form Submission**: Users enter sensitive transaction information, including bank account details.
2. **OTP Verification**: A one-time password is sent to the user's phone number for verification.
3. **Secure Processing**: Only after successful verification is the transaction completed.

## Technical Implementation

The project utilizes:
- **Streamlit**: For creating the interactive web interface
- **Twilio Verify API**: For handling SMS verification
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
- In production environments, consider using environment variables or a dedicated secrets management service.
- Never expose Twilio credentials in client-side code in a production environment.
- Consider implementing additional security measures like rate limiting and IP filtering.

## Future Enhancements

- Email verification as an alternative to SMS
- WhatsApp channel integration for OTP delivery
- Biometric verification options
- Integration with fraud detection systems

## License

[MIT License](LICENSE)

## Acknowledgments

- Twilio for providing the Verify API
- Streamlit for the web application framework
# twilio-otp-poc
