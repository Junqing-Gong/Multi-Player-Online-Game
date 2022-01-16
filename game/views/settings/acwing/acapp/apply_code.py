from django.http import JsonResponse
from urllib.parse import quote # 将特殊字符转为非特殊字符
from random import randint
from django.core.cache import cache

def get_state():
    res = ""
    for i in range(8):
        res += str(randint(0,9))
    return res


def apply_code(requset):
    appid = "250"
    redirect_uri = quote("https://app250.acapp.acwing.com.cn/settings/acwing/acapp/receive_code/")
    scope = "userinfo"
    state = get_state()

    cache.set(state, True, 7200) # 状态码值为true，有效期为两个小时

    return JsonResponse({
        'result': "success",
        'appid': appid,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': state,
    })
