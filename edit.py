
from flask import Flask
from instagrapi import Client
cl = Client()
username = 'luizatanque'
password = 'robert7'
session = cl.load_settings(f"{username}.json")
cl.set_settings(session)
cl.login(username, password)
print("ACCOUNT_INFO",cl.account_info())
cl.dump_settings(f"{username}.json")

#EDIT USERNAME
#new_username = 'luizatanque'
#cl.account_edit(username=new_username,full_name="Lugar de Mulher")

#EDIT IMAGE PROFILE FROM URL
#media_pk = cl.media_pk_from_url('https://www.instagram.com/p/C2Db4KtPh24/')
#print("MEDIA_PK",media_pk)
#profile_pic_path = cl.photo_download(media_pk, folder='./tmp')
#cl.account_change_picture(profile_pic_path)

#EDIT IMAGE PROFILE FROM DIR
#cl.account_change_picture('./tmp/a.jpeg')

#UPLOAD POST
media = cl.photo_upload(
    "./tmp/b.jpg",
    "Test caption for photo with #hashtags and mention users such @example",
    extra_data={
        "custom_accessibility_caption": "alt text example",
        "like_and_view_counts_disabled": 1,
        "disable_comments": 1,
    }
)
