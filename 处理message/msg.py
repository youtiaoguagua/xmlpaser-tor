import uuid

import javalang
from dbutils.pooled_db import PooledDB
import pymysql
from javalang.tree import Literal

from common.log import logger as log
from common import translate
from common.model import MsgModel
from pymysql.converters import escape_string


POOL = PooledDB(
    creator=pymysql,
    ping=0,
    host='10.107.27.140',
    port=3306,
    user='mysql',
    password='nQSumQujPY6IxHXa',
    database='trantor_gaia_app_b2b_mgmt',
    charset='utf8'
)

conn = POOL.connection()
cursor = conn.cursor(pymysql.cursors.DictCursor)


def paserJava(path):
    tree = javalang.parse.parse(open(path).read())
    packageName = tree.package.name
    className = tree.types[0].name

    res = []
    for item in tree.types[0].fields:
        fieldName = item.declarators[0].name
        fieldValue = item.declarators[0].initializer.value

        doc:str = item.documentation

        if doc:
            doc = doc.lstrip("/**").rstrip("/**").strip()
            doc = doc.split("*")[-1].strip()


        if item.type.name == "String":
            fieldValue = fieldValue.strip("\"")
        message_value = None
        for annotation in item.annotations:
            if annotation.name == "Message":
                if isinstance(annotation.element, Literal):
                    message_value = annotation.element.value
                else:
                    msg = list(filter(lambda t: t.name == 'value', annotation.element))[0]
                    message_value = msg.value.value
                message_value = message_value.strip("\"")
                break
        res.append(MsgModel(fieldName, fieldValue, message_value,doc))
    return packageName, className, res


def get_message(javaClassName, originalKey):
    sql = f"""
            select * from meta_store_management__versioned_message 
            where `javaClassName`='{escape_string(javaClassName)}' and originalKey='{escape_string(originalKey)}' and productVersion='2.4.4'
    """
    log.info(sql)
    cursor.execute(sql)
    t = cursor.fetchall()
    if len(t) == 0:
        return None
    return t[0]


def insert_language(fieldInfo, classInfo,projectId,fromProject,project='gaia',fromLanguage='603be97052c3d1ce0f8483b8fe02bd83'):

    if classInfo.doc is None:
        translation = translate.translate({classInfo.msgValue: classInfo.msgValue}, "zh", 'en')[classInfo.msgValue]
    else:
        translation = classInfo.doc

    sql = f"select * from meta_store_management__versioned_i18n_message where originalKey='{escape_string(fieldInfo['key'])}'"
    log.info(f"sql:{sql}")
    cursor.execute(sql)
    t = cursor.fetchall()
    if len(t) > 0:
        log.info("已经存在了翻译")
        return

    sql = f"""
        INSERT INTO trantor_gaia_app_b2b_mgmt.meta_store_management__versioned_i18n_message 
        (id, bizAppKey, version, _version, createdAt, updatedAt, translation, projectId, 
        tenantId, productVersion, digester, modificationType, `desc`, name, overrideAppKey, 
        originalKey, `key`, isDeleted, deletedAt, CreatedBy, FromLanguage, FromProject, 
        Message, DependencyProductVersion, UpdatedBy, FromTenant) VALUES 
        ('{str(uuid.uuid4()).replace("-", "")}', null, null, 1, now(), now(), 
        '{escape_string(translation)}', {projectId}, 2001, '2.4.4', null, null, '{escape_string(fieldInfo['content'])}', 
        '{escape_string(fieldInfo['originalKey'])}', null, '{escape_string(fieldInfo['key'])}', 
        '{project}_zh-CN_{escape_string(fieldInfo['key'])}', 0, 0, 1, '{fromLanguage}', {fromProject}, 
        '{escape_string(fieldInfo['id'])}', '{escape_string(fieldInfo['DependencyProductVersion'])}', 1, 2001);
        """
    log.info(f"sql:{sql}")
    cursor.execute(sql)
    conn.commit()


def main():
    # path = "/Users/youtiao/IdeaProjects/gaia/gaia-app-srm/srm-requisition-api/src/main/java/io/terminus/gaia/app/srm/requisition/msg/RequisitionExtMsg.java"
    path = input("请输入：")
    packageName, className, fieldData = paserJava(path)

    for item in fieldData:
        field_info = get_message(f"{packageName}.{className}", item.fieldValue)
        insert_language(field_info, item,1,1)


main()
