#!/usr/bin/python3
# encoding=utf-8

import urllib.request, json, time

UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'

def cookie_dict_to_str(**cookie):
    return '; '.join(map('='.join, cookie.items()))

def cookie_str_to_dict(cookie):
    return dict(map(lambda s: s.partition('=')[::2], cookie.split('; ')))

def make_url(url, order=None, **args):
    if not order:
        order = args
    return url + '?' + '&'.join(map(lambda k: k+'=%s'%args[k], order))

def make_g_tk(p_skey, __cache={}, **cookie):
    if p_skey in __cache:
        return __cache[p_skey]
    tk = 5381
    for c in p_skey:
        tk += (tk<<5) + ord(c)
    tk &= 0x7fffffff
    __cache[p_skey] = tk
    return tk

class NotLoadedType:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # 初始化单例状态
            cls._is_loaded = False
        return cls._instance

    def __bool__(self):
        return False

    def __repr__(self):
        return "<NotLoaded>"

NotLoaded = NotLoadedType()  # 最终单例

class Media:
    '''图片或视频'''
    def __init__(self, url, video_url=None):
        self.url = url
        self.video_url = video_url
        self.type = 'Video' if video_url else 'Image'
        if url.startswith('http://p.qpimg.cn/cgi-bin/cgi_imgproxy?'):
            self.url = url[url.find('url=')+4:]

    def open(self):
        req = urllib.request.Request(self.url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
        return urllib.request.urlopen(req)

    def open_video(self):
        if self.type != 'Video':
            raise TypeError('不是视频')
        req = urllib.request.Request(self.video_url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
        try:
            return urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            raise ValueError(f'错误：{e.code}')
        except urllib.error.URLError as e:
            raise ValueError(f'错误：{e.reason}')

    def __str__(self):
        return f'<{self.type}>'

class Comment:
    '''评论'''
    def __init__(self, data):
        self.author_uin = data['uin']  # 存储评论者QQ号
        self.space_accessible = None   # 初始化为未知
        self.parse(data)
        
        
    def check_space_access(self, qzone_obj):
        """检测评论者的空间是否可访问"""
        self.space_accessible = qzone_obj.check_space_accessible(self.author_uin)
        return self.space_accessible
    
    def parse(self, data):
        self.content = data['content']
        self.ctime = data['create_time']
        self.nickname = data['name']
        self.tid = data['tid']
        self.author = data['uin']
        self.replys = []
        if 'list_3' in data and data['list_3']:
            for r in data['list_3']:
                self.replys.append(Comment(r))
        self.pictures = []
        if 'rich_info' in data and data['rich_info']:
            for p in data['rich_info']:
                self.pictures.append(Media(p['burl']))
        self.videos = []  # 新增视频列表
        if 'video' in data and data['video']:
            self.videos = [Media(v['url1'], v['url3']) for v in data['video']]

    def __str__(self):
        s = '%s: %s%s' % (self.nickname, ''.join(map(str, self.pictures)), self.content)
        if self.replys:
            s += '\n| ' + '\n| '.join(map(str, self.replys))
        return s

class Emotion:
    '''说说

    这个类的部分属性值可能是NotLoaded，列表类型的属性值中也可能包含NotLoaded，表示相关信息必须进一步发送请求才能载入。调用load()方法可完全载入所有信息。'''
    def __init__(self, data):
        self.parse(data)

    def parse(self, data):
        '''解析各种信息

        目前支持的信息如下：
            comments
            shortcon
            content
            ctime
            forwardn
            location
            nickname
            pictures
            origin
            forwards
            source
            tid
            author
            like
        '''
        # comments
        if 'commentlist' in data and data['commentlist']:
            self.comments = list(map(Comment, data['commentlist']))
        else:
            self.comments = []
        # shortcon
        self.shortcon = data['content']
        # content
        if 'has_more_con' in data and data['has_more_con']:
            self.content = NotLoaded
        else:
            self.content = data['content']
        # ctime
        self.ctime = data['created_time']
        # forwardn
        self.forwardn = data['fwdnum']
        # location
        if 'lbs' in data:
            self.location = data['lbs']
        else:
            self.location = NotLoaded
        # nickname
        self.nickname = data['name']
        # pictures
        self.pictures = []
        if 'pictotal' in data and data['pictotal']:
            for pic in data['pic']:
                if 'video_info' in pic:
                    self.pictures.append(Media(pic['url1'], pic['video_info']['url3']))
                else:
                    self.pictures.append(Media(pic['url1']))
            self.pictures += [NotLoaded] * (data['pictotal'] - len(self.pictures))
        # videos
        if data.get('video'):
            self.pictures += list(map(lambda i: Media(i['url1'], i['url3']), data['video']))
        # origin
        if 'rt_con' in data and data['rt_tid']:
            odata = dict(commentlist=[], content=data['rt_con']['content'], created_time=NotLoaded, name=data['rt_uinname'])
            for k in data:
                if k.startswith('rt_'):
                    odata[k[3:]] = data[k]
            self.origin = Emotion(odata)
        else:
            self.origin = None
        # forwards
        if 'rtlist' in data and data['rtlist']:
            self.forwards = []
            for f in data['rtlist']:
                if 'con' not in f:
                    f['con'] = f['content']
                odata = dict(content=f['con'], has_more_con=1, created_time=NotLoaded, fwdnum=NotLoaded)
                for k in f:
                    odata[k] = f[k]
                self.forwards.append(Emotion(odata))
        # source
        self.source = data['source_name']
        # tid
        self.tid = data['tid']
        # author
        self.author = data['uin']
        # like
        if '__like' in data:
            self.like = {}
            for i in data['__like']:
                self.like[i['fuin']] = (i['nick'], Media(i['portrait']))
        else:
            self.like = NotLoaded

    def load(self):
        '''完全载入一条说说的所有信息'''
        url = make_url('https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msgdetail_v6',
                uin = self.author,
                tid = self.tid,
                num = 20,
                pos = 0,
                g_tk = make_g_tk(**qzone_cookie),
                not_trunc_con = 1)
        req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
        with urllib.request.urlopen(req) as http:
            s = http.read().decode(errors='surrogateescape')
        data = json.loads(s[s.find('(')+1 : s.rfind(')')])
        for i in range(20, len(self.comments), 20):
            if len(data['commentlist']) != 20 * i:
                break
            url = make_url('https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msgdetail_v6',
                    uin = self.author,
                    tid = self.tid,
                    num = 20,
                    pos = i,
                    g_tk = make_g_tk(**qzone_cookie),
                    not_trunc_con = 1)
            req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
            with urllib.request.urlopen(req) as http:
                s = http.read().decode(errors='surrogateescape')
            data['commentlist'] += json.loads(s[s.find('(')+1 : s.rfind(')')])['commentlist']
        url = make_url('https://users.qzone.qq.com/cgi-bin/likes/get_like_list_app',
                uin = int(qzone_cookie['uin'].strip('o')),
                unikey = 'http%%3A%%2F%%2Fuser.qzone.qq.com%%2F%s%%2Fmood%%2F%s' % (self.author, self.tid),
                begin_uin = 0,
                query_count = 999999,
                if_first_page = 1,
                g_tk = make_g_tk(**qzone_cookie))
        req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
        with urllib.request.urlopen(req) as http:
            s = http.read().decode(errors='surrogateescape')
        like = json.loads(s[s.find('(')+1 : s.rfind(')')])
        data['__like'] = like['data']['like_uin_info']
        self.parse(data)
        if self.pictures:
            url = make_url('https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_get_pics_v6',
                    uin = self.author,
                    tid = self.tid,
                    g_tk = make_g_tk(**qzone_cookie))
            req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
            with urllib.request.urlopen(req) as http:
                s = http.read().decode(errors='surrogateescape')
            pictures = json.loads(s[s.find('(')+1 : s.rfind(')')])
            self.pictures = [pic for pic in self.pictures if pic]
            urls = {pic.url for pic in self.pictures}
            image_urls = pictures.get('imageUrls', [])  # 如果不存在则返回空列表
            # 兼容旧版图片字段（如果有）
            if not image_urls and 'pic' in pictures:
                image_urls = [pic['url'] for pic in pictures['pic'] if 'url' in pic]
            self.pictures += [Media(url) for url in image_urls if url not in urls]

    def __str__(self):
        s = self.nickname
        if self.ctime:
            s += ' ' + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.ctime))
        if self.location and self.location['name']:
            s += ' from %s' % self.location['name']
        if self.source:
            s += ' via %s' % self.source
        s += '\n'
        s += ''.join(map(str, self.pictures))
        if self.content:
            s += self.content
        else:
            s += self.shortcon + ' ...'
        s += '\n'
        if self.origin:
            s += '| ' + '\n| '.join(str(self.origin).splitlines()) + '\n'
        if self.like:
            s += '%s likes   ' % len(self.like)
        s += '%s forwards   %s comments\n' % (self.forwardn, len(self.comments))
        s += '\n'.join(map(str, filter(None, self.comments)))
        return s

