import random
from typing import Any, Dict
from app.provider_interfaces import VideoProvider, ImageProvider


class MockProvider(VideoProvider, ImageProvider):
    name = 'mock'

    def generate(self, **kwargs):
        job_id = f'mock-job-{random.randint(1000, 9999)}'
        return {
            'job_id': job_id,
            'status': 'queued',
            'provider': 'mock',
            'result_url': None,
        }

    def get_status(self, job_id: str):
        return {
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'result_url': f'https://example.com/generated/{job_id}.mp4',
        }

    def cancel(self, job_id: str):
        return {'job_id': job_id, 'status': 'cancelled'}

    def get_result(self, job_id: str):
        return {
            'job_id': job_id,
            'url': f'https://example.com/generated/{job_id}.mp4',
            'status': 'completed',
        }
