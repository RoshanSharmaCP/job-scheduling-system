from celery_app import celery_app
from models import Job
from database import SessionLocal
from sqlalchemy.orm import Session
import time
from datetime import datetime

def get_job(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()

@celery_app.task(bind=True, max_retries=3)
def execute_job(self, job_id):
    db = SessionLocal()
    job = get_job(db, job_id)

    try:
        # Simulate a long-running job
        time.sleep(5)
        job.status = "completed"
        job.result = "Success"
    except Exception as exc:
        job.status = "failed"
        job.retry_count += 1
        if job.retry_count < job.max_retries:
            self.retry(exc=exc)
        else:
            job.result = str(exc)
    finally:
        job.updated_at = datetime.utcnow()
        db.commit()
        db.close()
