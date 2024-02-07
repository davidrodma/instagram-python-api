import traceback
import json
from flask import jsonify, request
from app.common.utilities.json_enconder import JSONEncoder
from pydantic import ValidationError

class ExceptionUtility:

    @classmethod
    def catch(self,e:Exception,pretext="",complete=False):
        # Capturando a exceção do sistema
        error_type = type(e).__name__
        error_message = str(e)
        traceback_info = traceback.format_exc()

        # Criando um JSON de erro com informações detalhadas
        error_data = {
            "error": f"{pretext}: {error_message}" 
        }
        if complete:
            return error_data | {
                "type": error_type,
                "message": error_message,
                "traceback": traceback_info
            }
        return error_data
    
    @classmethod
    def catch_json_dumps(self,e: Exception,pretext=""):
        return json.dumps(self.catch(e,pretext))
    
    @classmethod
    def catch_response(self,e: Exception,pretext="",complete=False):
        return JSONEncoder().encode(self.catch(e,pretext,complete)), 400
    
    @classmethod
    def catch_response_validation(self,e:ValidationError):
        return jsonify({'error': f"Error Validation: {e}",'errors':e.errors(), 'error_count':e.error_count()}), 422
    
    @classmethod
    def base_exception(self,e: Exception,pretext=""):
        return JSONEncoder().encode(self.catch(e,pretext)), 400