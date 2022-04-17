import uvicorn
from fastapi import FastAPI,BackgroundTasks
import requests
from bs4 import BeautifulSoup
from replit import db
import os


app = FastAPI()

def send():
  res = requests.get('https://www.newsfirst.lk/feed/')
  soup = BeautifulSoup(res.content,features='lxml')
  item = soup.find('item')
  title = item.find('title').text
  image = item.find('img').get('src')
  paragraph = item.find_all('p')[1].text
  url = item.find('a').get('href')
  caption = f"""
  *{title}*
  `{paragraph}`
  ||[read more]({url})||
  """
  token = os.environ['DEMO']
  data = {
    "chat_id":os.environ['CHAT'],
    "photo":image,
    "caption":caption,
    "parse_mode":"MarkdownV2"
  }
  requests.post(
    f'https://api.telegram.org/{token}/sendPhoto',
    data=data
  )
@app.get("/")
def root():
  return {"message":"newsfirst rss"}

@app.get("/isupdate")
def isUpdate(background_tasks: BackgroundTasks):
    res = requests.get('https://www.newsfirst.lk/feed/')
    job = None
    soup = BeautifulSoup(res.content,features='xml')
    lastbuilddate = soup.find('lastBuildDate').text
    db_lastbuilddate = db['lastbuilddate']
    if hash(lastbuilddate) != db_lastbuilddate:
      db['lastbuilddate'] = hash(lastbuilddate)
      job = 'accept'
      background_tasks.add_task(send)
    else:
      job = 'reject'
    return {"job":job}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

