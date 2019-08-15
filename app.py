# get dependencies 
# ----------------------------------------------------------
import simplejson
#import os
from flask import Flask, render_template, request, redirect
from bokeh.resources import CDN
from bokeh.embed import json_item 
from fff_map import map_data, map_create
from fff_twitter import tw_daily_data, tw_daily_create, tw_hourly_data, tw_hourly_create, tw_nlp_data, tw_nlp_create
# ----------------------------------------------------------

# initialize tell-me-about-fff
# ----------------------------
tellmetaboutfff = Flask(__name__)

# take me to...
# -------------
@tellmetaboutfff.route('/', methods=['GET'])
def page1():
	return render_template('one.html')

@tellmetaboutfff.route('/two', methods=['GET'])
def page2():
    return render_template('two.html')

@tellmetaboutfff.route('/three', methods=['GET'])
def page3():
	return render_template('three.html', resources=CDN.render())

@tellmetaboutfff.route('/four', methods=['GET'])
def page4():
	return render_template('four.html')

@tellmetaboutfff.route('/five', methods=['GET'])
def page5():
	return render_template('five.html', resources=CDN.render())	

@tellmetaboutfff.route('/six', methods=['GET'])
def page6():
	return render_template('six.html', resources=CDN.render())

@tellmetaboutfff.route('/seven', methods=['GET'])
def page7():
	return render_template('seven.html', resources=CDN.render())	

@tellmetaboutfff.route('/eight', methods=['GET'])
def page8():

	return render_template('eight.html', resources=CDN.render())

@tellmetaboutfff.route('/nine', methods=['GET'])
def page9():

	return render_template('nine.html', resources=CDN.render())		

# create visualizations to embed 
# ------------------------------
@tellmetaboutfff.route('/plot_map')
def create_map():

	prot_pop_geo, prot_pop = map_data()
	maptabs = map_create(prot_pop_geo, prot_pop)

	return simplejson.dumps(json_item(maptabs, "map"))

@tellmetaboutfff.route('/plot_tw_daily')
def create_twd():

	daily_count_df, daily_count_avg_df = tw_daily_data()
	tw_daily = tw_daily_create(daily_count_df, daily_count_avg_df)

	return simplejson.dumps(json_item(tw_daily, "tw_daily"))

@tellmetaboutfff.route('/plot_tw_hourly')
def create_twh():

	hourly_count_avg_df = tw_hourly_data()
	tw_hourly = tw_hourly_create(hourly_count_avg_df)

	return simplejson.dumps(json_item(tw_hourly, "tw_hourly"))

@tellmetaboutfff.route('/plot_tw_nlp')
def create_twn():

	words_p, pop_p, pop_p_unique, words_np, pop_np, pop_np_unique = tw_nlp_data()
	tw_nlp = tw_nlp_create(words_p, pop_p, pop_p_unique, words_np, pop_np, pop_np_unique)

	return simplejson.dumps(json_item(tw_nlp, "tw_nlp"))

# call the application
# --------------------
#if __name__ == "__main__":
#	port = int(os.environ.get("PORT", 5000))
#	tellmetaboutfff.run(host='0.0.0.0', port=port)
if __name__ == '__main__':
	app.run(port=33507)		



