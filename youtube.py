import os
import shutil
import time
import requests
import gridfs
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from pytube import YouTube
import pandas as pd
import pymongo
import mongo_data
from IPython import display


def scroll_to_end(wd, sleep_between_interactions):
    """
    :param wd: give driver name {"wd = webdriver.Chrome()" and "wd = webdriver.FirefoxOptions()"}
    :param sleep_between_interactions: fix the time sleep value according to your network connection
    :return: scroll down to the end of your page
    """
    prev_h = 0
    while True:
        height = wd.execute_script("""
                    function getActualHeight() {
                        return Math.max(
                            Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
                            Math.max(document.body.offsetHeight, document.documentElement.offsetHeight),
                            Math.max(document.body.clientHeight, document.documentElement.clientHeight)
                        );
                    }
                    return getActualHeight();
                """)
        wd.execute_script(f"window.scrollTo({prev_h},{prev_h + 200})")
        # fix the time sleep value according to your network connection
        time.sleep(sleep_between_interactions)
        prev_h += 200
        if prev_h >= height:
            break


def front_page_info(channel_url: str, no_of_vedio: int = 1, sleep_between_interactions: int = 1):
    """
    :param channel_url: give YouTube channel url
    :param no_of_vedio: How much no. of vedios info you want to get
    :param sleep_between_interactions: fix the time sleep value according to your network connection
    :return: a list of information ([title_list, video_urls, video_IDs, thumbnails]) and it save it in .csv format also with the name of front_page_data.csv
    """
    title_list = []
    video_urls = []
    video_IDs = []
    thumbnails = []
    search_url = channel_url + "/videos"

    def find_video_id(value):
        """
        :param value: give vedio url
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        :return: vedio_id
        """

        query = urlparse.urlparse(value)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = urlparse.parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/shorts':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        return None

    # load the page
    wd = webdriver.Chrome()
    wd.get(search_url)
    wd.maximize_window()
    time.sleep(sleep_between_interactions + 1)
    scroll_to_end(wd, sleep_between_interactions)
    content = wd.page_source.encode('utf-8').strip()
    wd.close()
    soup = BeautifulSoup(content, 'lxml')

    # get all vedios titles
    try:
        total_titles = soup.findAll('a', id='video-title')
        vedio_count = len(total_titles)
        titles = total_titles[:no_of_vedio]
    except Exception as e:
        print(e)

    try:
        for title in titles:
            title_list.append(title.text)
    except Exception as e:
        print(e)

    print("we are fetching {} latest video's info out of {} total numbers of vedios ".format(len(titles), vedio_count))

    # get all vedios url
    try:
        for i in range(len(titles)):
            video_urls.append('https://www.youtube.com' + titles[i]['href'])
    except Exception as e:
        print(e)

    # get all vedios thumbnails
    try:
        for video_url in video_urls:
            video_id = find_video_id(video_url)
            video_IDs.append(video_id)
            thumbnail = 'http://img.youtube.com/vi/{}/maxresdefault.jpg'.format(video_id)
            thumbnails.append(thumbnail)

    except Exception as e:
        print(e)
    front_page_data = pd.DataFrame(
        {"title_list": title_list, "video_urls": video_urls, "video_IDs": video_IDs, "thumbnails": thumbnails})
    front_page_data.to_csv("front_page_data.csv")
    return [title_list, video_urls, video_IDs, thumbnails]


def each_vedio_info(sleep_between_interactions):
    """
    :param sleep_between_interactions: fix the time sleep value according to your network connection
    :return: list [likes, views, comment_counts, commenter_dict, comment_dict]
    """
    df1 = mongo_data.mongo_fetch()
    df = df1[0]
    vedio_urls = df['urls']
    likes = []
    comment_counts = []
    commenter_dict = {}
    comment_dict = {}
    views = []
    for m, url in enumerate(vedio_urls):
        wd = webdriver.Chrome()
        wd.get(url)
        wd.maximize_window()
        scroll_to_end(wd, sleep_between_interactions)
        soup = BeautifulSoup(wd.page_source, 'html.parser')
        wd.quit()

        if url.split('/')[3] == 'shorts':
            like = soup.select('#text')[5].text
            comment_count = "0"
            comment_name = ["unable to fetch"]
            comment_list = ["unable to fetch"]
        else:
            like = soup.select("#text")[2].text
            comment_count = soup.select("h2 yt-formatted-string")[4].text
            commenter = soup.select("#author-text span")
            comment_name = [x.text.strip('\n').strip() for x in commenter]
            comment_div = soup.select("#content #content-text")
            comment_list = [x.text for x in comment_div]
        commenter_dict[str(m)] = comment_name
        comment_dict[str(m)] = comment_list
        likes.append(like)
        comment_counts.append(comment_count)
        # finding views
        vedio_name = YouTube(url)
        view = vedio_name.views
        views.append(view)
    return [likes, views, comment_counts, commenter_dict, comment_dict]


def first_page(channel_url, no_of_vedio, sleep_between_interactions):
    """
    :param channel_url: give YouTube channel url
    :param no_of_vedio: How much no. of vedios info you want to get
    :param sleep_between_interactions: fix the time sleep value according to your network connection
    :return: a list of information ([title_list, urls, IDs, thumbnails])
    """
    fp = front_page_info(channel_url, no_of_vedio, sleep_between_interactions)
    data1 = {"title_list": fp[0],
             "urls": fp[1],
             "IDs": fp[2],
             "thumbnails": fp[3]}
    mongo_data.mongo_dropfirst()
    mongo_data.monog_firstPage(data1)
    df1 = mongo_data.mongo_fetch()
    df = df1[0]
    return df


