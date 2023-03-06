# import dependencies
from bs4 import BeautifulSoup
from splinter import Browser
import time

import sqlalchemy as sql
import csv
from sqlalchemy.orm import Session

from db.setup import Base, Movie

# import driver manager
from webdriver_manager.chrome import ChromeDriverManager

driver_path=ChromeDriverManager().install()

# create browser
browser=Browser('chrome', executable_path=driver_path)

# constants
BASE_URL='https://www.rottentomatoes.com/browse/movies_in_theaters/'
db_url='db/RT.sqlite'
DB_CONNECTION_URL=f'sqlite:///{db_url}'
scroll_js='window.scrollTo(0, document.body.scrollHeight);'

engine=sql.create_engine(DB_CONNECTION_URL)

Base.metadata.create_all(engine)

# visit website
browser.visit(BASE_URL)

# wait until website is rendered completely
time.sleep(2)

# get html from browser
html=browser.html

def scrape_movie_page(html):
	# create soup object with html (str)
	soup=BeautifulSoup(html, 'html.parser')
	session=Session(engine)
	    
	# parse element from html
	# find the tiles division
	tiles=soup.find_all('div', class_='discovery-tiles')[1]

	# find all the anchors
	links_list=tiles.find_all('a', class_='js-tile-link')

	for current_listing in links_list: 
	    movie_dict={}
	    title=current_listing.find_all('span', class_='p--small')[0].text.strip()
	    open_date=current_listing.find_all('span', class_='smaller')[0].text.strip()
	    movie_link=current_listing['href']
	    poster_link=current_listing.find_all('img', class_='posterImage')[0]['src']
	    score_pairs=current_listing.find_all('score-pairs')[0]

	    critic_score=None
	    audience_score=None
	    audience_sentiment=None
	    critic_sentiment=None

	    try: 
	        critic_score=score_pairs['criticscore']
	    except: 
	        pass

	    try: 
	        audience_score=score_pairs['audiencescore']
	    except: 
	        pass

	    try: 
	        critic_sentiment=score_pairs['criticsentiment']
	    except: 
	        pass

	    try: 
	        audience_sentiment=score_pairs['audiencesentiment']
	    except: 
	        pass

	    movie_dict['title']=title
	    movie_dict['open_date']=open_date
	    movie_dict['movie_link']=movie_link
	    movie_dict['poster_link']=poster_link
	    movie_dict['critic_score']=critic_score
	    movie_dict['critic_sentiment']=critic_sentiment
	    movie_dict['audience_score']=audience_score
	    movie_dict['audience_sentiment']=audience_sentiment

	    new_movie=Movie(**movie_dict)
	    session.add(new_movie)

	session.commit()
	session.close()        

id=1
for i in range(1, 4): 
	print(f'Scraping Page {i}...')
	browser.execute_script(scroll_js)
	more_button=browser.find_by_text('Load more')
	more_button.click()
	time.sleep(2)

scrape_movie_page(html)
browser.quit()