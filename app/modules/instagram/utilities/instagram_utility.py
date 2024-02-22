from datetime import datetime
import requests
from typing import Union,Dict, Optional
import base64
from PIL import Image
from io import BytesIO

class InstagramUtility:
    
    @classmethod
    def get_expire_at(reason: str):
        if 'block will expire on' in reason or 'will be unavailable for you until' in reason:
            split_msg = 'block will expire on ' if 'block will expire on' in reason else 'will be unavailable for you until '
            expire_at_date = reason.split(split_msg)[1][:10] + ' 03:00'
            return datetime.strptime(expire_at_date, '%Y-%m-%d %H:%M')
        return None
    

    @classmethod
    def is_error_prevent_login(error: str) -> bool:
        message_error = error.lower()
        if 'ip_block' in message_error:
            return False
        return ('429' in message_error or
                'wait a few minutes' in message_error or
                'feedback' in message_error or
                'challenge' in message_error or
                'checkpoint' in message_error or
                'username you entered' in message_error or
                'been disabled' in message_error or
                'account was disabled' in message_error or
                'you requested to delete' in message_error or
                'account details were deleted' in message_error or
                'password' in message_error)
    
    @classmethod
    def is_error_session(error: str) -> bool:
        message_error = error.lower()
        return ('login_required' in message_error or
                'user_has_logged_out' in message_error or
                'not extract userid' in message_error)
    
    @classmethod
    def is_error_prevent_action(error: str) -> bool:
        message_error = error.lower()
        if 'ip_block' in message_error:
            return False
        return ('feedback' in message_error or
                'challenge' in message_error or
                'checkpoint' in message_error or
                'username you entered' in message_error or
                'been disabled' in message_error or
                'account was disabled' in message_error or
                'you requested to delete' in message_error or
                'account details were deleted' in message_error or
                'password' in message_error or
                'timed out' in message_error)
    

    @classmethod
    async def stream_image_to_base64(url: str, resize_options: Optional[Dict[str, Union[int, None]]] = None) -> str:
        try:
            image = requests.get('GET', url)
            image = await image.content
        except Exception as e:
            return 'data:image/jpeg;base64,/9j/4QAYRXhpZgAASUkqAAgAAAAAAAAAAAAAAP/sABFEdWNreQABAAQAAAA8AAD/4QMaaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLwA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/PiA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJBZG9iZSBYTVAgQ29yZSA1LjYtYzE0OCA3OS4xNjQwMzYsIDIwMTkvMDgvMTMtMDE6MDY6NTcgICAgICAgICI+IDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+IDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdFJlZj0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlUmVmIyIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOkI2QkU4MUQ5RTYxQTExRUQ4RUM3REEwQTAxQkI1MTAzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOkI2QkU4MUQ4RTYxQTExRUQ4RUM3REEwQTAxQkI1MTAzIiB4bXA6Q3JlYXRvclRvb2w9IkFkb2JlIFBob3Rvc2hvcCAyMDIwIFdpbmRvd3MiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0iODhEN0RGMDMyMjYyODZBREZDQUIyMjQwREE3RjZCOEUiIHN0UmVmOmRvY3VtZW50SUQ9Ijg4RDdERjAzMjI2Mjg2QURGQ0FCMjI0MERBN0Y2QjhFIi8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+/+4ADkFkb2JlAGTAAAAAAf/bAIQABgQEBAUEBgUFBgkGBQYJCwgGBggLDAoKCwoKDBAMDAwMDAwQ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'
        
        if resize_options:
            image = Image.open(BytesIO(image))
            width = resize_options.get('width', None)
            height = resize_options.get('height', None)
            quality = resize_options.get('quality', 80)
            
            if width and height:
                image = image.resize((width, height))
            elif width:
                ratio = width / float(image.size[0])
                height = int(float(image.size[1]) * ratio)
                image = image.resize((width, height), Image.ANTIALIAS)
            elif height:
                ratio = height / float(image.size[1])
                width = int(float(image.size[0]) * ratio)
                image = image.resize((width, height), Image.ANTIALIAS)
            
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=quality)
            image = buffered.getvalue()
        
        return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')
