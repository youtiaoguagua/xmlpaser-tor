import json
import uuid

import pymysql
from dbutils.pooled_db import PooledDB
from common.log import logger as log
from pymysql.converters import escape_string
from configparser import ConfigParser

conn = pymysql.connect(
    host='10.107.27.140',
    port=3306,
    user='mysql',
    password='nQSumQujPY6IxHXa',
    database='trantor_gaia_app_b2b_mgmt',
    charset='utf8'
)

cursor = conn.cursor(pymysql.cursors.DictCursor)


def insert(depUUid, language, projectId, trans, text, project, version):
    sql = f"""
    select * from meta_store_management__versioned_i18n_view_text where text='{escape_string(text)}' and 
    projectId={projectId} and productVersion='{version}' and textAppKey='{project}'
    """
    cursor.execute(sql)
    t = cursor.fetchall()
    if len(t) > 0:
        return

    sql = """
    select max(`order`) od
            from meta_store_management__versioned_i18n_view_text;
    """
    cursor.execute(sql)
    t = cursor.fetchone()
    log.info(t)

    sql = f"""
        INSERT INTO meta_store_management__versioned_i18n_view_text 
        (id, textAppKey, bizAppKey, _version, `order`, text, createdAt, updatedAt, version, 
        translation, projectId, tenantId, productVersion, digester, modificationType, `desc`, 
        name, overrideAppKey, originalKey, `key`, isDeleted, deletedAt, FromTenant, DependencyProductVersion, 
        FromProject, FromLanguage, CreatedBy, UpdatedBy) VALUES 
        ('{str(uuid.uuid4()).replace("-", "")}', '{project}', null, 1, {int(t['od']) + 1}, '{escape_string(text)}', now(), 
        now(), null, '{escape_string(trans)}', {projectId}, 2001, '{version}', null, null, null, null, null, 
        '{str(uuid.uuid4()).replace("-", "")}', '{project}_zh-CN_{str(uuid.uuid4()).replace("-", "")}', 0, 0, 2001, 
        '{depUUid}', 1, '{language}', 1, 1);

    """
    log.info(sql)
    cursor.execute(sql)


cfg = ConfigParser()
cfg.read('../config.ini')
dependencyProductVersion = cfg.get('text', 'DependencyProductVersion')
fromLanguage = cfg.get('text', 'FromLanguage')
projectId = cfg.get('text', 'projectId')
textAppKey = cfg.get('text', 'textAppKey')
productVersion = cfg.get('text', 'productVersion')


def main():
    if not dependencyProductVersion or not fromLanguage or not projectId or not textAppKey or not productVersion:
        raise RuntimeError("text配置为空")
    file = input("输入：")
    with open(file) as f:
        j = f.read()
    j = json.loads(j)

    def solve(item):
        for trans, text in item.items():
            insert(dependencyProductVersion, fromLanguage, projectId, trans, text, textAppKey, productVersion)

    if isinstance(j, list):
        for item in j:
            solve(item)

    else:
        solve(j)


if __name__ == "__main__":
    main()
    conn.commit()
    conn.close()
