# get dependencies 
# ----------------------------------------------------------
import pandas as pd
import dill
import numpy as np
from numpy import linspace
from scipy.stats.kde import gaussian_kde
from bokeh.models import HoverTool, ColumnDataSource, Span
from bokeh.layouts import row
from bokeh.plotting import figure
# ----------------------------------------------------------

# daily tweets count
# ------------------
def tw_daily_data():

	# get daily hashtag counts data
	daily_count = [dill.load(open('data/twitter/res_{}.pkd'.format(i), 'rb'))['results'] for i in range(10,0, -1)]

	# create df and add day and moving average columns
	daily_count_df = pd.DataFrame([y for x in daily_count for y in x])
	daily_count_df['timePeriod'] = pd.to_datetime(daily_count_df['timePeriod'], format='%Y%m%d%H%M')
	daily_count_df['day'] = daily_count_df['timePeriod'].dt.day_name()
	daily_count_df['ra_count'] = daily_count_df['count'].rolling(14).mean()

	# average tweets per day
	daily_count_avg_df = daily_count_df.groupby('day').mean().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']) 

	return daily_count_df, daily_count_avg_df

# hourly tweets count 
# -------------------
def tw_hourly_data():

	# get hourly hashtag counts data
	hourly_count_df = pd.DataFrame(dill.load(open('data/twitter/tph.pkd', 'rb'))['results'])
	hourly_count_df['hours'] = [int(i[-4:-2]) for i in list(hourly_count_df['timePeriod'])]
	hourly_count_avg_df = hourly_count_df[['hours', 'count']].groupby('hours').mean()

	return hourly_count_avg_df

# tweets nlp
# ----------
def tw_nlp_data():

	# get NLP results data
	list_words_p,popscore_p,list_words_np,popscore_np = dill.load(open('data/twitter/words_pop.pkd', 'rb'))

	words_pop_p = [[list_words_p[i][0], popscore_p[i]] for i in range(len(list_words_p))]
	words_pop_np = [[list_words_np[i][0], popscore_np[i]] for i in range(len(list_words_np))]

	words_pop_sorted_p = sorted(words_pop_p, key=lambda x: (-x[1], x[0]))
	words_pop_sorted_np = sorted(words_pop_np, key=lambda x: (-x[1], x[0]))

	words_to_plot_p = [words_pop_sorted_p[0]] + words_pop_sorted_p[2:11] 
	words_p = [i[0]for i in words_to_plot_p]
	pop_p = [i[1]for i in words_to_plot_p]

	words_to_plot_np = words_pop_sorted_np[1:3] + words_pop_sorted_np[4:12] 
	words_np = [i[0]for i in words_to_plot_np]
	pop_np = [i[1]for i in words_to_plot_np]

	# create lists with counts of unique words
	pop_p_unique = []
	for word, num in zip(words_p, pop_p):
	    if word in ('action, join, young'):
	        pop_p_unique.append(num)
	    else:
	        pop_p_unique.append(0)

	pop_np_unique = []
	for word, num in zip(words_np, pop_np):
		    if word in ('new, help, need'):
		        pop_np_unique.append(num)
		    else:
		        pop_np_unique.append(0)         

	return words_p, pop_p, pop_p_unique, words_np, pop_np, pop_np_unique

