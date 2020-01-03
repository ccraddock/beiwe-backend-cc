import base64
from Crypto.Cipher import AES
from libs.client_key_management import get_client_private_key
user = some_user
private_key = get_client_private_key(user._id, user['study_id'])


x = some_file_contents
b64_key = x.pop(0)
decrypted_key = base64.urlsafe_b64decode(private_key.decrypt(b64_key))

for y in x.splitlines():
    ivs, ds = y.split(":")
    #print iv, d
    iv = base64.urlsafe_b64decode(ivs)
    d = base64.urlsafe_b64decode(ds)
    #print ivs, ds
    #print len(iv), len(d)
    print AES.new(decrypted_key, mode=AES.MODE_CBC, IV=iv).decrypt(d).encode("string_escape")
