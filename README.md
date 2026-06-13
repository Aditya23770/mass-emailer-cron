# Cold Email Automation Tool

A Flask web app that automates sending personalized cold emails for job applications. Manages your contact list, rotates email templates, attaches your resume, and tracks who has already been contacted.

---

## Features

- Multiple personalized email templates (rotated automatically)
- CSV-based contact management with duplicate prevention
- PDF resume attached to every email
- Configurable delay between sends to avoid spam filters
- Web UI to trigger sends, set test mode, and monitor status
- Real-time logs viewable at `/logs`
- WSGI-ready for deployment on PythonAnywhere

---

## Project Structure

```
cold-email-tool/
├── app.py                  # Flask web app (main entry point)
├── send_emails.py          # Email sending engine
├── scheduled_task.py       # Background job runner
├── wsgi.py                 # WSGI config for production deployment
├── requirements.txt        # Python dependencies
├── .env.example            # Template for your .env file (copy and fill)
├── config.example.json     # Template for config.json (copy and fill)
├── contacts_example.csv    # Demo contacts file (copy to filtered_contacts.csv)
├── example_resume.pdf      # Demo PDF resume (replace with yours)
├── template_1.txt          # Email template 1
├── template_2.txt          # Email template 2
├── template_3.txt          # Email template 3
├── templates/
│   └── form.html           # Web UI HTML form
└── .gitignore              # Excludes sensitive files from git
```

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/cold-email-tool.git
cd cold-email-tool
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your environment

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
SENDER_NAME=Your Full Name
SENDER_PHONE=+91-XXXXXXXXXX
SENDER_LINKEDIN=linkedin.com/in/your-profile
SENDER_GITHUB=github.com/YourUsername
RESUME_PATH=example_resume.pdf
```

### 4. Configure the app

```bash
cp config.example.json config.json
```

Edit `config.json` if needed (change subjects, add test contacts, etc.).

### 5. Add your contacts

```bash
cp contacts_example.csv filtered_contacts.csv
```

Replace the sample rows with your real contacts. Format: `Name,Email,Company`

### 6. Add your resume

Replace `example_resume.pdf` with your actual resume PDF, then update `RESUME_PATH` in `.env`.

### 7. Run the app

```bash
python app.py
```

Open your browser at `http://localhost:5000`

---

## Gmail App Password Setup

> **Why not just use your normal Gmail password?**
>
> Your normal Gmail password is what you type when logging into Gmail in a browser. Google blocks external apps from using it directly for security reasons.
>
> An **App Password** is a special 16-character password that Google generates **just for this app**. It lets the tool send emails on your behalf without knowing your real password. If compromised, you can revoke it instantly without changing your main password.

