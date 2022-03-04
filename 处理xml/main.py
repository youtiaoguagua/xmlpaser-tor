import json
import os

from bs4 import BeautifulSoup
from bs4.element import Comment

from common.log import logger as log
from common import translate

translation = {}


def isChinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def soup_prettify2(soup, desired_indent):
    pretty_soup = str()
    previous_indent = 0
    for line in soup.prettify().split("\n"):
        current_indent = str(line).find("<")
        if current_indent == -1 or current_indent > previous_indent + 2:
            current_indent = previous_indent + 1
        previous_indent = current_indent
        pretty_soup += write_new_line(line, current_indent, desired_indent)
    pretty_soup = pretty_soup.replace("%3D%3E", "=>")
    pretty_soup = pretty_soup.replace("atatat", "@")
    return pretty_soup


def write_new_line(line, current_indent, desired_indent):
    new_line = ""
    spaces_to_add = (current_indent * desired_indent) - current_indent
    if spaces_to_add > 0:
        for i in range(spaces_to_add):
            new_line += " "
    new_line += str(line) + "\n"
    return new_line


def parser(path):
    xml = open(path).read()
    xml = xml.replace("=>", "%3D%3E")
    xml = xml.replace("@", "atatat")
    soup = BeautifulSoup(xml, "xml")

    view = soup.find("View")

    xsiNo = "https://trantor-docs-dev.app.terminus.io/static/v0.18.x/schema/base.xsd"
    if not view.has_attr("xsi:noNamespaceSchemaLocation") or view['xsi:noNamespaceSchemaLocation'] != xsiNo:
        view['xsi:noNamespaceSchemaLocation'] = xsiNo

    if not view.has_attr("xmlns:xsi"):
        view['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"

    #  处理title
    titles = soup.findAll(lambda attr: attr.has_attr('title') and isChinese(attr['title']))

    need_translate = {}
    for item in titles:
        t = item['title']
        if t == "" or t == None or "i18n" in t:
            continue
        need_translate[t] = t

    trans = (translate.translate(need_translate) if len(need_translate) else {})

    for item in titles:
        t = item['title']
        if t == "" or t == None or "i18n" in t:
            continue
        item.insert_before(Comment(f"title={t}"))
        item.insert_before("\n")
        translation[t] = trans[t]
        item["title"] = f"#{{i18n.get('{trans[t]}').d('{trans[t]}')}}"

    #  处理message
    messages = soup.findAll(lambda attr: attr.has_attr('message') and isChinese(attr['message']))

    query = {}
    for item in messages:
        if "i18n" in item['message']:
            continue
        query[item['message']] = item['message']

    trans = (translate.translate(query) if len(query) else {})

    for item in messages:
        if "i18n" in item['message'] or "+" in item['message']:
            continue
        origin_message = trans[item['message']]
        item.insert_before(Comment(f"message={item['message']}"))
        item.insert_before("\n")
        translation[item['message']] = origin_message
        item['message'] = f"#{{i18n.get('{origin_message}').d('{origin_message}')}}"

    #  处理label
    field_labels = soup.findAll(
        lambda attr: attr.has_attr('label') and isChinese(attr['label']) and attr.name != "Action")

    # 预先翻译
    need_translate = {}
    for item in field_labels:
        if item.name.lower() == 'action' or item.name == 'RecordActions':
            if isChinese(item['label']):
                need_translate[item['label']] = item['label']

    trans = (translate.translate(need_translate) if len(need_translate) > 0 else {})

    for item in field_labels:
        if "i18n" in item['label'] or "+" in item['label']:
            item.insert_before(Comment(f"label={item['label']}"))
            item.insert_before("\n")
            del item['label']
            continue

        if item.name == 'RecordActions':
            if isChinese(item['label']):
                item.insert_before(Comment(f"label={item['label']}"))
                item.insert_before("\n")
                translation[item['label']] = trans[item['label']]
                item['label'] = trans[item['label']]
            continue

        if item.name.lower() == 'field':
            item.insert_before(Comment(f"label={item['label']}"))
            item.insert_before("\n")
            del item['label']

    # 处理action
    field_confirms = soup.findAll(lambda attr: attr.name == "Action")

    need_translate = {}
    for item in field_confirms:
        if item.has_attr('label') and isChinese(item['label']) and "i18" not in item['label']:
            label = item['label']
            need_translate[label] = label

        if item.has_attr('confirm') and isChinese(item['confirm']) and "i18" not in item['confirm']:
            confirm = item['confirm']
            need_translate[confirm] = confirm

    trans = (translate.translate(need_translate) if len(need_translate) > 0 else {})

    for item in field_confirms:
        message = []
        if item.has_attr('label') and isChinese(item['label']) and "i18" not in item['label']:
            message.append(f"label={item['label']}")
            translation[item['label']] = trans[item['label']]
            item['label'] = trans[item['label']]

        if item.has_attr('confirm') and isChinese(item['confirm']) and "i18" not in item['confirm']:
            message.append(f"confirm={item['confirm']}")
            translation[item['confirm']] = trans[item['confirm']]
            item['confirm'] = trans[item['confirm']]

        if len(message) > 0:
            item.insert_before(Comment(",".join(message)))
            item.insert_before("\n")

    # 处理modalTitle
    model_titles = soup.findAll(
        lambda attr: attr.has_attr('modalTitle') and isChinese(attr['modalTitle']) and "i18" not in attr['modalTitle'])

    need_translate = {}
    for item in model_titles:
        need_translate[item['modalTitle']] = item['modalTitle']

    trans = translate.translate(need_translate)

    for item in model_titles:
        item.insert_before(Comment(f"modalTitle={item['modalTitle']}"))
        item.insert_before("\n")
        translation[item['modalTitle']] = trans[item['modalTitle']]
        item['modalTitle'] = trans[item['modalTitle']]

    pretty_soup = soup_prettify2(soup, desired_indent=4)
    with open(path, 'w') as f:
        f.write(pretty_soup)
    log.info(f"完成{path}")
    return pretty_soup


# with open(path, 'w') as f:
#     f.write()
# print(soup.prettify())
path = input("输入路径：")
if os.path.isfile(path):
    log.info(f"处理路径:{path}")
    parser(path)
else:
    for root, dirs, files in os.walk(path):
        if "resources" not in root:
            continue

        for file in files:
            if file.endswith(".xml"):
                log.info(f"处理路径:{os.path.join(root, file)}")
                parser(os.path.join(root, file))

# a = "/Users/youtiao/IdeaProjects/gaia/gaia-app-srm/srm-price-implement/src/main/resources/trantor/resources/srm_price/view/PricePlanEditNew.view.xml"
# t = parser(a)
# print(t)

res = json.dumps(translation, indent=4, ensure_ascii=False)
log.info("\n" + res)

with open("../res.json", 'w') as f:
    f.write(res)