class Qzone:
    def __init__(self, **cookie):
        global qzone_cookie
        qzone_cookie = cookie
        
        
    def get_likers(self, emotion):
        """获取一条说说的点赞用户列表（返回QQ号列表）"""
        likers = []
        if emotion.like != NotLoaded:
            likers = list(emotion.like.keys())  # 提取点赞者的QQ号
        return likers

    def get_forwarders(self, emotion):
        """获取一条说说的转发用户列表（返回QQ号列表）"""
        forwarders = []
        if hasattr(emotion, 'forwards') and emotion.forwards:
            for forward in emotion.forwards:
                if forward.author != NotLoaded:
                    forwarders.append(forward.author)  # 提取转发者的QQ号
        return forwarders

    def check_space_accessible(self, target_uin):
        """检测目标用户空间是否可访问（非好友/私密空间会返回False）"""
        try:
            # 尝试访问空间主页（不需要完整爬取，只需检查HTTP状态码或返回内容）
            url = f"https://user.qzone.qq.com/{target_uin}"
            req = urllib.request.Request(url, headers={
                'Cookie': cookie_dict_to_str(**qzone_cookie),
                'User-Agent': UA
            })
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8', errors='ignore')
                # 判断是否被拦截（如出现"权限不足"或"主人设置了权限"）
                if "抱歉，主人设置了权限" in html or "没有权限" in html:
                    return False
                return True
        except urllib.error.HTTPError as e:
            if e.code == 403 or e.code == 404:
                return False
            raise
    
    def emotion_list_raw(self, uin, num=20, pos=0, ftype=0, sort=0, replynum=100,
            code_version=1, need_private_comment=1):
        '''获取一个用户的说说列表，返回经过json解析的原始数据'''
        url = make_url('https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6',
                uin = uin,
                ftype = ftype,
                sort = sort,
                pos = pos,
                num = num,
                replynum = replynum,
                g_tk = make_g_tk(**qzone_cookie),
                callback = '_preloadCallback',
                code_version = code_version,
                format = 'jsonp',
                need_private_comment = need_private_comment)
        req = urllib.request.Request(url, headers={'Cookie': cookie_dict_to_str(**qzone_cookie), 'User-Agent': UA})
        with urllib.request.urlopen(req) as http:
            s = http.read().decode(errors='surrogateescape')
        return json.loads(s[s.find('(')+1 : s.rfind(')')])

    def emotion_list(self, uin, num=20, pos=0, ftype=0, sort=0, replynum=100,
            code_version=1, need_private_comment=1):
        '''获取一个用户的说说列表，返回Emotion对象列表'''
        response = self.emotion_list_raw(uin, num, pos, ftype, sort, replynum, code_version, need_private_comment)
        if 'msglist' not in response:
            error_code = response.get('code', response.get('retcode', '未知'))
            error_msg = response.get('message', response.get('msg', '无错误信息'))
            print(f"API响应异常 [代码{error_code}] {error_msg}")
            return None
        l = response['msglist']
        return list(map(Emotion, l if l else []))