# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import json
import os

from alibabacloud_alimt20181012 import models as alimt_20181012_models
from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from configparser import ConfigParser

from common.log import logger as log


def create_client(
        access_key_id: str,
        access_key_secret: str,
) -> alimt20181012Client:
    """
    使用AK&SK初始化账号Client
    @param access_key_id:
    @param access_key_secret:
    @return: Client
    @throws Exception
    """
    config = open_api_models.Config(
        # 您的AccessKey ID,
        access_key_id=access_key_id,
        # 您的AccessKey Secret,
        access_key_secret=access_key_secret
    )
    # 访问的域名
    config.endpoint = f'mt.cn-hangzhou.aliyuncs.com'
    return alimt20181012Client(config)

cfg = ConfigParser()
if os.getenv("translate")=="local":
    cfg.read('../config-local.ini')
else:
    cfg.read('../config.ini')
access_key_id = cfg.get('translate','access_key_id')
access_key_secret = cfg.get('translate','access_key_secret')

def translate(query,target_language='en',source_language='zh',):
    if not access_key_id or not access_key_secret:
        raise RuntimeError('翻译配置不能为空')
    client = create_client(access_key_id, access_key_secret)

    get_batch_translate_request = alimt_20181012_models.GetBatchTranslateRequest(
        api_type='translate_standard',
        source_text=json.dumps(query),
        format_type='text',
        target_language=target_language,
        source_language=source_language,
        scene='general'
    )
    # 复制代码运行请自行打印 API 的返回值
    res = client.get_batch_translate(get_batch_translate_request)

    log.info(res.body)
    result = {}
    for item in res.body.translated_list:
        result[item["index"]] = item["translated"]
    return result

if __name__ == "__main__":
    translate({"草":"草"})
