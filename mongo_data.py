import pymongo
import requests
import gridfs


def monog_firstPage(data1):
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")

        database = client['youtubescape']
        collection = database["front_Page"]
        collection.insert_one(data1)
        print('data inserted')
    except Exception as e:
        print(e)
    finally:
        client.close()


def mongo_dropfirst():
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")

        database = client['youtubescape']
        collection = database["front_Page"]
        collection.drop()
        print('old data deleted')
    except Exception as e:
        print(e)
    finally:
        client.close()


def mongo_fetch():
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")

        database = client['youtubescape']
        collection = database["front_Page"]
        record = collection.find()
        table1 = [x for x in record]
        return table1
    except Exception as e:
        print(e)
    finally:
        client.close()


def mongo_secondPage(data2):
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")
        database = client['youtubescape']
        collection = database["second_Page"]
        collection.insert_one(data2)
        print('data inserted')
    except Exception as e:
        print(e)
    finally:
        client.close()


def mongo_dropsecond():
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")

        database = client['youtubescape']
        collection = database["second_Page"]
        collection.drop()
        print('old data deleted')
    except Exception as e:
        print(e)
    finally:
        client.close()


def mongo_secondfetch():
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")

        database = client['youtubescape']
        collection = database["second_Page"]
        record = collection.find()
        table2 = [x for x in record]
        return table2
    except Exception as e:
        print(e)
    finally:
        client.close()


def mongo_dropphotosvideos():
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")

        database = client['youtubescape']
        collection = database["fs.chunks"]
        collection.drop()
        collection = database['fs.files']
        collection.drop()
        print('old data deleted')
    except Exception as e:
        print(e)
    finally:
        client.close()
