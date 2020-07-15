import pandas
import pandas as pandas
from flask import Flask, render_template
from flask_cors import CORS
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup,NavigableString
import re
from pymongo import MongoClient
import pandas as pd
import csv
import xlsxwriter

# DataBase Connection
client = MongoClient("mongodb+srv://kavi:kavi123@cluster0-wovzx.mongodb.net/News?retryWrites=true&w=majority")
db = client.News

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/BBC')
def BBC():
    BBC_url = "http://feeds.bbci.co.uk/news/rss.xml"
    BBC_get = requests.get(BBC_url)
    BBC_soup = BeautifulSoup(BBC_get.content, features="xml")
    BBC = BBC_soup.findAll('item')
    # print(BBC)
    count = 0
    BBC_items = []
    for item in BBC:

        BBC_item = {}
        BBC_item['BBCTitle'] = item.title.text
        BBC_item['BBCDescription'] = item.description.text
        BBC_item['BBCLink'] = item.link.text
        BBC_item['BBCDate'] = item.pubDate.text


        tit = item.title.text
        desc = item.description.text
        search = 'Covid-19' or 'pandemic'
        search1 = 'Coronavirus' or 'corona'

        if search in tit or search in desc or search1 in tit or search1 in desc:
            count = count + 1
            if count < 22:
                BBC_items.append(BBC_item)

    Dataframe_BBC = pd.DataFrame(BBC_items, columns=['BBCTitle', 'BBCDescription', 'BBCLink', 'BBCDate'])
    # print(Dataframe_BBC)
    Dataframe_BBC.to_csv('BBC.csv', index=False, encoding='utf-8')
    db.feed_BBC.insert_many(Dataframe_BBC.to_dict('records'))
    return render_template('BBC.html', tables=[Dataframe_BBC.to_html(classes='data')], titles=Dataframe_BBC.columns.values)

@app.route('/CNN')
def CNN():
    CNN_url = ('http://rss.cnn.com/rss/cnn_topstories.rss')
    CNN_get = requests.get(CNN_url)
    CNN_soup = BeautifulSoup(CNN_get.content, features="xml")
    CNN = CNN_soup.findAll('item')
    # print(CNN)
    count = 0

    CNN_items = []
    for item in CNN:
        CNN_item = {}
        CNN_item['CNNTitle'] = item.title.text
        CNN_item['CNNLink'] = item.link.text

        pubDate = ''
        desc = ''

        try:
            if item.description.text is not None:

                soup = BeautifulSoup(item.description.text, 'lxml')
                desc = soup.text.strip()
                # print("chkk", len(desc))
                if(len(desc) < 1):
                    desc = 'None'

        except:
            print("An exception occurred")
            desc = 'None'

        try:
            if item.pubDate.text is not None:
                pubDate= item.pubDate.text


        except:
            print("An exception occurred")
            pubDate = 'None'

        CNN_item['CNNDate'] = pubDate
        CNN_item['CNNDescription'] = desc

        tit = item.title.text
        search = 'Covid-19'
        search1 = 'corona'
        if search in tit or search in desc or search1 in tit or search1 in desc:
            count = count + 1
            if count < 22:
                CNN_items.append(CNN_item)

    # print(CNN_items)

    Dataframe_CNN = pd.DataFrame(CNN_items, columns=['CNNTitle', 'CNNDescription', 'CNNLink' ,'CNNDate'])
    # print(Dataframe_CNN)
    Dataframe_CNN.to_csv('CNN.csv', index=False, encoding='utf-8')
    db.feed_CNN.insert_many(Dataframe_CNN.to_dict('records'))
    return render_template('BBC.html', tables=[Dataframe_CNN.to_html(classes='data')],titles=Dataframe_CNN.columns.values)


# print("Making final csv")
import pandas as pd
df2 = pd.read_csv('CNN.csv')
df1 = pd.read_csv('BBC.csv')
finaldf = df1.join(df2)
finaldf.to_csv("finaldf.csv")


#create object
def sentiment(polarity):
    if blob.sentiment.polarity < 0:

        print("Negative")
    elif blob.sentiment.polarity > 0:
        print("Positive")
    else:
        print("Neutral")

print('---------------BBC-------------------------')


row_count = 0
sentiment = ''


infile_BBC = 'finaldf.csv'

with open(infile_BBC, 'r') as csvfile_BBC:
    print("ENTER")
    Semantic_items = []
    rows = csv.reader(csvfile_BBC)

    for row in rows:

        Semantic_item = {}
        sentence = row[1]
        sentence1 = row[5]
        blob = TextBlob(sentence)
        blob1 = TextBlob(sentence1)
        # print("11:: ",blob.sentiment)
        # print("@22:: " ,sentence)

        print(blob.sentiment.polarity)
        value = blob.sentiment.polarity
        value1 = blob1.sentiment.polarity

        if blob.sentiment.polarity < 0:
            bbc_sentiment = 'Negative'

            print("Negative")
        elif blob.sentiment.polarity > 0:
            print("Positive")
            bbc_sentiment = 'Positive'
        else:
            print("Neutral")
            bbc_sentiment = 'Neutral'

        if blob1.sentiment.polarity < 0:
            cnn_sentiment = 'Negative'

            print("Negative")
        elif blob1.sentiment.polarity > 0:
            print("Positive")
            cnn_sentiment = 'Positive'
        else:
            print("Neutral")
            cnn_sentiment = 'Neutral'

        # print ('--------------' , value ," ++++ ", sentence)
        print('---------------------------------------')
        row_count = row_count + 1
        if row_count > 2 :
            Semantic_item['BBCTitle'] = sentence
            Semantic_item['BBCSentiment'] = bbc_sentiment
            Semantic_item['BBCPolarity'] = value

            Semantic_item['CNNTitle'] = sentence1
            Semantic_item['CNNSentiment'] = cnn_sentiment
            Semantic_item['CNNPolarity'] = value1
            Semantic_items.append(Semantic_item)
    Dataframe_Semantic = pd.DataFrame(Semantic_items, columns=['BBCTitle', 'BBCSentiment','BBCPolarity', 'CNNTitle', 'CNNSentiment','CNNPolarity'])
    print("Sementic Dataframes :::", Dataframe_Semantic)
    Dataframe_Semantic.to_csv('Semantic.csv', index=False, encoding='utf-8')
    db.Sementic.insert_many(Dataframe_Semantic.to_dict('records'))

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