# daily tweets count - vis
# ------------------------
def tw_daily_create(daily_count_df, daily_count_avg_df):

	# ----- Daily count ----- 

	# initialize figure
	daily_count_tp = ColumnDataSource(daily_count_df)
	hover_a = HoverTool(tooltips = [('Day','@day'),('Date', '@timePeriod{%Y-%m-%d}'), ('Tweets','@count')], 
	                  formatters={'timePeriod': 'datetime','height' : 'printf'}, toggleable=False) 

	p_a = figure(title=" ", 
	            x_axis_label='Date', 
	            x_axis_type='datetime',
	            tools = [hover_a],
	            y_axis_label='Tweets with #FridaysForFuture',
	            y_axis_type="log", 
	            plot_width=750, plot_height=500)

	# add data lines
	rd = p_a.line(x = 'timePeriod', y = 'count', line_color='grey', line_alpha=0.6, source=daily_count_tp)  
	p_a.line(x = 'timePeriod', y = 'ra_count', line_color='black', source=daily_count_tp, line_width=3, line_alpha=0.5)
	start = Span(location=daily_count_df.loc[14, 'timePeriod'], dimension='height', line_color='red', line_dash='dotted', line_width=3, line_alpha=0.5)
	p_a.add_layout(start)

	# prettify
	p_a.title.text_font = "Raleway"
	p_a.title.text_font_style = "normal"
	p_a.title.align='center'
	p_a.title.text_color='black'
	p_a.title.text_font_size = '18pt'
	p_a.xaxis.axis_label_text_font_style = "normal" 
	p_a.xaxis.axis_label_text_font = "Raleway"
	p_a.yaxis.axis_label_text_font_style = "normal" 
	p_a.yaxis.axis_label_text_font = "Raleway"
	p_a.yaxis.axis_label_text_font_size = '15pt'
	p_a.xaxis.axis_label_text_font_size = '15pt'
	p_a.xaxis.major_label_text_font = 'Raleway'
	p_a.xaxis.major_label_text_font_size = '12pt'
	p_a.yaxis.major_label_text_font = 'Raleway'
	p_a.yaxis.major_label_text_font_size = '12pt'
	p_a.ygrid.grid_line_alpha = 0.8
	p_a.xgrid.grid_line_alpha = None
	p_a.yaxis.minor_tick_line_color = None 
	hover_a.renderers =[rd]
	p_a.toolbar_location = 'left'
	p_a.toolbar.logo = None
	p_a.outline_line_color = None 

	# ----- Daily average -----  

	# initialize figure
	p_b = figure( x_range = list(daily_count_avg_df.index), 
				y_axis_label='Average number of tweets',
        		plot_width=300, 
        		plot_height=500, 
        		tools = '')

	# add data vbars
	p_b.vbar(x=daily_count_avg_df.index, top=daily_count_avg_df['count'], width=0.9, alpha=0.4, line_color = '#1A96F8', fill_color = '#1A96F8')   

	# prettify
	p_b.xaxis.axis_label_text_font_style = "normal" 
	p_b.xaxis.axis_label_text_font = "Raleway"
	p_b.yaxis.axis_label_text_font_style = "normal" 
	p_b.yaxis.axis_label_text_font = "Raleway"
	p_b.yaxis.axis_label_text_font_size = '15pt'
	p_b.xaxis.axis_label_text_font_size = '15pt'
	p_b.xaxis.major_label_text_font = 'Raleway'
	p_b.xaxis.major_label_text_font_size = '12pt'
	p_b.yaxis.major_label_text_font = 'Raleway'
	p_b.yaxis.major_label_text_font_size = '12pt'
	p_b.ygrid.grid_line_alpha = 0.8
	p_b.xgrid.grid_line_alpha = None
	p_b.yaxis.minor_tick_line_color = None
	p_b.x_range.range_padding = 0.1
	p_b.xaxis.major_label_orientation = 0.9
	p_b.outline_line_color = None
	p_b.toolbar.logo = None
	p_b.toolbar_location = None

	return row(p_a, p_b)

# hourly tweets count - vis
# -------------------------
def tw_hourly_create(hourly_count_avg_df):

	# Gaussian kernel density estimation 
	norm_c = np.array(hourly_count_avg_df['count'])/np.array(hourly_count_avg_df['count'].sum())
	w1 = [int(i)*[ind] for ind,i in enumerate(list(hourly_count_avg_df['count']))]
	w2 = [k for j in w1 for k in j]
	pdf = gaussian_kde(pd.Series(w2))

	# initialize figure
	norm_c_df = ColumnDataSource(pd.DataFrame(norm_c, columns = ['prob']))
	hover = HoverTool(tooltips = [('Hour','@index')], toggleable=False)
	p = figure(title = " ",
             plot_width=600, 
             plot_height=500, 
             tools = [hover])

	# add data vbars
	b = p.vbar(x='index', top='prob', width=0.6, alpha=0.2, line_color = '#1A96F8', fill_color = '#1A96F8', source=norm_c_df)
	p.line(linspace(0,23), pdf(linspace(0,23)), line_width=4, alpha = 0.8, line_color = '#1A96F8')  

	# prettify
	p.xaxis.axis_label_text_font_style = "normal" 
	p.xaxis.axis_label_text_font = "Raleway"
	p.yaxis.axis_label_text_font_style = "normal" 
	p.yaxis.axis_label_text_font = "Raleway"
	p.yaxis.axis_label_text_font_size = '15pt'
	p.xaxis.axis_label_text_font_size = '15pt'
	p.xaxis.major_label_text_font = 'Raleway'
	p.xaxis.major_label_text_font_size = '12pt'
	p.yaxis.major_label_text_font = 'Raleway'
	p.yaxis.major_label_text_font_size = '12pt'
	p.ygrid.grid_line_alpha = 0.8
	p.xgrid.grid_line_alpha = None
	p.yaxis.minor_tick_line_color = None
	p.x_range.range_padding = 0.1
	p.outline_line_color = None
	p.xaxis.minor_tick_line_color = None
	p.xaxis.axis_label = "Hour"
	p.yaxis.axis_label = "Probability of tweets"
	p.toolbar.logo = None
	p.toolbar_location = None
	hover.renderers =[b]	
	p.title.text_font = "Raleway"
	p.title.text_font_style = "normal"
	p.title.align='center'
	p.title.text_color='black'
	p.title.text_font_size = '18pt'

	return p

