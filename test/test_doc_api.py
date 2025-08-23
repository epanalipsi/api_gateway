from unittest import TestCase
import httpx
from pathlib import Path
import random

class TestDocAPI(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host_url = 'http://localhost:8000'
        
        login_url = cls.host_url + '/user_auth/login'
        res = httpx.post(login_url, data={
            'email': 'edwin@gmail.com',
            'password': '123'
        })
        cls.token = res.json()['token']
        cls.images_path = list(Path("../dataset/samples_doc/image").glob("*.jpg"))
        cls.pdf_path = list(Path("../dataset/samples_doc/pdf").glob('*.pdf'))
        
    def test_01_insert(self):
        api_url = self.host_url + '/doc/insert'
        headers = {"Authorization": "Bearer {}".format(self.token)}
        
        sample_docs = random.sample(self.pdf_path, 3)
        
        files = [
            ("documents", (open(d, "rb"))) for d in sample_docs
        ]
        res = httpx.post(api_url, files=files, headers=headers)
        print(res)
    
    def test_02_list(self):
        pass