def second_page(sleep_between_interactions):
    """
    :param sleep_between_interactions: fix the time sleep value according to your network connection
    :return: list of information of each video [likes, views, comment_counts, commenter_dict, comment_dict]
    """
    page2_data = each_vedio_info(sleep_between_interactions)
    data = {"likes": page2_data[0],
            "views": page2_data[1],
            "comment_count": page2_data[2],
            "commenter": page2_data[3],
            "comment": page2_data[4]}
    mongo_data.mongo_dropsecond()
    try:
        mongo_data.mongo_secondPage(data)
    except Exception as e:
        print('data is not inserting {}'.format(e))
    df2 = mongo_data.mongo_secondfetch()
    df_second = df2[0]
    return df_second


def final(channel_url, no_of_vedio, sleep_between_interactions):
    """
    :param channel_url: channel_url(string)
    :param no_of_vedio: no_of_vedio you want to fetch(int)
    :param sleep_between_interactions: sleep_between_interactions(int/float: from 0 to 5) according to your internet speed
    :return: it will save all data in mongodb server.
    """
    first_page(channel_url, no_of_vedio, sleep_between_interactions)
    second_page(sleep_between_interactions)
    mongo_photo_video_upload()
    mongo_photodownload()


def mongo_photo_video_upload():
    mongo_data.mongo_dropphotosvideos()
    mongo_photoupload()
    mongo_videoupload()


def mongo_photoupload():
    """
    :return: upload thumbnails photo into mongodb
    """
    df1 = mongo_data.mongo_fetch()
    df = df1[0]
    photo_thumbs = df['thumbnails']
    client = pymongo.MongoClient(
        "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")

    database = client['youtubescape']
    # Create an object of GridFs for the above database.
    fs = gridfs.GridFS(database)
    for n, photo_thumb in enumerate(photo_thumbs):
        name = photo_thumb
        image_content = requests.get(name).content
        fs.put(image_content, filename=name)
    print("New photos uploaded in mongodb")


def mongo_photodownload():
    """
    :return: download all photos into thumbnail_photo folder
    """
    try:
        shutil.rmtree('thumbnail_photo')
        time.sleep(3)
        os.mkdir('thumbnail_photo')
        time.sleep(3)
    except OSError as e:
        print(e)
    df1 = mongo_data.mongo_fetch()
    df = df1[0]
    photo_thumbs = df['thumbnails']
    client = pymongo.MongoClient(
        "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")
    database = client['youtubescape']
    # Create an object of GridFs for the above database.
    fs = gridfs.GridFS(database)
    folder_path = './thumbnail_photo'
    for n, photo_thumb in enumerate(photo_thumbs):
        name = photo_thumb
        image_content = database.fs.files.find_one({"filename": name})
        photo_id = image_content['_id']
        outputdata = fs.get(photo_id).read()
        output = open(os.path.join(folder_path, 'thumbnail_' + str(n) + ".jpg"), 'wb')
        output.write(outputdata)
        output.close()
    print("Photos downloaded in your system")


def mongo_videoupload():
    """
    :return: upload video into mongodb
    """
    df1 = mongo_data.mongo_fetch()
    df = df1[0]
    vedio_urls = df['urls']

    client = pymongo.MongoClient(
        "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")

    database = client['youtubescape']
    # Create an object of GridFs for the above database.
    fs = gridfs.GridFS(database)
    for m, url in enumerate(vedio_urls):
        name = url
        image_content = requests.get(name).content
        fs.put(image_content, filename=name)
    print("Video uploaded in Mongo")


# vedios downloader
def download_vedio():
    try:
        shutil.rmtree('Video')
        time.sleep(3)
    except OSError as e:
        print(e)
    df1 = mongo_data.mongo_fetch()
    df = df1[0]
    vedio_urls = df['urls']
    for m, url in enumerate(vedio_urls):
        try:
            vedio_name = YouTube(url)
            vedio_streams = vedio_name.streams.filter(adaptive=True, file_extension='mp4').first()
            # vids = list(enumerate(vedio_streams))
            # for i in vids:
            #     print(i[0], " for ", i[1].type, " ", i[1].resolution, " ", i[1].mime_type)
            # while True:
            #     try:
            #         strm = int(input("enter no. from 0 to {} for download vedio/audio: ".format(len(vids) - 1)))
            #         if 0 <= strm < (len(vids)):
            #             print("Please wait vedio is downloading...")
            #             break;
            #         else:
            #             print("No. should be greater than or equal to 0 and less than {}...".format(len(vids)))
            #     except ValueError:
            #         print("Provide an integer value...which is greater than or equal to 0 and less than {}...".format(
            #             len(vids)))
            #         continue
            # vedio_streams[strm].download('./Video', timeout=20)
            vedio_streams.download('./Video', timeout=10)
            print('{} Vedio Downloaded Successfully.... Please wait :-)'.format(m+1))
        except Exception as e:
            print("Some connection issue coming....{}".format(e))
            continue
    print('All vedios download completed. {} vedios downloaded'.format(len(vedio_urls)))


def photo_print():
    """
    :return: It will print all photos of thumbnail
    """
    df1 = mongo_data.mongo_fetch()
    df = df1[0]
    photo_thumbs = df['thumbnails']
    client = pymongo.MongoClient(
        "mongodb+srv://himanshu:ramram@testing-cluster.t5jsa.mongodb.net/?retryWrites=true&w=majority")
    database = client['youtubescape']
    # Create an object of GridFs for the above database.
    fs = gridfs.GridFS(database)
    for n, photo_thumb in enumerate(photo_thumbs):
        name = photo_thumb
        image_content = database.fs.files.find_one({"filename": name})
        photo_id = image_content['_id']
        outputdata = fs.get(photo_id).read()
        x = display.Image(outputdata, height=200, width=300)
        print(x)
        return x
