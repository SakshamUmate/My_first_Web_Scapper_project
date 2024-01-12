import logging
import re
import requests
import pymongo
from flask import Flask,request,render_template
from flask_cors import CORS,cross_origin
import pandas as pd

logging.basicConfig(filename="Youtube_Scrapper.log",level=logging.DEBUG,format='%(asctime)s %(name)s %(levelname)s %(message)s')

client=pymongo.MongoClient("mongodb+srv://saksham:qk70nd97a@cluster1.vucvhcs.mongodb.net/?retryWrites=true&w=majority")
db=client["datascience"]
collection=db["Y_T_Scrapper"]

app=Flask(__name__)

@app.route("/",methods=["GET","POST"])
@cross_origin()
def home_page():
    return render_template("index.html")                       




@app.route("/details",methods=["POST"])   
@cross_origin()                                                                                
def result():
    if request.method=="POST":
        try:
            logging.info("Scrapping is started")
            
            content=(request.form["text"]).replace(" ","")
            url=f"https://www.youtube.com/@{content}/videos"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            
            logging.info("details are requesting in response...")
            response=requests.get(url,headers=headers)
            res=response.text
            
            logging.info("Titles are scraping...")
            vid_titles = re.findall('"title":{"runs":\[{"text":".*?"', res)
            
            logging.info("Thumbnails are scraping...")
            vid_thumbnails = re.findall(r"https://i.ytimg.com/vi/[A-Za-z0-9_-]{11}/[A-Za-z0-9_]{9}.jpg", res)
            
            logging.info("links are scraping...")            
            vid_links = re.findall(r"watch\?v=[A-Za-z0-9_-]{11}", res)
            
            logging.info("veiws are scraping...")  
            pattern3 = re.compile(r"[0-9]+(\.[0-9]+)?[a-zA-Z]*K views")
            
            logging.info("Video age ...")
            pattern4 = re.compile(r"\d+ (minutes|hours|hour|days|day|weeks|week|years|year) ago")
            
            matches1 = pattern3.finditer(res)
            matches2 = pattern4.finditer(res)
            
            vid_viewcounts=[]
            vid_ages=[]
            
            for match1,match2 in zip(matches1,matches2):
                vid_ages.append(match2[0])
                vid_viewcounts.append(match1[0])
            
            logging.info("9-titles...")
            titles = vid_titles[0:10]
            
            logging.info("thumbnails...")
            thumbnails = list(dict.fromkeys(vid_thumbnails))
            
            logging.info("9-links...")
            links = vid_links[0:10]   
            
            logging.info("9-viewcounts by jump of 2...")
            viewcounts=vid_viewcounts[0:20:2]
            
            logging.info("9-ages by jump of 2...")
            ages=vid_ages[0:20:2]
            
            details_list=[]

            for title,thumbnail,link,viewcount,age in zip(titles,thumbnails,links,viewcounts,ages):
                details_dict={
                "title":title.split('"')[-2], "thumbnail": thumbnail, "link": "https://www.youtube.com/"+link,
                "viewcount": viewcount, "age": age
                }
                details_list.append(details_dict)
                        
            collection.insert_many(details_list)
            df=pd.DataFrame(details_list)
            df.to_csv("YT_scrapper")
            return render_template("details.html",details=details_list,channel=content)

        except Exception as e:
            logging.error(e)
            return "Something went wrong \U0001F629"

if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)















