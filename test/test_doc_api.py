from unittest import TestCase
import httpx
from pathlib import Path
import random
from datetime import datetime

class TestDocAPI(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host_url = 'http://localhost:9000'
        # cls.host_url = 'https://api-gateway-yitm.onrender.com'
        
        login_url = cls.host_url + '/user_auth/login'
        res = httpx.post(login_url, data={
            'username': 'edwin',
            'email': 'edwin@gmail.com',
            'password': '123'
        })
        cls.token = res.json()['token']
        cls.images_path = list(Path("../dataset/samples_doc/image").glob("*.jpg"))
        cls.pdf_path = list(Path("../dataset/samples_doc/pdf").glob('*.pdf'))
        cls.headers = {"Authorization": "Bearer {}".format(cls.token)}
        
    def test_01_insert(self):
        api_url = self.host_url + '/doc/insert'
        headers = {"Authorization": "Bearer {}".format(self.token)}
        
        sample_docs = random.sample(self.pdf_path, 6) + random.sample(self.images_path, 4)
        
        files = [
            ("files", (open(d, "rb"))) for d in sample_docs
        ]
        res = httpx.post(api_url, files=files, headers=headers, timeout=5000)
        self.assertEqual(200, res.status_code)
        print(res.json())
    
    def test_02_list(self):
        api_url = self.host_url + '/doc/list'
        
        res = httpx.post(api_url, headers=self.headers, data={
            'page': 1, 'page_size': 10
        })
        
        self.assertEqual(200, res.status_code)
        data = res.json()['data']
        
        TestDocAPI.data_sample = data
            
    def test_03_update(self):
        api_url = self.host_url + '/doc/update'
        sample_data = random.choice(TestDocAPI.data_sample)
        sample_data['doc_type'] = 'invoice'
        sample_data['file_path'] = 'docs/test/'
        sample_data['file_name'] = 'test_2.jpg'
        sample_data['update_date'] = str(datetime.utcnow())
        
        res = httpx.post(api_url, headers=self.headers, json=sample_data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 200)
        self.assertIn('data', res.json())
        
    def test_04_search(self):
        api_url = self.host_url + '/doc/search'
        
        res = httpx.post(api_url, headers=self.headers, data={'doc_id': "b42706b9-e354-4bc3-a556-d85131c64242"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 200)
        
        print(res.json()['llm_response'])
    
    # def test_05_delete(self):
    #     api_url = self.host_url + '/doc/delete'
        
    #     for d in TestDocAPI.data_sample:
    #         res = httpx.post(api_url, headers=self.headers, data={'doc_id': d['doc_id']})
    #         self.assertEqual(res.status_code, 200)
    #         self.assertEqual(res.json()['status'], 200)