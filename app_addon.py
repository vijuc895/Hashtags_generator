from random import randint
from time import strftime
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import numpy as np
import pandas as pd
from tqdm import tqdm
import google
import time
import instaloader
import time
from datetime import date, timedelta

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'
class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])


@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    #print(form.errors)
    if request.method == 'POST':
        keyword=request.form['name']
        keyword=keyword.lower()
        keyword=keyword.split(" ")
        length=len(keyword)
        iters=int(180/length)
        print(keyword)
        data = pd.DataFrame(columns=['username', 'following','datetime','followers','likes','comments', 'caption_hashtags'])
        info = []
        print("initiated")
        L = instaloader.Instaloader()
        likes = []
        comments = []
        caption_hashtags=[]
        datetime = []
        username = []
        following = []
        followers = []
        def scraper(hashtag):

            count = 0
            for post in L.get_hashtag_posts(hashtag):
                dt=post.date.strftime("%d-%m-%Y")
                if dt<(date.today() - timedelta(days=1)).strftime('%d-%m-%Y'):
                    profile = instaloader.Profile.from_username(L.context, post.owner_username)
                    username.append(post.owner_username)
                    following.append(profile.followees)
                    followers.append(profile.followers)
                    datetime.append(post.date)
                    caption_hashtags.append(post.caption_hashtags)
                    likes.append(post.likes)
                    comments.append(post.comments)
                    count+=1
                    print("collected",count,"post")
                    if count ==iters:
                        break   
        print("data scraper started")
        for i in keyword:
            scraper(i)
        data=pd.DataFrame(
        {'username':username,
         'following':following,
         'followers':followers,
         'datetime':datetime,  
         'likes':likes,
         'comments':comments,
         'caption_hashtags':caption_hashtags,
        })
        print(data.shape)
        print(data.columns)
        data.head()
        data.sort_values(["likes","comments","followers"], axis=0, ascending=False, inplace=True)
        data.drop_duplicates(subset ="datetime",keep = 'first', inplace = True) 
        hashtage_data = pd.DataFrame(columns=['hashtage'])
        hastage_count = []
        print("now apply data processing")
        def hastage_counts(hastage):
            L = instaloader.Instaloader()
            count=0
            for post in L.get_hashtag_posts(hastage):
                dt=post.date.strftime("%d-%m-%Y")
                count+=1
                if dt==(date.today() - timedelta(days=2)).strftime('%d-%m-%Y'):
                    break
            hastage_count.append(count)# Custom function to extract various attributes given a hashtag
        hashtage=[]
        not_hastage=[]
        for i in data["caption_hashtags"]:
            for j in i:
                for k in keyword:
                    if k in j:
                        hashtage.append(j)
                    else:
                        not_hastage.append(j)
                    
        hashtage_data=pd.DataFrame({'hashtage':hashtage})          
        hash=hashtage_data["hashtage"].value_counts()
        df_hashtage=hash.to_frame()
        df_hashtage.reset_index(inplace = True)
        not_hashtage_data=pd.DataFrame({'hashtage':not_hastage})          
        not_hash=not_hashtage_data["hashtage"].value_counts()
        not_df_hashtage=not_hash.to_frame()
        not_df_hashtage.reset_index(inplace = True)

        print(df_hashtage.shape)
        print(data.shape)
        l1=len(df_hashtage)
        df_hashtage.sort_values(["hashtage"], axis=0,ascending=False, inplace=True)
        not_df_hashtage=not_df_hashtage[not_df_hashtage["hashtage"]>df_hashtage.loc[1]["hashtage"]]
        l2=len(not_df_hashtage)
        for i in range(l2):
            df_hashtage.loc[l1+i]=not_df_hashtage.loc[i]
        print("count post for particular hashtage")
        for i in df_hashtage["index"]:
            hastage_counts(i)
        df_hashtage["hastage_count"]=hastage_count
        df_hashtage.sort_values(["hastage_count", "hashtage"], axis=0,ascending=False, inplace=True) 
        df_hashtage.head()
        df_hashtage.reset_index(inplace=True)
        df_hashtage=df_hashtage.drop(["level_0"],1)
        df_hashtage=df_hashtage.head(50)
        top_hashtage=df_hashtage.head(6)
        recommended_hashtage=top_hashtage["index"]
        tags=[]
        c=0
        for i in recommended_hashtage:
            tags.append(i)
            c+=1
            if c==6:
                break
        print("len of tags",len(tags))
        print("hashtage to recommended are Created")
        df_hashtage.to_csv('accounting_hashtage.csv',sep=',')
        print("stored hashtage in csv with their freq and post")
        print()


        

        if form.validate():
            flash('Hi!! Must used hastage are: {} {}'.format('#'+tags[0],'#'+tags[1],'#'+tags[2],'#'+tags[3],'#'+tags[4],'#'+tags[5]))
            flash("Also other hastage excel has Also Been Generated")
        else:
            flash('Error: All Fields are Required')

    return render_template('index.html', form=form)

if __name__ == "__main__":
    app.run()
