from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base, Job
from schemas import JobCreate, JobResponse
from celery_app import celery_app
from celery.result import AsyncResult

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/jobs/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(name=job.name)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Schedule job
    try:
        task = celery_app.send_task("celery_worker.execute_job", args=[db_job.id])
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    return db_job

@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }
