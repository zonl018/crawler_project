# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from pymongo import MongoClient

class MyfirstscrapyprojectPipeline(object):
    def process_item(self, item, spider):
        item["push"] = int(item["push"])
        return item

    
'''
- 將原本推文數量從字串轉為整數：
- 要啟用pipeline，打開settings這隻檔案，找到ITEM_PIPELINES（如下程式碼）部分將註解拿掉：
    ITEM_PIPELINES = {
     'myFirstScrapyProject.pipelines.MyfirstscrapyprojectPipeline': 300,
    }
- 後面的數字300表示Pipeline的執行順序，小的會先執行。
'''
class DeleteNullTitlePipeline(object):
    def process_item(self, item, spider):
        title = item["title"]
        if title:
            return item
        else:
            raise DropItem("found null title %s", item)

            
'''
- 新增一個DuplicatesTitlePipeline的類別。
- 建立一個叫做article的集合。
- 若發現title已經存在於集合內則丟棄該item，否則丟入集合內並傳回item。
---------------------------------------------------------------------
-不過本篇的例子為爬PTT版，可能就不適合單用title來過濾重複，因為通常回文的標題都是一樣的，這樣會不小心把文章都過濾掉了，所以要確定好需求再去寫pipelines哦！

'''
class DuplicatesTitlePipeline(object):
    def __init__(self):
        self.article = set()
    def process_item(self, item, spider):
        title = item['title']
        if title in self.article:
            raise DropItem('duplicates title found %s', item)
        self.article.add(title)
        return(item)


class MongoDBPipeline:
    def open_spider(self, spider):
        db_uri = spider.settings.get('MONGODB_URI', 'mongodb://localhost:27017')
        db_name = spider.settings.get('MONGODB_DB_NAME', 'ptt_scrapy')
        self.db_client = MongoClient('mongodb://localhost:27017')
        self.db = self.db_client[db_name]

    def process_item(self, item, spider):
        self.insert_article(item)
        return item

    def insert_article(self, item):
        item = dict(item)
        self.db.article.insert_one(item)

    def close_spider(self, spider):
        self.db_client.close()