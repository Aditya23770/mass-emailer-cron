from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import threading
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'email_log.txt')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
STATUS_FILE = os.path.join(BASE_DIR, 'status.json')

app = Flask(__name__, template_folder=BASE_DIR)


def _read_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return default


def _write_status(running, message):
    with open(STATUS_FILE, 'w') as f:
        json.dump({'running': running, 'message': message, 'updated': datetime.now().isoformat()}, f)


def _run_job(job):
    import send_emails
    try:
        if job.get('test_mode'):
            _write_status(True, f"Sending test email to {job['test_email']}...")
            send_emails.send_test_email(
                test_email=job['test_email'],
                test_name=job.get('test_name', 'Test Person'),
                test_company=job.get('test_company', 'Test Company'),
                template_index=job.get('template_index', 0),
            )
            _write_status(False, f"Test email sent to {job['test_email']}.")
        else:
            n = job['num_to_send']
            _write_status(True, f"Sending {n} emails... (check logs for progress)")
            send_emails.send_emails(n, job['delay_seconds'])
            _write_status(False, f"Done. Sent {n} emails.")
    except Exception as e:
        _write_status(False, f"Error: {e}")


@app.route('/', methods=['GET', 'POST'])
def index():
    status = _read_json(STATUS_FILE, {})
    if status.get('running'):
        # Block new submissions while a job is running
        test_contacts = _read_json(CONFIG_FILE, {}).get('test_contacts', [])
        return render_template('form.html', status=status, test_contacts=test_contacts, blocked=True)

    if request.method == 'POST':
        test_mode = 'test_mode' in request.form
        if test_mode:
            job = {
                'test_mode': True,
                'test_email': request.form.get('test_email', ''),
                'test_name': request.form.get('test_name', 'Test Person'),
                'test_company': request.form.get('test_company', 'Test Company'),
                'template_index': int(request.form.get('template_index', 0)),
            }
        else:
            job = {
                'test_mode': False,
                'num_to_send': int(request.form.get('num_to_send', 0)),
                'delay_seconds': int(request.form.get('delay_seconds', 30)),
            }
        thread = threading.Thread(target=_run_job, args=(job,), daemon=True)
        thread.start()
        return redirect(url_for('index'))

    test_contacts = _read_json(CONFIG_FILE, {}).get('test_contacts', [])
    return render_template('form.html', status=status, test_contacts=test_contacts, blocked=False)


@app.route('/status')
def status():
    return jsonify(_read_json(STATUS_FILE, {'running': False, 'message': ''}))


@app.route('/logs')
def logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            log_content = f.read()
    else:
        log_content = 'No logs yet.'
    return f"<pre style='font-family:monospace; padding:1rem;'>{log_content}</pre>"


if __name__ == '__main__':
    app.run(debug=True)
