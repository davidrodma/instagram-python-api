from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    SelectContactPointRecoveryForm, RecaptchaChallengeForm,
    FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
)


def json_value():
    return ''

class InstagrapiChallenge:

    @classmethod
    def detect_name_challenge(self,e):
        name =''
        if isinstance(e, BadPassword):
            name ='BadPassword'
        elif isinstance(e, LoginRequired):
            name ='LoginRequired'
        elif isinstance(e, ChallengeRequired):
            #if isinstance(e, SelectContactPointRecoveryForm):
            #    name ='SelectContactPointRecoveryForm'
            if isinstance(e, RecaptchaChallengeForm):
                name ='RecaptchaChallengeForm'
            return 'ChallengeRequired'
        elif isinstance(e, FeedbackRequired):
            name ='FeedbackRequired'
        elif isinstance(e, PleaseWaitFewMinutes):
            name ='PleaseWaitFewMinutes'
        else:
            name =''

        return name
    
    def handle_exception(self,client:Client, e):
        if isinstance(e, BadPassword):
            client.logger.exception(e)
            client.set_proxy(self.next_proxy().href)
            if client.relogin_attempt > 0:
                self.freeze(str(e), days=7)
                raise ReloginAttemptExceeded(e)
            client.settings = self.rebuild_client_settings()
            return self.update_client_settings(client.get_settings())
        elif isinstance(e, LoginRequired):
            client.logger.exception(e)
            client.relogin()
            return self.update_client_settings(client.get_settings())
        elif isinstance(e, ChallengeRequired):
            api_path = json_value(client.last_json, "challenge", "api_path")
            if api_path == "/challenge/":
                client.set_proxy(self.next_proxy().href)
                client.settings = self.rebuild_client_settings()
            else:
                try:
                    client.challenge_resolve(client.last_json)
                except ChallengeRequired as e:
                    self.freeze('Manual Challenge Required', days=2)
                    raise e
                except (ChallengeRequired, SelectContactPointRecoveryForm, RecaptchaChallengeForm) as e:
                    self.freeze(str(e), days=4)
                    raise e
                self.update_client_settings(client.get_settings())
            return True
        elif isinstance(e, FeedbackRequired):
            message = client.last_json["feedback_message"]
            if "This action was blocked. Please try again later" in message:
                self.freeze(message, hours=12)
                # client.settings = self.rebuild_client_settings()
                # return self.update_client_settings(client.get_settings())
            elif "We restrict certain activity to protect our community" in message:
                # 6 hours is not enough
                self.freeze(message, hours=12)
            elif "Your account has been temporarily blocked" in message:
                """
                Based on previous use of this feature, your account has been temporarily
                blocked from taking this action.
                This block will expire on 2020-03-27.
                """
                self.freeze(message)
        elif isinstance(e, PleaseWaitFewMinutes):
            self.freeze(str(e), hours=1)
        raise e
    
    def next_proxy():
        return {'href':''}
    
    def freeze(error:str,days:int):
        pass

    def rebuild_client_settings():
        pass
    
    def update_client_settings():
        pass