from unittest import TestCase
import httpx
import faker
from pathlib import Path
import json
import random
import asyncio

async def send_single_request(client, url, headers, image_path, run_background, schema=None):
    with open(image_path, 'rb') as f:
        files = {'documents': f}
        data = {
            'prompt': "Extract this a json",
            'system_prompt': 'You are an extraction agent',
            'run_background': run_background
        }
        if schema is not None:
            data['schema'] = json.dumps(schema)
            
        res = await client.post(url, data=data, files=files, headers=headers)
        return res.json()

async def process_images_concurrently(sampled_images, url, headers, run_background, schema=None):
    async with httpx.AsyncClient(timeout=400) as client:
        tasks = [
            send_single_request(client, url, headers, image_path, run_background, schema)
            for image_path in sampled_images
        ]
        
        results = await asyncio.gather(*tasks)
        
    return results

class TestAPI(TestCase):
    @classmethod
    def setUpClass(cls):
        # cls.host_url = 'http://localhost:9000'
        cls.host_url = 'https://api-gateway-yitm.onrender.com'
        cls.token = None
        f = faker.Faker()

        cls.user_data = {
            'username': f.user_name(),
            'email': f.email(),
            'password': f.password()
        }
        cls.images_path = list(Path("../dataset/samples_doc/image").glob("*.jpg"))
        cls.pdf_path = list(Path("../dataset/samples_doc/pdf").glob('*.pdf'))
        cls.schema_path = '../docsentry_llm_engine/schema/invoice.json'
    
    def test_02_user_login(self):
        url = self.host_url + '/user_auth/login'
        
        res = httpx.post(url, data=self.user_data)
        self.assertEqual(res.status_code, 200)
        
        data = res.json()
        self.assertIn('token', data)
        self.__class__.token = data['token']
        
    def test_01_register(self):
        url = self.host_url + '/user_auth/register'
        res = httpx.post(url, data=self.user_data)
        self.assertEqual(res.status_code, 200)
        
        data = res.json()
        self.assertIn('token', data)
        print(data)
        self.__class__.token = data['token']
    
    def test_03_user_health(self):
        url = self.host_url + '/user_auth/health'
        res = httpx.get(url)
        
        self.assertEqual(res.status_code, 200)
        self.assertIn('status', res.json())
    
    def test_04_engine_pred(self):
        with open(self.schema_path, 'r') as jsonf:
            schema = json.load(jsonf)
        
        url = self.host_url + '/engine/struct_predict'
        
        headers = {"Authorization": "Bearer {}".format(self.token)}
        
        files = random.sample(self.images_path, 1) + random.sample(self.pdf_path, 1)

        data = asyncio.run(process_images_concurrently(
            files, url, headers, False, schema
        ))
        for index, d in enumerate(data):
            print('Index: {}\nRes: {}'.format(index, d))
    
    def test_05_engine_pred_background(self):
        with open(self.schema_path, 'r') as jsonf:
            schema = json.load(jsonf)
        
        url = self.host_url + '/engine/struct_predict'
        
        headers = {"Authorization": "Bearer {}".format(self.token)}
        
        files = random.sample(self.images_path, 1)
        data = asyncio.run(process_images_concurrently(
            files, url, headers, False, schema
        ))
        
        for index, d in enumerate(data):
            # print('Index: {}\nRes: {}'.format(index, d))
            self.__class__.job_id = d['job_id']
    
    def test_06_engine_status(self):
        url = self.host_url + '/engine/status'
        headers = {"Authorization": "Bearer {}".format(self.token)}
        data = {'job_id': self.job_id}
        
        res = httpx.post(url, data=data, headers=headers, timeout=400)
        print(res.json())
    
        
    def test_07_chat(self):
        url = self.host_url + '/engine/chat'
        headers = {"Authorization": "Bearer {}".format(self.token)}
       
        files = random.sample(self.images_path, 1)
        data = asyncio.run(process_images_concurrently(
            files, url, headers, False
        ))
       
        for index, d in enumerate(data):
            print('Index: {}\nRes: {}'.format(index, d))
            
    # def test_08_test_token_limit(self):
    #     url = self.host_url + '/engine/chat'
    #     headers = {"Authorization": "Bearer {}".format(self.token)}
       
    #     files = random.sample(self.images_path, 3)
    #     data = asyncio.run(process_images_concurrently(
    #         files, url, headers, False
    #     ))
       
    #     for index, d in enumerate(data):
    #         print('Index: {}\nRes: {}'.format(index, d))
            