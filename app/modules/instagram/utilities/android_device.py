from typing import List
import random
from datetime import datetime, timezone, timedelta
from devices import devices, builds

class AndroidDevice:
    def __init__(self):
        self.id = ''
        self.descriptor = ''
        self.uuid = ''
        self.familyId = ''
        self.phoneId = ''
        self.adid = ''
        self.build = ''
        self.language = 'en_US'
        self.appStartupCountry = None
        self.radioType = 'wifi-none'
        self.connectionType = 'WIFI'
        self.timezoneOffset = str(timezone(timedelta(hours=0)).utcoffset(datetime.now()).total_seconds())
        self.isLayoutRTL = False

    @property
    def batteryLevel(self) -> int:
        percent_time = random.randint(200, 600)
        return 100 - (int(datetime.now().timestamp()) // percent_time % 100)

    @property
    def isCharging(self) -> bool:
        return bool(random.randint(0, 1))

    @property
    def payload(self) -> dict:
        return {
            'android_version': self.details['android_version'],
            'android_release': self.details['android_release'],
            'manufacturer': self.details['manufacturer'],
            'model': self.details['model'],
        }

    @property
    def details(self) -> dict:
        device_parts = self.descriptor.split(';')
        android_version_1, android_release = device_parts[0].split('/')
        width, height = map(int, device_parts[2].split('x'))
        manufacturer, model = device_parts[3],device_parts[4]
        android_version = int(android_version_1)

        return {
            'android_version': android_version,
            'android_release': android_release,
            'manufacturer': manufacturer,
            'model': model,
            'viewport': {
                'width': width,
                'height': height,
            },
        }
    
    @property
    def settings(self) -> dict:
        details = self.details
        device_parts = self.descriptor.split(';')
        dpi, device, cpu = device_parts[1],device_parts[5],device_parts[6]
        android_version,android_release = details['android_version'],details['android_release']
        resolution = str(details['viewport']['width'])+"x"+str(details['viewport']['height'])
        payload = self.payload
        manufacturer = payload['manufacturer']
        model = payload['model']
        app_version = "269.0.0.18.75"
        version_code = "314665256"
        return {
            "app_version": app_version,
            "android_version": android_version,
            "android_release": android_release,
            "dpi": dpi,
            "resolution": resolution,
            "manufacturer": manufacturer,
            "device": device,
            "model": model,
            "cpu": cpu,
            "version_code":version_code
         }


    @staticmethod
    def generate(seed: str) -> 'AndroidDevice':
        random.seed(seed)  # Use a semente para geração de números aleatórios
        device = AndroidDevice()
        device.id = f'android-{random.randint(10000000, 99999999)}'
        device.descriptor = random.choice(devices)
        device.uuid = str(random.randint(10000000, 99999999))
        device.phoneId = str(random.randint(10000000, 99999999))
        device.adid = str(random.randint(10000000, 99999999))
        device.build = random.choice(builds)
        device.familyId = str(random.randint(10000000, 99999999))

        return device
    




# Exemplo de uso:
# device_seed = 'jauafdsa'
# device = AndroidDevice.generate(device_seed)
# print('device ',device.descriptor)
# print('payload',device.payload)
# print('batteryLevel',device.batteryLevel)
# print('isCharging',device.isCharging)
# print('details',device.details)
# print("build",device.build)
# print('id ',device.id)
# print('uuid ',device.uuid)
# print('phoneId ',device.phoneId)
# print('familyId ',device.familyId)
# print('settings ',device.settings)



