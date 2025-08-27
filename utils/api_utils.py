import httpx
import asyncio

import io
import base64
import time
import aiofiles
import json

from typing import List
from fastapi import UploadFile

async def send_request(job_input, url, headers, timeout=300):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, headers=headers, json=job_input)
            return r.json()
    except Exception as e:
        return {"error": str(e)}
    
async def poll_jobs(job_ids, endpoint_id, api_key, timeout=300, poll_interval=5):
    async def poll_one(job_id):
        start = time.time()
        while time.time() - start < timeout:
            status = await get_job_status(job_id, endpoint_id, api_key)
            if status.get("status") in ("COMPLETED", "FAILED", "CANCELLED", "ERROR"):
                return status
            await asyncio.sleep(poll_interval)
        return {"id": job_id, "status": "TIMEOUT"}

    return await asyncio.gather(*[poll_one(jid) for jid in job_ids])
        
async def submit_jobs(job_input, url, headers, api_key, job_id, background=False, is_complete=False):
    tasks = []
    
    for job in job_input:
        tasks.append(send_request(job, url, headers))
        
    job_responses = await asyncio.gather(*tasks)
    if background:
        if is_complete:
            job_ids = [r['id'] for r in job_responses]
            results = await poll_jobs(job_ids, job_id, api_key)
        else:
            results = job_responses
        return results
    else:
        all_completed = all(job.get("status") == "COMPLETED" for job in job_responses)
        if all_completed:
            return job_responses  # wait for results
        else:
            # Efficient batch polling for incomplete jobs
            completed_jobs = [job for job in job_responses if job.get("status") == "COMPLETED"]
            incomplete_jobs = [job for job in job_responses if job.get("status") != "COMPLETED"]

            if incomplete_jobs:
                job_ids = [job.get("id") for job in incomplete_jobs]
                polled_results = await poll_jobs(job_ids, '67awaqzdmoq3fn', api_key)

                # Add only those that are now completed
                completed_jobs.extend([job for job in polled_results if job.get("status") == "COMPLETED"])

            return completed_jobs

async def get_job_status(job_id, endpoint_id, api_key):
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"id": job_id, "status": "ERROR", "details": response.text}

async def read_json_file(path):
    async with aiofiles.open(path, 'r', encoding='utf-8') as f:
        content = await f.read()
        data = json.loads(content)
        return data

