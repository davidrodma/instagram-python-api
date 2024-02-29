from datetime import datetime
import requests
from typing import Union,Dict, Optional
import base64
from PIL import Image
from io import BytesIO

class InstagramUtility:
    
    @classmethod
    def get_expire_at(self,reason: str):
        if 'block will expire on' in reason or 'will be unavailable for you until' in reason:
            split_msg = 'block will expire on ' if 'block will expire on' in reason else 'will be unavailable for you until '
            expire_at_date = reason.split(split_msg)[1][:10] + ' 03:00'
            return datetime.strptime(expire_at_date, '%Y-%m-%d %H:%M')
        return None
    

    @classmethod
    def is_error_prevent_login(self,error: str) -> bool:
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
    def is_error_session(self,error: str) -> bool:
        message_error = error.lower()
        return ('login_required' in message_error or
                'user_has_logged_out' in message_error or
                'not extract userid' in message_error)
    
    @classmethod
    def is_error_prevent_action(self,error: str) -> bool:
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