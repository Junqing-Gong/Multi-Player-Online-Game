from django.http import HttpResponse

def gyr(request):
    line1 = '<img src="">'
    return HttpResponse(line1)

def index(request):
    line1 = '<h1 style="text-align: center">术士之战</h1>'
    line4 = '<a href="/play/">进入游戏</a>'
    # line3 = '<hr>'
    line2 = '<img src="https://tse1-mm.cn.bing.net/th/id/R-C.0f2134e0c473b4b2919959eb65771f4b?rik=NYwPb74Bu8Ar1g&riu=http%3a%2f%2f222.186.12.239%3a10010%2fJK_20190514%2f001.jpg&ehk=5Cwn5vwG%2fYbQo8ApwvTUxwNKztEsCbIGq17gonVdp7U%3d&risl=&pid=ImgRaw&r=0">'
    return HttpResponse(line1 + line4 + line2)

def play(request):
    line1 = '<h1 style="text-align: center">游戏界面</h1>'
    line3 = '<a href="/">返回主界面</a>'
    line2 = '<img src="https://tse1-mm.cn.bing.net/th/id/R-C.c35c2f9985e7865faa84776404a49c37?rik=ZfF5mh1KGKku5Q&riu=http%3a%2f%2fimg.mm4000.com%2ffile%2f6%2fec%2fe7bd8c7d3e.jpg&ehk=Ps0LEFNiVKFapAXOPeTZxFdFfrqAdvmwQlmdEE4kOV4%3d&risl=&pid=ImgRaw&r=0">'
    return HttpResponse(line1 + line3 + line2)
