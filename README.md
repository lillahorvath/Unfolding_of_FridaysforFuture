## Unfolding of Fridays for Future project

This repo contains the code and data behind the visual storytelling [project](https://unfolding-fridaysforfuture.herokuapp.com) about the unfolding of the remarkable environmental movement Fridays for Future. The project was part of [The Data Incubator](https://www.thedataincubator.com) Data Science Fellowship Program (June-August 2019). The goal of this project was to demonstrate

  * A clear business objective: The Fridays for Future environmental movement grew to global scale within only months achieving unparalleled success in channeling public support against climate change.  In this project, I analyzed the representation of the movement on Twitter to gain actionable insights into how to navigate an impactful environmental campaign.

  * Data ingestion: I used two data sources for this project. For the spatial analysis I obtained information about the registered protests from the official Fridays for Future [website](https://www.fridaysforfuture.org) (dataset available for download as .csv) and subsequently conducted data wrangling using python's pycountry module. For the temporal and language analyses I used Twitter’s API together with python's requests module to acquire tweets with the hashtag #FridaysForFuture. To prepare the tweets for natural language processing I conducted regex-based cleaning. 
  
  * Visualizations: I used Bokeh to generate interactive figures including maps, line and bar (horizontal and vertical) plots. 
  
  * Machine Learning: To identify the main differences in the language of the 5000 most and 5000 least popular tweets with the hashtag #FridaysForFuture I implemented the bag-of-words model together with lemma-based tokenization using Scikit-learn and Spacy.
   
  * Interactive Website - Deliverable: The finished [web application](https://unfolding-fridaysforfuture.herokuapp.com) is deployed to Heroku. Visitors of the homepage are guided through a series of interactive visualizations to explore the key factors in the success of the movement, such as synchronization and periodicity, targeted timing and proactive, on-message language. 
  
This project was selected for an oral presentation at Pitch Night on August 8 2019.


