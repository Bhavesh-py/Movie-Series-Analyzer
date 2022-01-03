import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from imdb import IMDb
from matplotlib.gridspec import GridSpec


def rating_plot(title,df2, total_seasons, less, more):
  labels = 'Not Worth it', 'Worth it'
  data = [less, more]
  colors = ['orangered', 'greenyellow']
  explode = [0.1, 0]

  fig = plt.figure(figsize=(15,10))
  gs = fig.add_gridspec(2, 2)
  
  # create sub plots as grid
  ax1 = fig.add_subplot(gs[0, 0])
  ax2 = fig.add_subplot(gs[1, 0])
  ax3 = fig.add_subplot(gs[:, -1])

  plt.style.use("seaborn");

  fig.suptitle(str(title).title()+"'s Journey", fontsize=16, fontweight ="bold")

  ax1.plot(df2["season"], df2["rating"]);
  ax1.set(title = "Season v/s Rating", xlabel = "Season #", ylabel = "Rating");
  ax1.xaxis.set_ticks(np.arange(1, total_seasons + 1, 1));
  ax1.yaxis.set_ticks(np.arange(1, 11, 1));

  ax2.plot(df2["season"], df2["votes"]);
  ax2.set(title = "Season v/s No. of Votes", xlabel = "Season #", ylabel = "Number of Votes");
  ax2.xaxis.set_ticks(np.arange(1, total_seasons + 1, 1));
  

  ax3.pie(data, autopct='%1.1f%%', explode = explode, shadow = True, colors = colors, startangle = 90, radius = 1.15)
  ax3.legend(labels, loc = "best")
  ax3.set_title(str(title).title()+"'s recommendation based on "+str(less+more)+" reviews", fontsize = 16, y = 1.05);
  return fig


def recommendation_plot(title,less,more):
  labels = 'Not Worth it', 'Worth it'
  data = [less, more]
  colors = ['orangered', 'greenyellow']
  explode = [0.1, 0]

  fig, ax = plt.subplots(figsize =(10, 7))

  ax.pie(data, autopct='%1.1f%%', explode = explode, shadow = True, colors = colors, startangle = 90, radius = 1.15)
  
  # patches, texts, tiles = plt.pie(data, colors=colors, autopct='%1.1f%%', shadow=True, explode = (0.1,0), startangle=90, radius=1)
  ax.legend(labels, loc = "best")
  ax.set_title(str(title).title()+"'s recommendation based on "+str(less+more)+" reviews", fontsize = 16, y = 1.05)
  return fig

#Function for Show Rating.
def Series_Plot(title_id,total_seasons, url):
  s_data = []
  for s in range(1,total_seasons+1):
    url1 = url+"?season="+str(s)
    main_page = requests.get(url1).text
    soup = BeautifulSoup(main_page, "lxml")
    episodes = soup.find_all("div", {"class":"info", "itemprop":"episodes"})
    try:
      for i in episodes:
        season = s
        rating = float(i.find("span", class_ = "ipl-rating-star__rating").text)
        vote_count = int("".join(i.find("span", class_ = "ipl-rating-star__total-votes").text[1:-1].split(",")))
        
        ep_data = [season, rating, vote_count]
        s_data.append(ep_data)
    except:
      total_seasons-=1
      break

  #Creating Show DF
  final_data = pd.DataFrame(data = s_data, columns = ["Season", "Ep_Rating", "Vote_Count"])

  #Creating Season-wise DF
  season_data = []
  for i in sorted(list(set(final_data["Season"]))):
    curr_season = final_data[final_data["Season"] == i]
    temp = (curr_season["Ep_Rating"] * curr_season["Vote_Count"])
    season_rating = sum(temp) / sum(curr_season["Vote_Count"])
    season_data.append([i, round(season_rating,2), sum(curr_season["Vote_Count"])])
    df2 = pd.DataFrame(data = season_data, columns = ["season", "rating", "votes"])
    
  return (df2, total_seasons)



def Get_Reviews(title_id):
  url_reviews = "https://www.imdb.com/title/tt"+title_id+"/reviews/_ajax"
  url_reviews_next = "https://www.imdb.com/title/tt"+title_id+"/reviews/_ajax?ref_=undefined&paginationKey="
  response= requests.get(url_reviews).text
  soup = BeautifulSoup(response, 'lxml')
  reviews = []
  page_reviews = soup.find_all("span", class_="point-scale")
  for review in page_reviews:
    curr_rating = review.find_previous("span").text
    reviews.append(curr_rating)

  paginationKey = ''
  # If there's only one page and more, there's won't be the class load_more_data
  try:
      paginationKey = soup.find_all("div", class_="load-more-data")[0]["data-key"]
  except:
      paginationKey = ''
  while paginationKey != '':
      response= requests.get(url_reviews_next+paginationKey)
      soup = BeautifulSoup(response.text, "lxml")
      
      page_reviews = soup.find_all("span", class_="point-scale")
      for review in page_reviews:
        curr_rating = review.find_previous("span").text
        reviews.append(curr_rating)

      try:
          paginationKey = soup.find_all("div", class_="load-more-data")[0]["data-key"]
      except:
          paginationKey = ''
  
  return reviews



  

def Movie_Plot(title_id):
  reviews = Get_Reviews(title_id)
  less = 0
  more = 0
  for i in reviews:
    if int(i) < 6:
      less+=1
    else:
      more+=1

  return (less,more)




def Main(title, title_id):
  ins = IMDb()
  movie = ins.get_movie(title_id)
  total_seasons = 0
  try:
    total_seasons = movie["seasons"]
    if total_seasons > 1:
      url = "https://www.imdb.com/title/tt"+title_id+"/episodes"
      df2, total_seasons = Series_Plot(title_id,total_seasons, url)
      less, more = Movie_Plot(title_id)
      fig = rating_plot(title, df2,total_seasons, less, more)
    else:
      less, more = Movie_Plot(title_id)
      fig = recommendation_plot(title,less,more)
  except:
    less, more = Movie_Plot(title_id)
    fig = recommendation_plot(title,less,more)

  return fig




def Method(title):
  ins = IMDb()
  movie = ins.search_movie(title)
  title_id = movie[0].movieID
  fig = Main(title, title_id)
  return fig
