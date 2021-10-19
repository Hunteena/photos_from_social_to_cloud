from photos import Photos


def main():
    social = 'ВК'
    social_id = ...
    social_token = ...
    cloud = 'Яндекс.Диск'
    cloud_token = ...
    photos_count = 5
    album = 'profile'

    photos = Photos(photos_count, album)
    get_from = {
        'ВК': photos.from_vk,
        # 'Одноклассники': photos.from_ok,
        # 'Instagram': photos.from_inst
    }
    upload_to = {
        'Яндекс.Диск': photos.to_yadisk,
        # 'Google.Drive': photos.to_googledrive
    }

    get_from[social](social_id, social_token)
    upload_to[cloud](cloud_token)


if __name__ == '__main__':
    main()
