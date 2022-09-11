from flask import Flask, render_template, request, jsonify
import youtube
from flask_cors import CORS, cross_origin
import mongo_data

app = Flask(__name__)


@app.route('/', methods=['GET'])
@cross_origin()
def index():
    return render_template('index.html')


@app.route('/find', methods=['POST', 'GET'])
@cross_origin()
def information():
    if request.method == "POST":
        try:
            channel_url = str(request.form.get("channel_url"))
            no_of_vedio = int(request.form.get("no_of_vedio"))
            sleep_between_interactions = int(request.form.get("sleep_between_interactions"))
            youtube.final(channel_url, no_of_vedio, sleep_between_interactions)
            youtube.download_vedio()
            df1 = mongo_data.mongo_fetch()
            df2 = mongo_data.mongo_secondfetch()
            data_list = []
            for i in range(len(df1[0]['urls'])):
                output = {"Thumbnail": df1[0]['thumbnails'][i],
                          "TITLE OF VIDEOS": df1[0]["title_list"][i],
                          "VIDEOS URL": df1[0]['urls'][i],
                          "VIEWS": df2[0]['views'][i],
                          "LIKES": df2[0]['likes'][i],
                          "TOTAL NO. OF COMMENTS": df2[0]['comment_count'][i],
                          "COMMENTER": df2[0]['commenter'][str(i)],
                          "COMMENTS": df2[0]['comment'][str(i)]}
                data_list.append(output)
            return render_template('results.html', data_list=data_list[0:(len(data_list))])
        except Exception as e:
            print('The Exception message is: ', e)
            return "Lost Internet Connection"
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
