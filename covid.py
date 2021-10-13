import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

#github links to datasets
url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

confirmed = pd.read_csv(url_confirmed)
deaths = pd.read_csv(url_deaths)
recovered = pd.read_csv(url_recovered)
#unpivot the data
date1 = confirmed.columns[4:]
total_confirmed = confirmed.melt(id_vars = ['Province/State','Country/Region','Lat','Long'],value_vars = date1,var_name = 'date',value_name = 'confirmed')

date2 = deaths.columns[4:]
total_deaths = deaths.melt(id_vars = ['Province/State','Country/Region','Lat','Long'],value_vars = date2,var_name = 'date',value_name = 'deaths')

date3 = recovered.columns[4:]
total_recovered = recovered.melt(id_vars = ['Province/State','Country/Region','Lat','Long'],value_vars = date3,var_name = 'date',value_name = 'recovered')

#combining dataframes together
covid_data = total_confirmed.merge(right= total_deaths, how = 'left',on = ['Province/State','Country/Region','Lat','Long','date'])
covid_data = covid_data.merge(right= total_recovered, how = 'left',on = ['Province/State','Country/Region','Lat','Long','date'])

#change date format
covid_data['date'] = pd.to_datetime(covid_data['date'])

#fill NA's for recovered column
covid_data['recovered'] = covid_data['recovered'].fillna(0)

#new column named active
covid_data['active'] = covid_data['confirmed'] - covid_data['deaths'] - covid_data['recovered']

# new df for group by date
covid_data_2 = covid_data.groupby(['date'])[['confirmed','deaths','recovered','active']].sum().reset_index()

#create dict of list for map
covid_data_list = covid_data[['Country/Region','Lat','Long']]
dict_of_locations = covid_data_list.set_index('Country/Region')[['Lat','Long']].T.to_dict('dict')


#now we create dashapp
app = dash.Dash(__name__, meta_tags=[{"name":"viewport", "content": "width=device-width"}])

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('covid19Logo.jpg'),id = 'corona-logo',style={'height': '60px','width':'auto','margin-bottom':'25px'})

        ],className='one-third column'),
        html.Div([
            html.Div([
                html.H3('Covid-19',style={'margin-bottom':'0px','color':'white'}),
                html.H5('Track Covid-19 Cases',style={'margin-bottom':'0px','color':'white'})
            ])

        ],className='one-half column',id='title'),

        html.Div([
            html.H6('Last Updated: '+ str(covid_data['date'].iloc[-1].strftime('%B %d, %Y'))+ ' 00:01 (UTC)', style={'color':'orange'})
        ],className= 'one-third column', id='title1')

    ], id = 'header', className='row flex-display',style={'margin-bottom':'25px'}),
    #2nd row
    html.Div([
        html.Div([
            html.H6(children='Global Cases', style={'text-align':'center','color':'white'}),
            html.P(f"{covid_data_2['confirmed'].iloc[-1]:,.0f}",
                   style={'text-align':'center','color':'orange','fontSize':'3vw'}),
            html.P('new: ' + f"{covid_data_2['confirmed'].iloc[-1] - covid_data_2['confirmed'].iloc[-2]:,.0f}" + ' (' + str(round(((covid_data_2['confirmed'].iloc[-1] - covid_data_2['confirmed'].iloc[-2])/(covid_data_2['confirmed'].iloc[-1]))*100,2))+'%)',
                   style={'text-align':'center','color':'orange','fontSize':15,'margin-top':'-18px'})

        ],className='card_container three columns'),
        #Column 2
        html.Div([
                    html.H6(children='Global Deaths', style={'text-align':'center','color':'white'}),
                    html.P(f"{covid_data_2['deaths'].iloc[-1]:,.0f}",
                           style={'text-align':'center','color':'red','fontSize':'3vw'}),
                    html.P('new: ' + f"{covid_data_2['deaths'].iloc[-1] - covid_data_2['deaths'].iloc[-2]:,.0f}" + ' (' + str(round(((covid_data_2['deaths'].iloc[-1] - covid_data_2['deaths'].iloc[-2])/(covid_data_2['deaths'].iloc[-1]))*100,2))+'%)',
                            style={'text-align':'center','color':'red','fontSize':15,'margin-top':'-18px'})

                ],className='card_container three columns'),
        #column 3
        html.Div([
            html.H6(children='Global Recovered', style={'text-align': 'center', 'color': 'white'}),
            html.P(f"{covid_data_2['recovered'].iloc[560]:,.0f}",
                   style={'text-align': 'center', 'color': 'green', 'fontSize': '3vw'})

        ], className='card_container three columns'),

        #Column 4
        html.Div([
                    html.H6(children='Global Active', style={'text-align':'center','color':'white'}),
                    html.P(f"{covid_data_2['active'].iloc[-1]:,.0f}",
                           style={'text-align':'center','color':'#e55467','fontSize':'3vw'}),
                    html.P('new: ' + f"{covid_data_2['active'].iloc[-1] - covid_data_2['active'].iloc[-2]:,.0f}" + ' (' + str(round(((covid_data_2['active'].iloc[-1] - covid_data_2['active'].iloc[-2])/(covid_data_2['active'].iloc[-1]))*100,2))+'%)',
                            style={'text-align':'center','color':'#e55467','fontSize':15,'margin-top':'-18px'})

                ],className='card_container three columns')

    ],className= 'row flex display'),
    #third row
    html.Div([
        html.Div([
            html.P('Select Country',className='fix_label',style={'color':'white'}),
            #add dropdown now
            dcc.Dropdown(id= 'w_countries',multi=False,searchable=True,value='US',placeholder='Select Country',
                         options=[{'label': c,'value':c}
                            for c in (covid_data['Country/Region'].unique())],className='dcc_compon'),
            #add kpi1 to second column position
            html.P('New Cases: '+' '+str(covid_data['date'].iloc[-1].strftime('%B %d, %Y')),className='fix_label',style={'text-align':'center','color':'white'}),
            #add graph
            dcc.Graph(id='confirmed', config={'displayModeBar':False},className='dcc_compon',style={'margin-top':'20px'}) ,
            #create new graph
            dcc.Graph(id='deaths', config={'displayModeBar':False},className='dcc_compon',style={'margin-top':'20px'}),
            # create new graph
            dcc.Graph(id='recovered', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'}),
            dcc.Graph(id='active', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'})

        ],className='create_container three columns'),

        #second column donut chart
        html.Div([
            #pie chart
            dcc.Graph(id='pie_chart',config={'displayModeBar':'hover'})

        ],className='create_container four columns'),

        # third column line/bar chart
        html.Div([
            # line/bar chart
            dcc.Graph(id='line_chart', config={'displayModeBar': 'hover'})
        #!!!!there are 12 columns in one row, this one is 5, pie is 4, Kpi is 3
        ], className='create_container five columns'),

    ],className='row flex display'),

    #fourth row
    html.Div([
        # third row map chart
        html.Div([
            # map chart
            dcc.Graph(id='map_chart', config={'displayModeBar': 'hover'})
            # !!!!there are 12 columns in one row, this one is 5, pie is 4, Kpi is 3
        ], className='create_container twelve columns',id='map')

    ],className='row flex-display')

],id= 'mainContainer',style={'display':'flex','flex-direction':'column'})

