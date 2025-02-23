import requests
from progress.bar import Bar
from datetime import datetime
from apikeys import TOKEN_VK, TOKEN_YNDX
from pprint import pprint


class VKphotos:

    common_url = 'https://api.vk.com/method/'

    def __init__(self,user_id: str, vk_token: str):
        self.vk_token = vk_token
        self.user_id = user_id
        self.common_params = {
            'access_token': self.vk_token,
            'v': 5.199
        }

    def _mode_date(self, second: str):
        ts = int(second)
        return datetime.fromtimestamp(ts).strftime('%d.%m.%Y_%H.%M.%S')

    def get_photos(self, album_ids=[('profile', 'Фотографии профиля')]):
        """
        Function for get photo's data.
        :param album_ids: list of tuples: (id_album, name_album)
        :return: dict where key is name_album, value is list of photo's data
        """
        photos = {}
        add_url = 'photos.get'
        params = self.common_params

        for album_id in album_ids:
            params.update({
                'owner_id': self.user_id,
                'extended': 1,
                'album_id': album_id[0]
            })
            use_name = set()
            response = requests.get(f'{self.common_url}{add_url}', params=params)
            if 100 <= response.status_code < 400:
                if list(response.json().keys())[0] == "error":
                    continue
                for item in Bar(f'Search photos from "{album_id[1]}"').iter(response.json()['response']['items']):
                    name_photo = item['likes']['count']
                    if name_photo in use_name:
                        name_photo = f'{name_photo}_' + self._mode_date(item['date'])
                    if album_id[1] in photos:
                        photos[album_id[1]].append({
                            'name_photo': name_photo,
                            'size': f'{item['orig_photo']['width']}x{item['orig_photo']['height']}',
                            'url': item['orig_photo']['url'] + f'&cs={item['orig_photo']['width']}x{item['orig_photo']['height']}'
                        })
                    else:
                        photos[album_id[1]] = []
                        photos[album_id[1]].append({
                            'name_photo': name_photo,
                            'size': f'{item['orig_photo']['width']}x{item['orig_photo']['height']}',
                            'url': item['orig_photo']['url'] + f'&cs={item['orig_photo']['width']}x{item['orig_photo']['height']}'
                        })
                    use_name.add(name_photo)
            else:
                continue
        return photos

    
    def get_albums(self):
        """
        :return: all non-empty albums from user. If user have no albums then return empty list.
        """
        albums = []
        add_url = 'photos.getAlbums'
        params = self.common_params
        params.update({
            'owner_id': self.user_id,
        })
        response = requests.get(f'{self.common_url}{add_url}', params=params)
        if 200 <= response.status_code < 400:
            if list(response.json().keys())[0] == "error":
                return albums
            for item in response.json()['response']['items']:
                if item['size'] > 0:
                    albums.append((item['id'], item['title']))
        return albums
    

class YNDXdisk:

    common_url = 'https://cloud-api.yandex.net/'

    def __init__(self, yndx_token):
        self.headers = {
            'Authorization': yndx_token
        }

    def check_or_made_folder(self, name_folder: str):
        """
        Check folder on resourse, if folder does not exist func made this.
        return: boolean True
        """
        add_url = 'v1/disk/resources/'
        params = {'path': name_folder}
        response = requests.get(f'{self.common_url}{add_url}', headers=self.headers, params=params)
        if 200 <= response.status_code < 400:
            return True
        else:
            requests.put(f'{self.common_url}{add_url}', headers=self.headers, params=params)
        return True

    def upload_photos(self, name_folder: str, name_photos: str, file_photo: bytes):
        """
        Load photo on resourse
        """
        add_url = 'v1/disk/resources/upload'
        params = {
            'path': f'{name_folder}/{name_photos}.jpg',
            }
        response_get = requests.get(f'{self.common_url}{add_url}', headers=self.headers, params=params)
        if 200 <= response_get.status_code < 400:
            response_put = requests.put(response_get.json()['href'], files={'file': file_photo})
            return True
        else:
            return False

if __name__ == '__main__':
    user_VK = VKphotos('########', TOKEN_VK) # Создаем экземпляр класса VKphotos
    photos = user_VK.get_photos() # Получаем словарь: key="Название альбома", value="список словарей с параметрами к фото"
    user_YNDX = YNDXdisk(TOKEN_YNDX) # Создаем экзепляр класса YNDXdisk
    user_YNDX.check_or_made_folder('backup_photos') # создаем папку для резервного копирования backup_photo
    for name_album in photos.keys(): # проходим по каждому альбому в переменной photos
        name_folder = f'backup_photos/{name_album}'
        user_YNDX.check_or_made_folder(name_folder) #создаем папку внутри backup_photos с названием альбома
        for photo in photos[name_album]: # проходим по каждому фото внутри альбома
            response = requests.get(photo['url'])
            user_YNDX.upload_photos(name_folder=name_folder, name_photos=photo['name_photo'], file_photo=response.content) # загружаем фото на яндекс диск

    user_VK = VKphotos('########', TOKEN_VK)
    alb = user_VK.get_albums()
    photos = user_VK.get_photos(alb)
    pprint(photos)
    for name_album in photos.keys(): # проходим по каждому альбому в переменной photos
        name_folder = f'backup_photos/{name_album}'
        user_YNDX.check_or_made_folder(name_folder) #создаем папку внутри backup_photos с названием альбома
        for photo in photos[name_album]: # проходим по каждому фото внутри альбома
            response = requests.get(photo['url'])
            user_YNDX.upload_photos(name_folder=name_folder, name_photos=photo['name_photo'], file_photo=response.content) # загружаем фото на яндекс диск