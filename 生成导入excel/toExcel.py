import json
import uuid

import xlwt
from common.log import logger as log

from common.translate import translate


def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def paser():
    file = input("输入需要转换的json路径：")
    wb = xlwt.Workbook()
    sh1 = wb.add_sheet('文本')
    wb.add_sheet('模型')
    wb.add_sheet('字典')
    wb.add_sheet('应用菜单')
    wb.add_sheet('权限')
    wb.add_sheet('消息')

    sh1.write(0, 0, '原文本')
    sh1.write(0, 1, '翻译')

    with open(file) as f:
        j = f.read()


    j = json.loads(j)

    start = 1
    for t in j:
        for k,v in t.items():
            if not is_contains_chinese(k):
                sh1.write(start, 0, v)
                ts = translate({k: k},target_language='zh',source_language='en')
                sh1.write(start, 1, ts[k])
                start += 1
                continue
            sh1.write(start,0,v)
            sh1.write(start,1,k)
            start+=1

    file = f"""res-b2b-{str(uuid.uuid4()).replace("-","")}.xlsx"""
    log.info(f"生成：{file}")
    wb.save(f'/Users/youtiao/Documents/{file}')

paser()
