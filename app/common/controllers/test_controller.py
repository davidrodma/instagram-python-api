

from flask import jsonify, request
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.profile.models.profile import Profile
from app.common.utilities.logging_utility import LoggingUtility
from app.common.utilities.exception_utility import ExceptionUtility
from app.database.repositories.mongo_repository import MongoRepository
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
logger = LoggingUtility.get_logger("Test")

class TestController():
    
   @staticmethod
   def my_test():
      return TestController.test()

   def test():
      try:
         likers = [
                        {
                           "pk": 10423549810,
                           "pk_id": "10423549810",
                           "username": "diego_.plata",
                           "full_name": "Diego Plata",
                           "is_private": True,
                           "strong_id__": "10423549810",
                           "is_verified": False,
                           "profile_pic_id": "3308119784989328869_10423549810",
                           "profile_pic_url": "https://scontent-iad3-1.cdninstagram.com/v/t51.2885-19/409092813_381600124654772_7690515985687596573_n.jpg?stp=dst-jpg_e0_s150x150&_nc_ht=scontent-iad3-1.cdninstagram.com&_nc_cat=108&_nc_ohc=3krZVW-cMN4AX_GcmCu&edm=APwHDrQBAAAA&ccb=7-5&oh=00_AfAHD3iv6Ps1gnBY99DyYK2soukoy7-OzXU0WpeyuMlOjg&oe=65E7C8C4&_nc_sid=8809c9",
                           "account_badges": [],
                           "latest_reel_media": 0
                        },
                        {
                           "pk": 328410236,
                           "pk_id": "328410236",
                           "username": "im.alexm_",
                           "full_name": "Alex Mor",
                           "is_private": True,
                           "strong_id__": "328410236",
                           "is_verified": False,
                           "profile_pic_id": "3311398643830363221_328410236",
                           "profile_pic_url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-19/429888910_288006927443430_8896239589949599291_n.jpg?stp=dst-jpg_e0_s150x150&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=106&_nc_ohc=I5m5NKSa48wAX9bKKm0&edm=APwHDrQBAAAA&ccb=7-5&oh=00_AfB-x7xG96swqfk4moc3HY24aoa5jE9c1H5l5K-OSAMzKg&oe=65E7F102&_nc_sid=8809c9",
                           "account_badges": [],
                           "latest_reel_media": 0
                        },
                        {
                           "pk": 55925512,
                           "pk_id": "55925512",
                           "username": "cuzita",
                           "full_name": "Erika Alva",
                           "is_private": True,
                           "strong_id__": "55925512",
                           "is_verified": False,
                           "profile_pic_id": "3262526822716809073_55925512",
                           "profile_pic_url": "https://scontent-iad3-2.cdninstagram.com/v/t51.2885-19/412072063_372943895126703_6638342273034059074_n.jpg?stp=dst-jpg_e0_s150x150&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_cat=103&_nc_ohc=aLXlEL8q0EAAX-VFjyW&edm=APwHDrQBAAAA&ccb=7-5&oh=00_AfCA16Ls-u7D8qBNz0YDmR2PsRHtRnx1N-f_2n4ALdWMPg&oe=65E81880&_nc_sid=8809c9",
                           "account_badges": [],
                           "latest_reel_media": 0
                        }
                     ]
         data = request.get_json()
         pk= data.get('media_id')
         ids_likers_action= data.get('ids_likers_action')
         total = len(likers)
         ids_likers_action = [ids_likers_action] if isinstance(ids_likers_action, str) or isinstance(ids_likers_action, int) else ids_likers_action
         ids_likers_action = [str(id) for id in ids_likers_action]
         filtered = [user for user in likers if str(user.get('pk')) in ids_likers_action]
         results = []
         for id in ids_likers_action:
               data = [user for user in filtered if str(user.get('pk')) == id]
               is_liker = True if data else False
               
               username = data[0].get('username') if is_liker else ''
               username_action = username if is_liker else ''
               image_action = data[0].get('profile_pic_url') if is_liker else ''
               is_liker = True if total >= 1000 else is_liker
               if is_liker:
                  logger.info(f"{id} liked in {pk} in {total} likers")
               else:
                  logger.error(f"{id} not liked in {pk} in {total} likers")
               results.append({'username': username, 'id': str(id), 'is_liker': is_liker})
         return jsonify({'media_id': pk, 'username_action': username_action, 'image_action': image_action, 'likers': results, 'total': total})
      except Exception as e:
            message_error = f'ERRO 2: {e}'
            print(message_error)
            return ExceptionUtility.catch_response(message_error,'Error Test')
        