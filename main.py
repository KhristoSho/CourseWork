import requests, json
from progress.bar import Bar
from base import VKphotos, YNDXdisk
from apikeys import TOKEN_VK, TOKEN_YNDX
from pprint import pprint

def backup_photos(iduser_vk: str, token_yndx: str, album=False, number_photos=5):

    info = []

    userVK = VKphotos(iduser_vk, TOKEN_VK)
    diskYNDX = YNDXdisk(TOKEN_YNDX)

    if album:
        albums = userVK.get_albums()
        list_photos = userVK.get_photos(albums)
    else:
        list_photos = userVK.get_photos()
    
    diskYNDX.check_or_made_folder('backup_photos')

    for album in list_photos.keys():
        name_folder = f'backup_photos/{album}'
        diskYNDX.check_or_made_folder(name_folder=name_folder)
        bar = Bar(f'Download photo from "{album}" to YandexDisk', max=(len(list_photos[album]) if len(list_photos[album]) <= number_photos else number_photos))
        for n, photo in enumerate(list_photos[album], 1):
            if n > number_photos:
                break
            response = requests.get(photo['url'])
            diskYNDX.upload_photos(
                name_folder=name_folder,
                name_photos=photo['name_photo'],
                file_photo=response.content
            )
            info.append({
                'folder': name_folder,
                'file_name': photo['name_photo'],
                'size': photo['size']
            })
            bar.next()
        bar.finish()
    info = json.dumps(info)
    return info


if __name__ == '__main__':
    id = ''
    backup_photos(id, TOKEN_YNDX, number_photos=10)
    backup_photos(id, TOKEN_YNDX, album=True, number_photos=10)