**Steps to create a Gmail App Password:**

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", enable **2-Step Verification** (required)
4. Go back to **Security** → scroll down → click **App passwords**
   *(If you don't see this option, 2FA is not enabled yet)*
5. Under "Select app" choose **Mail**
6. Under "Select device" choose **Other (Custom name)** → type `cold-email-tool`
7. Click **Generate**
8. Copy the 16-character password shown (e.g. `abcd efgh ijkl mnop`)
9. Paste it into your `.env` file as `GMAIL_APP_PASSWORD`

> Keep this password secret — treat it like a password. Anyone with it can send emails from your Gmail account.

---

## Customizing Email Templates

Edit `template_1.txt`, `template_2.txt`, `template_3.txt` to match your background and tone.

**Available placeholders:**

| Placeholder | Replaced with |
|---|---|
| `{name}` | Recipient's name from CSV |
| `{company}` | Company name from CSV |
| `{sender_name}` | Your name from `.env` |
| `{sender_phone}` | Your phone from `.env` |
| `{sender_linkedin}` | Your LinkedIn from `.env` |
| `{sender_github}` | Your GitHub from `.env` |

The tool cycles through templates in order (template 1 → 2 → 3 → 1 ...) so each contact gets a slightly different email.

---

## How to Get HR / Recruiter Contacts

Your contacts CSV needs three columns: `Name`, `Email`, `Company`.

**Where to find recruiter emails:**

- **[Topmate.io](https://topmate.io)** — Book 1:1s with hiring managers and recruiters; get direct contact details
- **[Apollo.io](https://apollo.io)** — Search by job title + company; free tier includes limited exports
- **[Hunter.io](https://hunter.io)** — Find verified work email addresses by company domain
- **LinkedIn** — Connect first, then message for email; some profiles show email directly

> *(Add your own sourcing tool links below this line)*
> <!-- INSERT YOUR PRODUCT LINKS HERE -->

**Important:** Only email people who may reasonably expect outreach (recruiters, HR, hiring managers). Respect anti-spam laws — include your contact info and never mislead recipients about who you are.

---

## Deploying on PythonAnywhere (Free Hosting)

PythonAnywhere offers a **free tier** that can host this Flask app permanently. No credit card required.

### Step 1 — Create a PythonAnywhere Account

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click **Pricing & signup** → **Create a Beginner account** (free)
3. Fill in username, email, password → Sign up
4. Verify your email address

> [SCREENSHOT: PythonAnywhere signup page]

---

### Step 2 — Upload Your Code

**Option A — Git clone (recommended):**

1. From the PythonAnywhere dashboard, click **Consoles** in the top menu
2. Click **Bash** to open a new Bash console
3. Run:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cold-email-tool.git
   ```
4. Your code is now at `/home/YOUR_USERNAME/cold-email-tool/`

> [SCREENSHOT: PythonAnywhere Bash console with git clone command]

**Option B — Manual upload:**

1. Click **Files** in the top menu
2. Navigate to your home directory
3. Click **Upload a file** and upload each project file

---

### Step 3 — Create a Virtual Environment

In the Bash console, run these commands one by one:

```bash
mkvirtualenv myenv --python=python3.10
workon myenv
pip install -r cold-email-tool/requirements.txt
```

> Wait for all packages to install. This may take 1–2 minutes.

> [SCREENSHOT: Virtual environment creation in Bash console]

---

### Step 4 — Create the Web App

1. Click **Web** in the top menu
2. Click **Add a new web app** button
3. Click **Next**
4. Choose **Manual configuration** (NOT "Flask" — we configure it ourselves)
5. Select **Python 3.10** → click **Next**
6. Your web app is created. You'll land on the Web app configuration page.

> [SCREENSHOT: Web tab → Add new web app → Manual configuration]

---

### Step 5 — Configure the Virtualenv

On the Web app configuration page:

1. Scroll down to the **Virtualenv** section
2. Click the text box and enter:
   ```
   /home/YOUR_USERNAME/.virtualenvs/myenv
   ```
   *(Replace `YOUR_USERNAME` with your actual PythonAnywhere username)*
3. Click the checkmark / tick to save

> [SCREENSHOT: Virtualenv section filled in]

---

### Step 6 — Edit the WSGI File

1. On the Web app configuration page, find **WSGI configuration file**
2. Click the link (it looks like `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`)
3. The file editor opens — **delete all the existing content**
4. Paste in the following:

```python
import sys
import os

sys.path.insert(0, '/home/YOUR_USERNAME/cold-email-tool')

from dotenv import load_dotenv
load_dotenv('/home/YOUR_USERNAME/cold-email-tool/.env')

from app import app as application
```

*(Replace `YOUR_USERNAME` with your actual username)*

5. Click **Save** (top right of the editor)

> [SCREENSHOT: WSGI file editor with the above code]

---

### Step 7 — Set Environment Variables

1. Go back to the **Web** tab
2. Scroll down to the **Environment variables** section
3. Add each variable from your `.env` file:

   | Variable | Value |
   |---|---|
   | `GMAIL_ADDRESS` | your_gmail@gmail.com |
   | `GMAIL_APP_PASSWORD` | xxxx xxxx xxxx xxxx |
   | `SENDER_NAME` | Your Full Name |
   | `SENDER_PHONE` | +91-XXXXXXXXXX |
   | `SENDER_LINKEDIN` | linkedin.com/in/your-profile |
   | `SENDER_GITHUB` | github.com/YourUsername |
   | `RESUME_PATH` | /home/YOUR_USERNAME/cold-email-tool/example_resume.pdf |

4. Click **Save** after adding all variables

> [SCREENSHOT: Environment variables section filled in]

---

### Step 8 — Create Your Config File

In the Bash console:

```bash
cd cold-email-tool
cp config.example.json config.json
```

Edit `config.json` to add your test contacts if desired.

---

### Step 9 — Upload Your Contacts and Resume

In the Bash console, or via the **Files** tab:

- Upload your `filtered_contacts.csv` (your actual contact list)
- Upload your real resume PDF and note the path (e.g. `/home/YOUR_USERNAME/cold-email-tool/MyResume.pdf`)
- Update `RESUME_PATH` in the environment variables section to point to it

---

### Step 10 — Reload and Test

1. On the **Web** tab, click the big green **Reload** button
2. Visit your app at: `https://YOUR_USERNAME.pythonanywhere.com`
3. You should see the email form UI
4. Use **Test Mode** to send a test email to yourself first

> [SCREENSHOT: Web app running at pythonanywhere.com URL]

> **Troubleshooting:** If the app shows an error, click the **error log** link on the Web tab to see what went wrong.

---

## GitHub Repository Setup

See the `setup.md` file in your local project directory for step-by-step instructions on creating a GitHub repo and pushing this code.

*(That file is intentionally excluded from git so your personal push steps stay local.)*

---

## License

MIT — free to use, modify, and share.
