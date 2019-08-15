# get dependencies 
# ----------------------------------------------------------
import pandas as pd
import geopandas as gpd
import simplejson
import pycountry
import dill
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LogColorMapper, LogTicker, ColorBar, Panel, Tabs, HoverTool, ZoomInTool, ZoomOutTool, ResetTool, BoxZoomTool, PanTool
from bokeh.palettes import cividis
# ----------------------------------------------------------

# Fridays for Future protests dataset
# -----------------------------------
def map_data():

	# get protests data
	protests = pd.read_csv('data/eventmap_data.csv', sep=',', skiprows=1)
	protests_df = protests['Country'].to_frame()
	protests_df = protests_df.rename(columns={'Country': 'name'})

	# get map shapefile for country codes and plotting
	shapefile = 'data/vis/ne_110m_admin_0_countries.shp'
	geo_df = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
	geo_df.columns = ['name', 'code', 'geometry']
	geo_nc = geo_df[['name', 'code']]

	# merge protests data and geo country+code data 
	prot_geo_nc = protests_df.merge(geo_nc, on='name', how='left')
	prot_geo_nc = prot_geo_nc.set_index('name')

	# ----- let's do a little cleaning -----

	# use pycountry to map unmapped countries to codes
	countries = {}
	for country in pycountry.countries:
	    countries[country.name] = country.alpha_3
	countries_df = pd.DataFrame.from_dict(countries, orient='index')

	missing = prot_geo_nc[pd.isnull(prot_geo_nc['code'])].index.unique()
	for i in missing:
	    if i in countries_df.index:
	        prot_geo_nc.loc[i,'code'] = countries_df.loc[i,0]

	# quick fix for the remaining missing mappings
	prot_geo_nc.loc['UK','code'] = 'GBR'
	prot_geo_nc.loc['Tanzania','code'] = 'TZA'
	prot_geo_nc.loc['USA','code'] = 'USA'
	prot_geo_nc.loc["Macedonia (FYROM)",'code'] = 'MKD'
	prot_geo_nc.loc["Taiwan 545",'code'] = 'TWN'
	prot_geo_nc.loc["Taiwan 500",'code'] = 'TWN'
	prot_geo_nc.loc["Taiwan 950",'code'] = 'TWN'
	prot_geo_nc.loc["Taiwan 600",'code'] = 'TWN'
	prot_geo_nc.loc["Taiwan 251",'code'] = 'TWN'
	prot_geo_nc.loc["Taiwan 224",'code'] = 'TWN'
	prot_geo_nc.loc["Taiwan 970",'code'] = 'TWN'
	prot_geo_nc.loc["5300 Hungary",'code'] = 'HUN'
	prot_geo_nc.loc["7100 Hungary",'code'] = 'HUN'
	prot_geo_nc.loc["Myanmar (Burma)",'code'] = 'MMR'
	prot_geo_nc.loc["The Gambia",'code'] = 'GMB'
	prot_geo_nc.loc["Dubai - United Arab Emirates",'code'] = 'ARE'
	prot_geo_nc.loc["Kashmir",'code'] = 'IND'
	prot_geo_nc.loc["Jammu",'code'] = 'IND'
	prot_geo_nc.loc["Jammu and Kashmir 194101",'code'] = 'IND'       

	# ----- get the number of protests and add population data -----

	# get the number of protests
	prot_count = prot_geo_nc['code'].value_counts()
	prot_count = prot_count.to_frame()
	prot_count.reset_index(level=0, inplace=True)
	prot_count.columns = ['code', 'protest']

	# country population
	country_pop = dill.load(open('data/country_pop.pkd', 'rb'))
	cp_df = pd.DataFrame(list(country_pop.items()), columns = ['code', 'population'])
	prot_pop = prot_count.merge(cp_df, on='code', how='left')
	prot_pop['pop_tm'] = prot_pop['population']/10000000
	prot_pop['prot_ptm'] = prot_pop['protest']/prot_pop['pop_tm']      

	# prepare data for plotting
	prot_pop_geo = geo_df.merge(prot_pop, left_on = 'code', right_on = 'code', how = 'left')
	prot_pop_geo.fillna('No data', inplace = True)

	return prot_pop_geo, prot_pop

