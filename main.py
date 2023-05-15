import json
import requests
import os
import argparse

'''
递归的进行处理，获取全国、省份、地市、区县的GEOJSON数据
对于全国、省份、地市的数据， 都存在两种：1. 只有轮廓； 2.包含全部子区域
WORKSPACE: 工作输出目录
url: 获取geojson数据的url地址
adcode: 区域编号
name: 区域名称
'''


def process(workspace, url, adcode, name):
    try:
        print('fetching: {}'.format(adcode))
        response = requests.get('{}{}'.format(url, adcode))
        if response.status_code == 200:
            geojson = json.loads(response.text)
            if name is None:
                name = geojson.get('features')[0].get('properties').get('name')
            path = os.sep.join([workspace, name])
            if not os.path.exists(path):
                os.makedirs(path)
            with open('{}{}{}.json'.format(path, os.sep, adcode), 'w') as f:
                json.dump(geojson, f, ensure_ascii=False)
            response = requests.get('{}{}_full'.format(url, adcode))
            if response.status_code == 200:
                geojson = json.loads(response.text)
                with open('{}{}{}_full.json'.format(path, os.sep, adcode), 'w') as f:
                    json.dump(geojson, f, ensure_ascii=False)
                features = geojson.get('features')
                for feature in features:
                    properties = feature.get('properties')
                    sub_name = properties.get('name')
                    sub_adcode = str(properties.get('adcode'))
                    process(path, url, sub_adcode, sub_name)
            elif response.status_code == 404:
                pass
        else:
            print('fail to fetch {}'.format(adcode))
    except:
        print('error')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, required=True, help='output path')
    parser.add_argument('--adcode', type=str, required=False, help='district\'s adcode, China is 100000')
    parser.add_argument('--adname', type=str, required=False, help='district\'s name')

    args = parser.parse_args()
    workspace = args.output
    adcode = args.adcode
    adname = args.adname

    if workspace[-1] == os.sep:
        workspace = workspace[0:-1]
    if adcode is None:
        adcode = '100000'

    url = 'https://geo.datav.aliyun.com/areas_v3/bound/geojson?code='
    process(workspace, url, adcode, adname)
    print('process completed!!!')


if __name__ == '__main__':
    main()