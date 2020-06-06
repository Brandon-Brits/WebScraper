import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#Get English-translated titles
headers = {"Accept-Language": "en-US, en;q=0.5"}

url = "https://www.imdb.com/search/title/?groups=top_1000&ref_=adv_prv"

#Get contents of page
#headers part tells scraper to bring us English, based on above code
results = requests.get(url, headers = headers)

#Make content easier to read
soup = BeautifulSoup(results.text, "html.parser")

#print(soup.prettify())

#initialize empty lists for data storage
titles = []
years = []
time = []
imdb_ratings = []
metascores = []
votes = []
us_gross = []

#Find all lister-item mode-advanced divs
#find_all() method extracts all div containers that have a specified class
movie_div = soup.find_all('div', class_ = 'lister-item mode-advanced')


#for loop tells scraper to iterate through every div container stored
for container in movie_div:

    #Get name
    #.h3 and .a is the attr notation to access each of the tags
    #.text accesses the text nested in the <a> tag
    name = container.h3.a.text
    titles.append(name)

    #Get year of release
    year = container.h3.find('span', class_='lister-item-year').text
    years.append(year)

    #Get movie length
    #if container.p.find says if there's data then grab it, else put a dash instead
    runtime = container.find('span', class_='runtime').text if container.p.find('span', class_='runtime') else '-'
    time.append(runtime)

    #Get IMDb ratings
    #float() turns the text found into a float
    imdb = float(container.strong.text)
    imdb_ratings.append(imdb)

    #Get Metascore
    m_score = container.find('span', class_='metascore').text if container.find('span', class_='metascore') else '-'
    metascores.append(m_score)

    #Get votes and gross earnings
    #nv variable holds both the votes and gross <span> tags
    #nv[0] grabs first data in the list which are the votes
    #nv[1] grabs the second data in the list which are the gross
    #nv[1].text if len(nv) > 1 else ‘-’ says if the length of nv 
    #is greater than one, then find the second datum that’s stored. 
    #But if the data that’s stored in nv isn’t greater than one —
    #meaning if the gross is missing — then put a dash there
    nv = container.find_all('span', attrs = {'name': 'nv'})
    vote = nv[0].text
    votes.append(vote)

    grosses = nv[1].text if len(nv) > 1 else '-'
    us_gross.append(grosses)

#Print out data in a more readable manner
movies = pd.DataFrame({
'movie': titles,
'year': years,
'timeMin': time,
'imdb': imdb_ratings,
'metascore': metascores,
'votes': votes,
'us_grossMillions': us_gross,
})

#print(movies.dtypes)
#(‘(\d+’) says to extract all the digits in the string
movies['year'] = movies['year'].str.extract('(\d+)').astype(int)

movies['timeMin'] = movies['timeMin'].str.extract('(\d+)').astype(int)

movies['metascore'] = movies['metascore'].astype(int)

movies['votes'] = movies['votes'].str.replace(',', '').astype(int)

#movies[‘us_grossMillions’] tells pandas to go to the column us_grossMillions 
#.map() function calls the specified function for each item of an iterable
#lambda x: x is an anonymous functions in Python (one without a name). 
#Normal functions are defined using the def keyword.
#lstrip(‘$’).rstrip(‘M’) is our function arguments. This tells our function to 
#strip the $ from the left side and strip the M from the right side.
#pd.to_numeric is a method we can use to change this column to a float.
#errors=’coerce’ will transform the nonnumeric values, our dashes, into NaN (not-a-number )values

movies['us_grossMillions'] = movies['us_grossMillions'].map(lambda x: x.lstrip('$').rstrip('M'))

movies['us_grossMillions'] = pd.to_numeric(movies['us_grossMillions'], errors='coerce')

movies.to_csv('movies.csv')