#anytime we want to get user input to update/filter the graphs we need to create a callback
@app.callback(Output('confirmed','figure'),[Input('w_countries','value')])

def update_confirmed(w_countries):
    covid_data_by_country = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'deaths', 'recovered', 'active']].sum().reset_index()
    value_confirmed = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['confirmed'].iloc[-1] - covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['confirmed'].iloc[-2]
    delta_confirmed = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['confirmed'].iloc[-2] - covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['confirmed'].iloc[-3]


    return {
       'data': [go.Indicator(
           mode='number+delta',
           value=value_confirmed,
           delta={'reference': delta_confirmed,'position': 'right','valueformat':'g','relative':False,'font':{'size':15}},
           number= {'valueformat': ',','font':{'size':20}},
           domain= {'y':[0,1], 'x':[0,1]}
       )],

        'layout':go.Layout(
           title={'text':'New Confirmed:',
                  'y':0.98,'x':0.5,'xanchor':'center','yanchor':'top'},
            height= 50,
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor= '#1f2c56'
            )
        }

#app call back for deaths
@app.callback(Output('deaths','figure'),[Input('w_countries','value')])

def update_confirmed(w_countries):
    covid_data_by_country = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'deaths', 'recovered', 'active']].sum().reset_index()
    value_confirmed = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['deaths'].iloc[-1] - covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['deaths'].iloc[-2]
    delta_confirmed = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['deaths'].iloc[-2] - covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['deaths'].iloc[-3]


    return {
       'data': [go.Indicator(
           mode='number+delta',
           value=value_confirmed,
           delta={'reference': delta_confirmed,'position': 'right','valueformat':'g','relative':False,'font':{'size':15}},
           number= {'valueformat': ',','font':{'size':20}},
           domain= {'y':[0,1], 'x':[0,1]}
       )],

        'layout':go.Layout(
           title={'text':'New Deaths:',
                  'y':0.98,'x':0.5,'xanchor':'center','yanchor':'top'},
            height= 50,
            font=dict(color='#dd1e35'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor= '#1f2c56'
            )
        }

#app call back for recovered
@app.callback(Output('recovered','figure'),[Input('w_countries','value')])

def update_confirmed(w_countries):
    covid_data_by_country = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'deaths', 'recovered', 'active']].sum().reset_index()
    value_confirmed = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['recovered'].iloc[-1] - covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['recovered'].iloc[-2]
    delta_confirmed = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['recovered'].iloc[-2] - covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['recovered'].iloc[-3]


    return {
       'data': [go.Indicator(
           mode='number+delta',
           value=value_confirmed,
           delta={'reference': delta_confirmed,'position': 'right','valueformat':'g','relative':False,'font':{'size':15}},
           number= {'valueformat': ',','font':{'size':20}},
           domain= {'y':[0,1], 'x':[0,1]}
       )],

        'layout':go.Layout(
           title={'text':'New Recovered:',
                  'y':0.98,'x':0.5,'xanchor':'center','yanchor':'top'},
            height= 50,
            font=dict(color='green'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor= '#1f2c56'
            )
        }

#app call back for active
@app.callback(Output('active','figure'),[Input('w_countries','value')])

def update_confirmed(w_countries):
    covid_data_by_country = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'deaths', 'recovered', 'active']].sum().reset_index()
    value_confirmed = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['active'].iloc[-1] - covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['active'].iloc[-2]
    delta_confirmed = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['active'].iloc[-2] - covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['active'].iloc[-3]


    return {
       'data': [go.Indicator(
           mode='number+delta',
           value=value_confirmed,
           delta={'reference': delta_confirmed,'position': 'right','valueformat':'g','relative':False,'font':{'size':15}},
           number= {'valueformat': ',','font':{'size':20}},
           domain= {'y':[0,1], 'x':[0,1]}
       )],

        'layout':go.Layout(
           title={'text':'New Active:',
                  'y':0.98,'x':0.5,'xanchor':'center','yanchor':'top'},
            height= 50,
            font=dict(color='purple'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor= '#1f2c56'
            )
        }

#app call back for pie chart
@app.callback(Output('pie_chart','figure'),[Input('w_countries','value')])

def update_graph(w_countries):
    covid_data_by_country = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'deaths', 'recovered', 'active']].sum().reset_index()
    confirmed_value = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['confirmed'].iloc[-1]
    death_value = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['deaths'].iloc[-1]
    recovered_value = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['recovered'].iloc[-1]
    active_value = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries]['active'].iloc[-1]

    #list of colors for pie chart(one for each column above
    colors = ['orange','#dd1e35','green','purple']

    return {
       'data': [go.Pie(
           labels=['Confirmed','Deaths','Recovered','Active'],
           values=[confirmed_value,death_value,recovered_value,active_value],
           marker=dict(colors=colors),
           hoverinfo='label+value+percent',
           textinfo='label+value',
           hole=0.7,
           rotation=45
           #insidetextorientation='radial'

       )],

        'layout':go.Layout(
           title={'text':'Total Cases: '+(w_countries),
                  'y':0.98,'x':0.5,'xanchor':'center','yanchor':'top'},
            titlefont={'color':'white','size':20},
            font=dict(family='sans-serif',color='white', size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor= '#1f2c56',
            legend={'orientation':'h','bgcolor':'#1f2c56','xanchor':'center','x':0.5,'y':-0.7}
            )
        }

#app call back for line chart
@app.callback(Output('line_chart','figure'),[Input('w_countries','value')])

def update_graph(w_countries):
    covid_data_by_country = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'deaths', 'recovered', 'active']].sum().reset_index()
    covid_data_3 = covid_data_by_country[covid_data_by_country['Country/Region'] == w_countries][['Country/Region', 'date', 'confirmed']].reset_index()
    covid_data_3['daily_confirmed'] = covid_data_3['confirmed'] - covid_data_3['confirmed'].shift(1)
    # need a rolling average for the last 7 days for line graph
    covid_data_3['rolling_avg'] = covid_data_3['daily_confirmed'].rolling(window=7).mean()

    #list of colors for pie chart(one for each column above
    colors = ['orange','#dd1e35','green','purple']

    return {
       'data': [go.Bar(
           x=covid_data_3['date'].tail(30),
           y=covid_data_3['daily_confirmed'].tail(30),
           name='Daily Confirmed Cases',
           marker=dict(color='orange'),
           hoverinfo='text',
           hovertext=
                '<b>Date</b>: '+ covid_data_3['date'].tail(30).astype(str) + '<br>' +
                '<b>Daily Confirmed Cases</b>: ' + [f'{x:,.0f}' for x in covid_data_3['daily_confirmed'].tail(30)]+ '<br>'+
                '<b>Country</b>: ' + covid_data_3['Country/Region'].tail(30).astype(str) + '<br>'

       ),
           #line chart
           go.Scatter(
               x=covid_data_3['date'].tail(30),
               y=covid_data_3['rolling_avg'].tail(30),
               name='Rolling Avg of the last 7 Days - Daily confirmed Cases',
               line=dict(color='#FF00FF',width=3),
               mode='lines',
               hoverinfo='text',
               hovertext=
               '<b>Date</b>: ' + covid_data_3['date'].tail(30).astype(str) + '<br>' +
               '<b>Daily Confirmed Cases</b>: ' + [f'{x:,.0f}' for x in covid_data_3['rolling_avg'].tail(30)] + '<br>'

           )
       ],

        'layout':go.Layout(
           title={'text':'Daily Confirmed Cases: '+(w_countries),
                  'y':0.98,'x':0.5,'xanchor':'center','yanchor':'top'},
            titlefont={'color':'white','size':20},
            font=dict(family='sans-serif',color='white', size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor= '#1f2c56',
            legend={'orientation':'h','bgcolor':'#1f2c56','xanchor':'center','x':0.5,'y':-0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>Date</b>',color='white',showline=True,showgrid=True,showticklabels=True, linecolor='white', linewidth=2,ticks='outside',tickfont=dict(family='Aerial',color='white',size=12)),
            yaxis=dict(title='<b>Daily Confirmed Cases</b>', color='white', showline=True, showgrid=True, showticklabels=True, linecolor='white', linewidth=2, ticks='outside', tickfont=dict(family='Aerial',color='white',size=12))
            )
        }

# callback for map chart
#app call back for line chart
@app.callback(Output('map_chart','figure'),[Input('w_countries','value')])

def update_graph(w_countries):
    covid_data_loc = covid_data.groupby(['Lat', 'Long', 'Country/Region'])[['confirmed', 'deaths', 'recovered', 'active']].max().reset_index()
    covid_data_loc_country = covid_data_loc[covid_data_loc['Country/Region'] == w_countries]

    if w_countries:
        zoom=2
        zoom_lat = dict_of_locations[w_countries]['Lat']
        zoom_long = dict_of_locations[w_countries]['Long']

    return {
       'data': [go.Scattermapbox(
           lon=covid_data_loc_country['Long'],
           lat=covid_data_loc_country['Lat'],
           mode='markers',
           marker=go.scattermapbox.Marker(size=covid_data_loc_country['confirmed']/1000, color=covid_data_loc_country['confirmed'], colorscale='HSV',showscale=False,sizemode='area',opacity=0.3),
           hoverinfo='text',
           hovertext=
           '<b>Country</b>: ' + covid_data_loc_country['Country/Region'].astype(str) + '<br>' +
           '<b>Longitude</b>: ' + covid_data_loc_country['Long'].astype(str) + '<br>' +
           '<b>Latitude</b>: ' + covid_data_loc_country['Lat'].astype(str) + '<br>' +
           '<b>Confirmed Cases</b>: ' + [f'{x:,.0f}' for x in covid_data_loc_country['confirmed']] + '<br>'+
           '<b>Deaths</b>: ' + [f'{x:,.0f}' for x in covid_data_loc_country['deaths']] + '<br>' +
           '<b>Recovered Cases</b>: ' + [f'{x:,.0f}' for x in covid_data_loc_country['recovered']] + '<br>' +
           '<b>Active Cases</b>: ' + [f'{x:,.0f}' for x in covid_data_loc_country['active']] + '<br>'
       )],

        'layout':go.Layout(
            hovermode='x',
            paper_bgcolor='#1f2c56',
            plot_bgcolor= '#1f2c56',
            margin=dict(r=0,l=0,b=0,t=0),
            mapbox=dict(
                accesstoken='pk.eyJ1IjoiZ2lsaGVybmFuZGV6MjEiLCJhIjoiY2t1b3hlYWxvMGRldDJ2cGcyMmFpbzhoMyJ9.9kuDFz1M8FooBCfjZtuzAQ',
                center=go.layout.mapbox.Center(lat=zoom_lat,lon=zoom_long),
                style='dark',
                zoom=zoom),
            autosize=True
            )
        }


if __name__ == '__main__':
    app.run_server(debug=True)