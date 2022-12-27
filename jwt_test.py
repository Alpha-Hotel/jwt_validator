import jwt
import datetime
import time

key = 'secret'
encoded = jwt.encode({"username":"Test", 'password':'my_pass','exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=5), 'iss':'Gov_Lambda'}, key, algorithm="HS256", headers={})

time.sleep(1)

print(jwt.decode(encoded, key, algorithms="HS256"))
print(jwt.get_unverified_header(encoded))

def validate_jwt(get_function):
    def wrapper(recieved_token):
        
        try:
            jwt.decode(encoded, key, algorithms="HS256")
            if recieved_token == encoded :
                return get_function(recieved_token)
            return 'not valid'
        except jwt.exceptions.ExpiredSignatureError:
            return 'expired'
    return wrapper

@validate_jwt
def get_request(token):
    return 'valid'

false_token = 'bad_actor'

print(f'The token { encoded } is {get_request(encoded)}')
print(f'The token {false_token} is {get_request(false_token)}')

time.sleep(5)

print(f'The token { encoded } is {get_request(encoded)}')
