import requests
import os
from PIL import Image
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv('NASA_API_KEY')
if not API_KEY:
    raise ValueError('Missing NASA_API_KEY environment variable')

BASE_URL = 'https://api.nasa.gov/planetary/apod?'

class APOD:
    def __init__(self, response):
        self.response = response

    def get_data(self, key):
        return self.response.get(key, None)

    def download_image(self, url, date):
        if not os.path.isfile(f'{date}.png'):
            try:
                raw_image = requests.get(url).content
                with open(f'{date}.jpg', 'wb') as file:
                    file.write(raw_image)
            except Exception as e:
                print(f"Error downloading image: {e}")
                return None

    def convert_image(self, image_path):
        try:
            path_to_image = os.path.normpath(image_path)
            basename = os.path.basename(path_to_image)
            filename_no_extension, _ = os.path.splitext(basename)
            base_directory = 'nasa/apod_images'
            image = Image.open(path_to_image)
            image.save(os.path.join(base_directory, f"{filename_no_extension}.png"))
            os.remove(image_path)
        except Exception as e:
            print(f"Error converting image: {e}")

def get_apod_data() -> dict:
    params = {'api_key': API_KEY}
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching APOD data: {e}")
        return {}



if __name__ == "__main__":
    apod_data = get_apod_data()
    apod = APOD(apod_data)
    date = apod.get_data('date')
    url = apod.get_data('url')
    apod.download_image(url, date)
    apod.convert_image(f'{date}.jpg')
    print(apod_data)
    