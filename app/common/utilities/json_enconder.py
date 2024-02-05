import json
from bson.objectid import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, object):
            # Convertendo o ObjectId para string
            obj_dict = obj.__dict__.copy()
            if isinstance(obj_dict.get('_id'), ObjectId):
                obj_dict['_id'] = str(obj_dict['_id'])
            return obj_dict
        return super().default(obj)
