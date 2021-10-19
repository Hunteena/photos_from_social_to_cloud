from operator import itemgetter
from time import localtime, strftime
import requests
import json
from tqdm import tqdm


class Photos:
    def __init__(self, count=5, album='profile'):
        """
        Содержит информацию о фото для загрузки:
        count - требуемое количество фото (после получения из соцсети
        изменяется на фактическое);
        album - альбом (папка), откуда нужны фото;
        элемент списка items - словарь для фото с датой, количеством
        лайков, максимальным размером, ссылкой и именем файла для
        сохранения (количество лайков; если количество лайков одинаково
        у нескольких фото, то добавляет дату загрузки).
        """
        self.count = count
        self.album = album
        self.items = []

    def from_vk(self, vk_id, vk_token):
        """
        Заполняет self.items по запросу к альбому self.album пользователя
        с id vk_id.
        Изменяет self.count на количество полученных фото.
        """
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'album_id': self.album,
            'extended': 1,
            'photo_sizes': 1,
            'count': self.count,
            'access_token': vk_token,
            'v': '5.131'
        }
        if vk_id:
            params['owner_id'] = vk_id
        response = requests.get(url=url, params=params)
        if response.status_code != 200 or not response.json().get('response'):
            self.count = 0
            print('Не удалось получить фотографии')
            return

        for item in response.json()['response']['items']:
            max_size_pict = max(item['sizes'], key=itemgetter('type'))
            likes_count = item['likes']['count']
            photo_inf = {
                'likes': likes_count,
                'date': strftime("%d %b %Y %H%M%S", localtime(item['date'])),
                'size': max_size_pict['type'],
                'url': max_size_pict['url']
            }
            self.items.append(photo_inf)

        all_photos_likes_counts = list(map(itemgetter('likes'), self.items))
        for item in self.items:
            if all_photos_likes_counts.count(item['likes']) > 1:
                item['file_name'] = f'{str(item["likes"])} {item["date"]}.jpg'
            else:
                item['file_name'] = f'{str(item["likes"])}.jpg'

        self.count = len(self.items)
        print(f'Получено фотографий: {self.count}')

    def from_inst(self, inst_id, token):
        self.count = 0
        print('Загрузка фотографий с Instagram в разработке')

    def from_ok(self, ok_id, token):
        self.count = 0
        print('Загрузка фотографий с Одноклассников в разработке')

    def to_yadisk(self, token):
        """
        Загружает фото из self.items на Яндекс.Диск в новую папку.
        Во время загрузки показывает прогресс-бар.
        Список загруженных файлов сохраняет в json-файл.
        """
        if self.count == 0:
            print('Нет фотографий для загрузки')
            return

        photos_list = []
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {token}'
        }

        local_now = strftime("%d %b %Y %H%M%S", localtime())
        new_folder_name = f'{self.album} {local_now}'
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': new_folder_name}
        response = requests.put(url=url, params=params, headers=headers)
        if response.status_code == 201:
            print(f'Создана папка "{new_folder_name}"')
        else:
            print(f'Не удалось создать папку.',
                  f'Код ошибки {response.status_code}')
            return

        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        with tqdm(total=self.count, desc='Загрузка в облако') as pbar:
            for item in self.items:
                file_name = item['file_name']
                params = {
                    'path': f'{new_folder_name}/{file_name}',
                    'url': item['url']
                }
                response = requests.post(url=upload_url,
                                         params=params,
                                         headers=headers)
                if response.status_code != 202:
                    print(f'Не все фотографии сохранены.',
                          f'Код ошибки {response.status_code}')
                    break
                photos_list.append({
                    "file_name": file_name,
                    "size": item['size']
                })
                pbar.update(1)

        result_file_name = 'result.json'
        with open(result_file_name, 'w') as result_file:
            json.dump(photos_list, result_file, indent=4)
            print(f'Список сохранённых фотографий записан в',
                  f'{result_file_name}')

    def to_googledrive(self, token):
        ...
