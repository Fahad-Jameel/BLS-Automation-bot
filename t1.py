import asyncio
import aiohttp
import io
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

class CaptchaSolver:
    async def solve_captcha_async(self, session, image_data):
        url = "http://38.242.213.32:8000/upload-image/?token=token123huzaifa"
        headers = {"accept": "application/json"}

        try:
            compressed_image = io.BytesIO(image_data)
            form = aiohttp.FormData()
            form.add_field('file', compressed_image, filename='captcha.jpg', content_type='image/jpeg')
            
            async with session.post(url, headers=headers, data=form) as response:
                response.raise_for_status()
                response_json = await response.json()
                return response_json
        except Exception as e:
            print(f"Captcha Not Returned! Error: {e}")
            return None

    async def get_captcha_solution(self, image_data):
        timeout = aiohttp.ClientTimeout(total=2.5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            result = await self.solve_captcha_async(session, image_data)
            if result:
                return result.get('prediction')
            else:
                return None

async def login(email, password):
    login_url = "https://blsitalypakistan.com/account/login"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Initial GET request to retrieve cookies and form details
            async with session.get(login_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
            
            # Solve CAPTCHA
            captcha_img = soup.find('img', src=re.compile(r'captcha', re.I))
            if captcha_img:
                captcha_url = urljoin(login_url, captcha_img['src'])
                async with session.get(captcha_url) as img_response:
                    img_data = await img_response.read()
                    solver = CaptchaSolver()
                    captcha_solution = await solver.get_captcha_solution(img_data)
                    if not captcha_solution:
                        return False
                    print(f"Solved CAPTCHA: {captcha_solution}")
            else:
                print("CAPTCHA image not found.")
                return False

            # Prepare form data
            csrf_token = soup.find('input', {'name': 'csrf_test_name'})['value']
            encrypted_email_field = "b986a9b7155fcaff96c6ff4ba6471b6aa320d20e12daf98aa3e6ef6974ec15932c711877312145e702214e531a7626780dbb33d60ff86e56b255e073350ba9d4Kn8vsBNXpumNMjuoQqUrr4SUBUQtB0D9wWa+cGdKCT8="

            form_data = {
                'csrf_test_name': csrf_token,
                encrypted_email_field: email,
                'login_password': password,
                'captcha_code': captcha_solution,
                'submitLogin': ''
            }

            # Prepare headers (important to mimic browser behavior)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
                'Referer': login_url,
                'Origin': 'https://blsitalypakistan.com',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Upgrade-Insecure-Requests': '1',
            }

            # Make login POST request
            async with session.post(login_url, data=form_data, headers=headers, allow_redirects=False) as response:
                if response.status == 303:
                    redirect_url = response.headers.get('Location')
                    print(f"Redirecting to: {redirect_url}")
                    return True
                else:
                    response_text = await response.text()
                    print(f"Login failed with status: {response.status}")
                    print("Response text:", response_text[:1000])  # Print more of the response text for debugging
                    return False

    except aiohttp.ClientConnectorError as e:
        print(f"Connection error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    
    return False


async def main():
    # Load credentials from the file
    with open('credentials.txt', 'r') as f:
        email = f.readline().strip()
        password = f.readline().strip()

    success = await login(email, password)
    print(f"Login {'successful' if success else 'failed'}.")

if __name__ == "__main__":
    asyncio.run(main())
