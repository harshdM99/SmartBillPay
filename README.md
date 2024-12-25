# SmartBillPay

**SmartBillPay** is an automation tool written in Python to simplify and automate the process of paying credit card bills. This project is tailored for Bank of America accounts and ensures timely payments by integrating web automation and email notifications.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [.env File Configuration](#env-file-configuration)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Features
* Automates login to the Bank of America website.
* Navigates to the credit card payment page and schedules payments.
* Sends email notifications regarding payment status.
* Operates in headless mode for seamless background execution.

## Tech Stack
* `Python`
* `Selenium`: For browser automation.
* `smtplib`: For sending email notifications.
* `dotenv`: For managing environment variables securely.

## Prerequisites
1. **Python 3.7+**: Ensure you have Python installed.
1. **Google Chrome/Brave Browser**: The automation requires a Chromium-based browser.
1. **ChromeDriver**: Compatible with your browser version.
1. **Environment Variables**: Create a .env file to store sensitive information.

## .env File Configuration
```makefile
BRAVE_PATH=/path/to/brave
USER_ID=your_bank_of_america_user_id
PASSWORD=your_bank_of_america_password
LOGIN_PAGE=https://secure.bankofamerica.com/login/sign-in/signOnV2Screen.go
SENDER_EMAIL_ID=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
RECEIVER_EMAIL=receiver_email@gmail.com
```

## Installation
1. Clone the repository:
```bash
git clone https://github.com/your-username/smartbillpay.git
cd smartbillpay
```

2. Install dependencies:
```bash
pip install -r requirements.txt
Set up your .env file as described above.
```

## Usage
Run the script using the following command:
```bash
python smartbillpay.py
```
Optional Arguments
* `-d`, `--debug`: Enables debug mode to keep the browser window open for inspection.

## Future Enhancements
Extend compatibility to other banks.

## Contributing
Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
```bash
git checkout -b feature-name
```
3. Commit your changes and push the branch:
```bash
git push origin feature-name
```
4. Open a pull request.