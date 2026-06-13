import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(BASE_DIR, 'jobs.json')


def run_job():
    print("Scheduled task started")
    if not os.path.exists(JOBS_FILE):
        print("jobs.json not found")
        return

    with open(JOBS_FILE, 'r') as f:
        try:
            job = json.load(f)
        except json.JSONDecodeError:
            print("jobs.json decode error")
            return

    if not job or not isinstance(job, dict):
        print("No job found in jobs.json")
        return

    print(f"Job found: {job}")

    import send_emails

    if job.get('test_mode'):
        send_emails.send_test_email(
            test_email=job.get('test_email', ''),
            test_name=job.get('test_name', 'Test Person'),
            test_company=job.get('test_company', 'Test Company'),
            template_index=job.get('template_index', 0),
        )
    else:
        send_emails.send_emails(
            num_to_send=job.get('num_to_send', 0),
            delay_seconds=job.get('delay_seconds', 0),
        )

    with open(JOBS_FILE, 'w') as f:
        json.dump({}, f)
    print("Job completed and jobs.json cleared")


if __name__ == '__main__':
    run_job()
