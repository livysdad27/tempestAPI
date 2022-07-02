from setup import ExtensionInstaller

def loader():
    return tempestAPIInstaller()

class tempestAPIInstaller(ExtensionInstaller):
    def __init__(self):
        super(tempestAPIInstaller, self).__init__(
            version=".7",
            name='tempestAPI',
            description='Weatherflow Tempest API installer',
            author="Billy Jackson",
            author_email="livysdad27@gmail.com",
            files=[('bin/user', ['bin/user/tempestAPI.py'])],
            config={
                'tempestAPI': {
                    'driver' : 'bin.user.tempestAPI',
                    'personal_token': 'your_api_token',
                    'tempest_device_id': 'your_tempest_device_id',
                    'tempest_rest_endpoint': 'https://swd.weatherflow.com/swd/rest/observations/device/',                        
                    'rest_sleep_interval': '20'
                },
            }
        )