# tweets nlp - vis
# ----------------
def tw_nlp_create(words_p, pop_p, pop_p_unique, words_np, pop_np, pop_np_unique):

	# initialize figure
	p_a = figure(plot_width=500, plot_height=500, title="Most popular tweets", 
				toolbar_location=None, y_range=words_p[::-1], x_range=(0, max(pop_p)+1))

	# add data hbars
	p_a.hbar(y=words_p[::-1], left=0, right=pop_p[::-1], height=0.5, color='#1A96F8', alpha=0.2)
	p_a.hbar(y=words_p[::-1], left=0, right=pop_p_unique[::-1], height=0.5, color='#1A96F8', alpha=0.6)

	# prettify
	p_a.xaxis.axis_label_text_font_style = "normal" 
	p_a.yaxis.axis_label_text_font_style = "normal" 
	p_a.xaxis.axis_label_text_font = "Raleway"
	p_a.yaxis.axis_label_text_font = "Raleway"
	p_a.yaxis.axis_label_text_font_size = '15pt'
	p_a.xaxis.axis_label_text_font_size = '15pt'
	p_a.xaxis.major_label_text_font = 'Raleway'
	p_a.xaxis.major_label_text_font_size = '12pt'
	p_a.yaxis.major_label_text_font = 'Raleway'
	p_a.yaxis.major_label_text_font_size = '12pt'
	p_a.xgrid.grid_line_alpha = 0.8
	p_a.ygrid.grid_line_alpha = None
	p_a.xaxis.minor_tick_line_color = None
	p_a.y_range.range_padding = 0.1
	p_a.outline_line_color = None
	p_a.xaxis.minor_tick_line_color = None
	p_a.xaxis.axis_label = "Number of occurrences"
	p_a.title.text_font = "Raleway"
	p_a.title.text_font_style = "normal"
	p_a.title.align='center'
	p_a.title.text_color='black'
	p_a.title.text_font_size = '18pt'

	# initialize figure
	p_b = figure(plot_width=500, plot_height=500, title="Least popular tweets",
	           toolbar_location=None, y_range=words_np[::-1], x_range=(0, max(pop_p)+1))

	# add data hbars
	p_b.hbar(y=words_np[::-1], left=0, right=pop_np[::-1], height=0.5, color='#FC2A1C', alpha=0.2)
	p_b.hbar(y=words_np[::-1], left=0, right=pop_np_unique[::-1], height=0.5, color='#FC2A1C', alpha=0.6)

	# prettify
	p_b.xaxis.axis_label_text_font_style = "normal" 
	p_b.yaxis.axis_label_text_font_style = "normal" 
	p_b.xaxis.axis_label_text_font = "Raleway"
	p_b.yaxis.axis_label_text_font = "Raleway"
	p_b.yaxis.axis_label_text_font_size = '15pt'
	p_b.xaxis.axis_label_text_font_size = '15pt'
	p_b.xaxis.major_label_text_font = 'Raleway'
	p_b.xaxis.major_label_text_font_size = '12pt'
	p_b.yaxis.major_label_text_font = 'Raleway'
	p_b.yaxis.major_label_text_font_size = '12pt'
	p_b.xgrid.grid_line_alpha = 0.8
	p_b.ygrid.grid_line_alpha = None
	p_b.xaxis.minor_tick_line_color = None
	p_b.y_range.range_padding = 0.1
	p_b.outline_line_color = None
	p_b.xaxis.minor_tick_line_color = None
	p_b.xaxis.axis_label = "Number of occurrences"
	p_b.title.text_font = "Raleway"
	p_b.title.text_font_style = "normal"
	p_b.title.align='center'
	p_b.title.text_color='black'
	p_b.title.text_font_size = '18pt'

	return row(p_a, p_b)