# Fridays for Future protests map
# -------------------------------
def map_create(prot_pop_geo, prot_pop):

	geosource = GeoJSONDataSource(geojson = simplejson.dumps(simplejson.loads(prot_pop_geo.to_json())))

	# ----- Raw count map -----

	# initialize figure
	palette = cividis(256)

	hover_a = HoverTool(tooltips = [ ('Country','@name'),('Protests', '@protest')])
	color_mapper_a = LogColorMapper(	palette = palette, 
									low = 1, high = prot_pop['protest'].max()+5, 
                          			nan_color = '#ffffff')
	color_bar_a = ColorBar(color_mapper=color_mapper_a, 
	                     ticker=LogTicker(),
	                     orientation = 'horizontal', 
	                     border_line_color=None, 
	                     location = (0,0), 
	                     label_standoff=8, 
	                     major_label_text_font = 'Raleway',
	                     major_label_text_font_size = '12pt',
	                     title = 'Number of registered Fridays for Future protests',
	                     title_text_font_style = 'normal', 
	                     title_text_font = 'Raleway', 
	                     title_text_font_size = '15pt')
	
	p_a = figure(title = 'The Fridays for Future movement grew to global scale within only 10 months',
				tools = [hover_a, ZoomInTool(), ZoomOutTool(), ResetTool(), PanTool()], 
				plot_height = 600, 
				plot_width = 980) 

	# add patch renderer 
	p_a.patches('xs','ys', source = geosource,fill_color = {'field' :'protest', 'transform' : color_mapper_a},
	          line_color = 'black', line_width = 0.25, fill_alpha = 1)

	# prettify
	p_a.xgrid.grid_line_color = None
	p_a.ygrid.grid_line_color = None
	p_a.outline_line_color = None
	p_a.axis.visible = False
	p_a.add_layout(color_bar_a, 'below')
	p_a.toolbar.logo = None 
	p_a.title.text_font = "Raleway"
	p_a.title.text_font_style = "normal"
	p_a.title.align='center'
	p_a.title.text_color='black'
	p_a.title.text_font_size = '20pt'

	tab_a = Panel(child=p_a, title="Absolute number")

	# ----- Population adjusted count map -----

	# initialize figure 
	hover_b = HoverTool(tooltips = [ ('Country','@name'), ('Protests per 10 million', '@prot_ptm'), ('Protests', '@protest'), ('Population', '@population')])
	color_mapper_b = LogColorMapper(palette = palette, 
									low = prot_pop['prot_ptm'].min(), 
									high = float(prot_pop.loc[prot_pop['code'] == 'GRL']['prot_ptm'])+10,
                          			nan_color = '#ffffff')
	color_bar_b = ColorBar(color_mapper=color_mapper_b, 
	                     ticker=LogTicker(),
	                     orientation = 'horizontal', 
	                     border_line_color=None, 
	                     location = (0,0), 
	                     label_standoff=8, 
	                     major_label_text_font = 'Raleway',
	                     major_label_text_font_size = '12pt',
	                     title = 'Number of registered Fridays for Future protests per 10 million',
	                     title_text_font_style = 'normal', 
	                     title_text_font = 'Raleway', 
	                     title_text_font_size = '15pt')
	
	p_b = figure(title = 'The Fridays for Future movement grew to global scale within only 10 months',
				tools = [hover_b, ZoomInTool(), ZoomOutTool(), ResetTool(), PanTool()], 
				plot_height = 600, 
				plot_width = 980) 

	# add patch renderer 
	p_b.patches('xs','ys', source = geosource,fill_color = {'field' :'prot_ptm', 'transform' : color_mapper_b},
	          line_color = 'black', line_width = 0.25, fill_alpha = 1)

	# prettify
	p_b.xgrid.grid_line_color = None
	p_b.ygrid.grid_line_color = None
	p_b.outline_line_color = None
	p_b.axis.visible = False
	p_b.add_layout(color_bar_b, 'below')
	p_b.toolbar.logo = None 
	p_b.title.text_font = "Raleway"
	p_b.title.text_font_style = "normal"
	p_b.title.align='center'
	p_b.title.text_color='black'
	p_b.title.text_font_size = '20pt'

	tab_b = Panel(child=p_b, title="Population normalized")

	tabs = Tabs(tabs=[tab_a, tab_b])

	return tabs