import re
import requests
from config import Config


def login():
    url = 'https://api.weibo.cn/2/account/login_sendcode'
    phone = input('请输入手机号：')
    data = {'phone': phone}
    response = requests.post(url=url, data=data)
    try:
        print(response.json()['msg'])
    except:
        print(response.json()['errmsg'])
        exit()
    url = 'https://api.weibo.cn/2/account/login'
    while True:
        smscode = input('请输入验证码：')
        data['smscode'] = smscode
        response = requests.post(url=url, data=data)
        if 'errmsg' in response.json():
            print(response.json()['errmsg'])
            continue
        name = response.json()['screen_name']
        gsid = response.json()['gsid']
        break
    return name, gsid


def sign(gsid):
    info_list = []
    since_id = ''
    url = f'http://api.weibo.cn/2/cardlist?c=android&s=68998320&from=10A3295010&gsid={gsid}&containerid=100803_-_followsuper'
    req = requests.Session()
    s = 0
    while True:
        url = url + '&since_id=' + since_id
        # 获取超话列表
        response = req.get(url)
        card_group = response.json()['cards'][0]['card_group']
        for i in range(len(card_group)):
            if card_group[i]['card_type'] == '8':
                info = {}
                print('*' * 50)
                # 超话名
                title_sub = card_group[i]['title_sub']
                # 超话等级
                lv = card_group[i]['desc1']
                # 超话信息
                desc = card_group[i]['desc2'].strip()
                # 去掉多余换行符
                desc = '\n'.join([i for i in desc.split('\n') if i != ''])
                # 超话签到信息
                sign_info = card_group[i]['buttons'][0]['name']
                # 超话id
                containerid = card_group[i]['scheme'].split('&')[0].split('=')[1]
                if sign_info == '签到':
                    sign_info = '未签到'
                info['title_sub'] = title_sub
                info['lv'] = int(re.findall('\d+', lv)[0])
                info['desc'] = desc
                info['sign_info'] = sign_info
                info['containerid'] = containerid
                print(title_sub)
                print(lv)
                if desc != '':
                    print(desc)
                print(sign_info)
                info_list.append(info)
                s += 1
        # 获取下一页id
        since_id = response.json()['cardlistInfo']['since_id']
        # 获取到空就是爬取完了
        if since_id == '':
            break
    # 按等级从大到小排序超话
    info_list.sort(key=lambda keys: keys['lv'], reverse=True)
    print('*' * 50)
    print('爬取完毕共%d个超话' % s)
    print('*' * 50)
    s = 0
    for i, info in enumerate(info_list):
        i += 1
        if info['sign_info'] == '未签到':
            print(f"正在签到第{i}个\"{info['title_sub']}\" 等级LV.{info['lv']}")

            # 打开超话
            r = req.get(
                url=f'https://api.weibo.cn/2/page?c=android&s=68998320&from=10A3295010&gsid={gsid}&containerid=' + info[
                    'containerid'])

            # 签到
            r = req.get(url='https://api.weibo.cn' + r.json()['pageInfo']['right_button']['params'][
                'action'] + f'&c=android&s=68998320&ua=HUAWEI-HUAWEI%20MLA-AL10__weibo__10.3.2__android__android5.1.1&v_p=82&from=10A3295010&gsid={gsid}&cum=AAAAAAAA')

            # 获取签到信息
            request_url = r.json()['scheme'].split('?')[1]
            r = req.get(
                f'https://api.weibo.cn/2/page/panel?c=android&s=68998320&from=10A3295010&gsid={gsid}&cum=AAAAAAAA&' + request_url)
            s += 1

            # 打印签到信息
            print(''.join(re.findall('<.*?>(.*?)</.*?>', r.json()['panel_list'][2]['text'])))
            print(''.join(re.findall('<.*?>(.*?)</.*?>', r.json()['panel_list'][3]['text'])))
            print('*' * 50)
    if s == 0:
        print('今天你已经全部签到')
    else:
        print('签到完毕，共签到成功%d个' % s)


if __name__ == '__main__':
    cf = Config('config.ini', '配置')
    gsid = cf.GetStr('配置', 'gsid')
    name = cf.GetStr('配置', 'name')
    if gsid == '':
        name, gsid = login()
        print('登录成功')
        cf.Add('超话签到', 'gsid', gsid)
        cf.Add('超话签到', 'name', name)
    print('用户名：' + name)
    print('gsid：' + gsid)
    sign(gsid)