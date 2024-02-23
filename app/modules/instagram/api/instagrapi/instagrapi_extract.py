from instagrapi import Client
from flask import Flask
from app.modules.instagram.api.instagrapi.instagrapi_profile import InstagrapiProfile
from app.modules.profile.services.profile_service import ProfileService
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
import sys, os

app = Flask(__name__)

class InstagrapiExtract:
    
    profile_service = ProfileService()

    def __init__(self,api):
        self.api = api
        self.instagrapi_profile = InstagrapiProfile(api)

    def type_extract_by_port(self):
         port =  app.config.get('SERVER_PORT')
         switch = {
            5011: "extract",
            5012: "worker",
            5013: "boost",
         }
         return switch.get(port, "extract")
        

    async def login_extract(self):

        cl = Client()
        type = self.type_extract_by_port()
        if 'worker'==type:
            raise Exception("Not implement")
        elif 'boost'==type:
            raise Exception("Not implement")
        else:
            try:
                profile = self.profile_service.get_random_profile()
                cl = await self.instagrapi_profile.login(profile,True)
            except Exception as e:
                raise Exception(f"loginExtract->login: {e}")
        return cl
    
    async def user_info_extract(self,username:str = '', pk: str ='', noImage: bool = False) -> dict:
        try:
            print('userInfoType init', username or pk)
            success = False
            attempts = 3
            info = None
            type = self.type_extract_by_port()
            cl:Client = None
            while not success:
                try:
                    cl = await self.login_extract()
                    attempts -= 1
                    success = True
                    print("PEGAR")
                    info = self.api.get_user_info(cl, username, pk)
                    print("PEGOU",info)
                    if type=="worker":
                        pass
                    elif type=="boost":
                        pass
                    else:
                        print("CONTA")
                        self.profile_service.update_count(cl.username, 1, 'userInfo')
                        print("CONTOU")

                    if info and info.get('profile_pic_url') and not noImage:
                        info['image_base64'] = await InstagramUtility.stream_image_to_base64(info['profile_pic_url'], {'width': 150, 'height': 150})

                except Exception as err:
                    message_error = str(err)
                    await self.instagrapi_profile.error_handling(cl, message_error)
                    if attempts <= 0:
                        raise Exception(message_error)
                    success = False

            return info
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

            message_error = f'user_info_extract: {e}'
            print(message_error)
            raise Exception(message_error)
