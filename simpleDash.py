#!/bin/env python

# This is a simple example of a streamlit dashboard.
# I make no claim that it's particularly good, since it's
# my first, but it may be a good starting point for
# developing streamlit dashboards.
#
# What is done here is to get some JSON data that we already
# have from an existing server that feeds browser plugins
# and use that JSON to make a dashboard.
#
# To get it going I did this :
#  Made a virtual environment and installed the required modules,
#  so something like :
#  $ python -m venv /home/noien/simpleStreamLitDash/virtEnv
#  $ source /home/noien/simpleStreamLitDash/virtEnv/bin/activate
#  $ pip install --upgrade pip
#  $ pip install requests streamlit
#
# Then cd to this directory with the simpleDash.py script in it, and :
# $ streamlit run ./simpleDash.py
# That runs it in dev mode (it brings up the server and points
# your default browser at it, somewhat comparable to flask).
#
# In this directory we have :
#  .streamlit/config.toml  <---- General config, colors, fonts etc in HIDDEN dir
#  icons/day.png           +
#  icons/night.png         + <-- Icon images
#  icons/questionMark.png  +
#  icons/cross.png         +
#  simpleDash.py  <------------- This file
#  requirements.txt <--- resulted from $ pip freeze > requirements.txt
#
# See also https://streamlit.io
#
# Niles Oien noien@nso.edu July 2024.
#

import requests
import streamlit as st

import math
import time
from datetime import datetime, timezone

# Function to return a full name given a single character site code
def getFullName( siteCode ) :

 if siteCode == "M" :
  return "Mauna Loa, HI, United States"
 if siteCode == "B" :
  return "Big Bear, CA, United States"
 if siteCode == "C" :
  return "Cerro Tololo, Chile"
 if siteCode == "Z" :
  return "Boulder, CO, United States"
 if siteCode == "L" :
  return "Learmonth, Australia"
 if siteCode == "U" :
  return "Udaipur, India"
 if siteCode == "T" :
  return "El Tiede, Spain"

 return siteCode;


# Function to return a string interval description given the age in seconds.
def getAgeString( age ) :

 if age < 60 :
  return str(age) + " Seconds"

 if age < 3600 :
  minutes = math.floor(age/60.0)
  seconds = age % 60;
  return str(minutes) + " Minutes " + str(seconds) + " Seconds"

 if age < 86400 :
  hours = math.floor(age/3600.0)
  minutes = round((age % 3600) / 60)
  return str(hours) + " Hours " + str(minutes) + " Minutes";

 if age >= 86400*10 : # Ten days old means no data found
  return "No recent data"

 days = math.floor(age/86400.0)
 hours = round((age % 86400) / 3600);
 return str(days) + " Days " + str(hours) + " Hours";


#### Main program starts ####

# Get a placeholder container (pc)
# and set the title to "Loading" while the JSON comes in.
pc = st.empty()
pc.title("Loading...")

# Then enter the eternal loop of getting JSON updates
# and putting the JSON in our streamlit app web page
while True :

 # Get the JSON from the server and clear out the old stuff (ie the last report)
 data = requests.get('https://gong2.nso.edu/products/hAlphaLatest/hac.php').json()
 pc.empty()

 # The following line is a big deal, needed for
 # pc.empty() to clear out the old stuff on update.
 with pc.container() :

  # Build the page from the JSON. Title first.
  st.title('GONG H-Alpha Dashboard')

  # JSON is something like this (the header part is optional as there is a default) :
  #
  # {"message":" GONG <A HREF="https://monitor.nso.edu">status</a> monitor",
  #  "siteInfo":[
  #    {"movieURL":"https://gong2.nso.edu/products/scaleViewTest/view.php?configFile=configs/hAlphaColor.cfg&productIndex=3",
  #     "imageLink":"https://gong2.nso.edu/HA/hac/202211/20221102/20221102145712Ch.jpg",
  #     "age":242,
  #     "siteCode":"C"},
  #    {"movieURL":"https://gong2.nso.edu/products/scaleViewTest/view.php?configFile=configs/hAlphaColor.cfg&productIndex=2",
  #     "imageLink":"https://gong2.nso.edu/HA/hac/202211/20221102/20221102145652Th.jpg",
  #     "age":262,
  #     "siteCode":"T"}
  #  ]} 
  #
  # Ages are measured in seconds. Data are sorted into order of ascending age.

  # Add a column header line. The two stars in the text mean bold text.
  # The list of numbers is the relative size of the columns.
  col1, col2, col3, col4, col5 = st.columns([2,5,5,3,3], vertical_alignment="center")
  col1.write("**Status**")
  col2.write("**Site**")
  col3.write("**Data age**")
  col4.write("**Latest Image**")
  col5.write("**Movie Page**")

  # Put together the content from the JSON from the server.
  # Loop through the site info entries in the JSON (now a dictionary).
  for item in data['siteInfo'] :

   # Select the correct icon based on age.
   displayImage='icons/day.png'
   if item['age'] > 3600 :
    displayImage='icons/night.png'
   if item['age'] >= 3 * 86400 :
    displayImage='icons/questionMark.png'
   if item['age'] >= 10 * 86400 :
    displayImage='icons/cross.png'

   # Important to get columns inside the loop so that each
   # row is a new set of columns.
   col1, col2, col3, col4, col5 = st.columns([2,5,5,3,3], vertical_alignment="center")
   col1.image(displayImage)
   col2.write(getFullName(item['siteCode']))
   col3.write(getAgeString(item['age']))
   if item['imageLink'] == 'NONE' :
    col4.write(' ')
   else :
    col4.page_link(item['imageLink'], label="Image link")

   if item['movieURL'] == 'NONE' :
    col5.write(' ')
   else :
    col5.page_link(item['movieURL'], label="Movie link")

  # Add the footer message. This is actually HTML so use st.html()
  # st.divider()
  st.html("<P>" + data['message'] + "</p>")
  # st.divider()

  # Get the current time so we can note it on the page.
  theTime = datetime.now(timezone.utc)
  tmStr=theTime.strftime("%Y/%m/%d %H:%M:%S %Z")

  # Add a countdown clock to the next update.
  tickingClock = st.empty()
  for i in range(60,0,-1) :
   tickingClock.empty()
   tickingClock.write("Last updated " + tmStr + ", next update in " + str(i) + " seconds")
   time.sleep(1)
  tickingClock.empty()
  tickingClock.write("Updating...")

# Because we looped eternally we never actually get to quit() but
# I'll leave it here to indicate The End.

quit()

