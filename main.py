import json
import time
from datetime import datetime
import requests
from tqdm import tqdm

with open('token.txt', 'r') as f:
    token_vk = f.read().strip()

with open('version.txt', 'r') as f1:
    version = f1.read().strip()

with open('token1.txt', 'r') as f2:
    token_yd = f2.read().strip()


class VkUserYaUploader:
    url = 'https://api.vk.com/method/'

    def __init__(self, token_vk, version, token_yd):
        self.params = {
            'access_token': token_vk,
            'v': version
        }
        self.token_yd = token_yd
        self.HEADERS = {"Authorization": f'OAuth {self.token_yd}'}

    def get_photo(self):
        photo_url = self.url + 'photos.get'
        photo_get_params = {
            'album_id': 'profile',
            'rev': 0,
            'extended': 1,
            'photo_sizes': 1
        }
        photo_lists = requests.get(photo_url, params={**self.params, **photo_get_params}).json()['response']['items']
        photo_info = []
        url_list = []
        dict_f = {}
        for counts, photo in enumerate(photo_lists):
            time.sleep(1)
            if counts == 5:
                break
            else:
                if photo['likes']['count'] in dict_f:
                    dict_f[f"{photo['likes']['count']}_{datetime.fromtimestamp(photo['date']).date()}"] = \
                        photo['sizes'][-1]['url']
                    info = {
                        'name': f"{photo['likes']['count']}_{datetime.fromtimestamp(photo['date']).date()}.jpg,'size': "
                                f"{photo['sizes'][-1]['type']}"
                    }
                    url = {photo['sizes'][-1]['url']}
                else:
                    dict_f[photo['likes']['count']] = photo['sizes'][-1]['url']
                    info = {'name': f"{photo['likes']['count']}.jpg, 'size': {photo['sizes'][-1]['type']}"}
                    url = {photo['sizes'][-1]['url']}
                photo_info.append(info)
                url_list.append(url)

        with open('Vk_photos_info.json', 'w') as file:
            json.dump(photo_info, file, indent=0)

        return dict_f

    def create_catalog(self, yadisk_foto: str):
        create_cat = "https://cloud-api.yandex.net/v1/disk/resources"
        parameters = {"path": yadisk_foto}
        create = requests.put(create_cat, headers=self.HEADERS, params=parameters)
        create.raise_for_status()
        if create.status_code == 201:
            return f'Папка "{yadisk_foto}" создана на Yandex Disk'
        else:
            return "Что-то не так!"

    def upload_foto(self, path_o: str):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        path_dict = self.get_photo()

        for name, url_vk_foto in tqdm((path_dict.items()), desc='Загрузка фото на диск'):
            time.sleep(2)
            path_o_ya = f'{path_o},{name}.jpg'

            params = {"path": path_o_ya, "url": url_vk_foto}
            requests.post(upload_url, headers=self.HEADERS, params=params)
        return


vk_client = VkUserYaUploader(token_vk, version, token_yd)
vk_client.get_photo()
print(vk_client.create_catalog('vk_foto'))
vk_client.upload_foto('vk_foto/')
