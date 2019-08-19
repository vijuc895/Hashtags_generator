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
                date=post.date.strftime("%d-%m-%Y")
                if date<'17-08-2019':
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
                    if count == 150:
                        break   
        print("data scraper started")
        scraper(keyword)
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
        hashtage_data = pd.DataFrame(columns=['hashtage'])
        hastage_count = []
        print("now apply data processing")
        def hastage_counts(hastage):
            L = instaloader.Instaloader()
            count=0
            for post in L.get_hashtag_posts(hastage):
                date=post.date.strftime("%d-%m-%Y")
                count+=1
                if date=='16-08-2019':
                    break
            hastage_count.append(count)# Custom function to extract various attributes given a hashtag
        hashtage=[]
        for i in data["caption_hashtags"]:
            for j in i:
                if keyword in j:
                    hashtage.append(j)
        hashtage_data=pd.DataFrame({'hashtage':hashtage})          
        hash=hashtage_data["hashtage"].value_counts()
        df_hashtage=hash.to_frame()
        df_hashtage.reset_index(inplace = True)
        print(df_hashtage.shape)
        print(data.shape)
        print("count post for particular hashtage")
        for i in df_hashtage["index"]:
            hastage_counts(i)
        df_hashtage["hastage_count"]=hastage_count
        df_hashtage.sort_values(["hastage_count", "hashtage"], axis=0,ascending=False, inplace=True) 
        df_hashtage.head()
        df_hashtage.reset_index(inplace=True)
        df_hashtage=df_hashtage.drop(["level_0"],1)
        df_hashtage=df_hashtage.head(50)
        df_hashtage.sort_values(["hashtage"], axis=0,ascending=False, inplace=True) 
        top_hashtage=df_hashtage.head(3)
        recommended_hashtage=top_hashtage["index"]
        tags=[]
        c=0
        for i in recommended_hashtage:
            tags.append(i)
            c+=1
            if c==3:
                break
        print("hashtage to recommended are Created")
        df_hashtage.to_csv('accounting_hashtage.csv',sep=',')
        print("stored hashtage in csv with their freq and post")    

        if form.validate():
            flash('Hi!! Must used hastage are: {} {}'.format('#'+tags[0],'#'+tags[1]))
            flash("Also other hastage excel has Also Been Generated")
        else:
            flash('Error: All Fields are Required')

    return render_template('index.html', form=form)

if __name__ == "__main__":
    app.run()
