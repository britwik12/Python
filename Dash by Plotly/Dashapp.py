# Project Dash 
# BZAN 544 UTK
# Dr. Jerry Day
# 2/15/2020

# Put your name here: Chiran, Ritwik, Vu                                  

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from datetime import datetime as dt

#styling (mostly for the scatter plot)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# reading in data.frame
games_flat = pd.read_csv('games_flat_xml_2012-2018.csv', header =0, index_col = 0)
games_flat.date = pd.to_datetime(games_flat.date)

#create month and year columns for aggregating purpose. We want to have data for different seasons (which is sep-jan next year)
games_flat['Year_A'] = games_flat['date'].dt.year
games_flat['Month_A'] = games_flat['date'].dt.month

#same logic for 2nd dataset
Tv_ratings = pd.read_csv('TV_Ratings_onesheet.csv',header = 0)
Tv_ratings.Date = pd.to_datetime(Tv_ratings.Date)
Tv_ratings['Year_V'] = Tv_ratings['Date'].dt.year
Tv_ratings['Month_V'] = Tv_ratings['Date'].dt.month

#remove all the game before 2012, we choose that threshold because games_flat only records from 2012 season onwards
currentGames = [x.year > 2012 for x in Tv_ratings.Date]
Tv_ratings = Tv_ratings.loc[currentGames]



#merged the provided data frame
ratings_df = games_flat.merge(Tv_ratings,left_on='TeamIDsDate', right_on='TeamIDsDate',how='outer', copy = True)


# Select relevant columns
relevant_list = ['homeid','homename','visid','visname','date','Year_A','Month_A','location','stadium','attend','postseason','leaguegame','neutralgame','nightgame','Matchup_Full_TeamNames','Date','Year_V','Month_V','GAME','Visitor Team','Home Team', 'VisTeamID','HomeTeamID','RATING','VIEWERS','Network']

#Select out those relevant columns
ratings_df = ratings_df[relevant_list]

# Sorting the df makes the plots turn out nicer in the case we want to use lines.
ratings_df = ratings_df.sort_values(by = "date")


#rename columns so it has self-explanatory name. _A stands for data from Games_flat ie. Attendance data, _V stands for data in viewership table

ratings_df.columns = ['HomeID_A','HomeName_A','VisitID_A',"VisitName_A",'Date_A','Year_A','Month_A','Location_A','Stadium_A','Attendance','Postseason_A','LeagueGame_A','NeutralGame_A','NightGame_A','Matchup_Full_TeamNames_A','Date_V','Year_V','Month_V', 'GAME_V','VisitName_V','HomeName_V','VisitID_V','HomeID_V','RATING_V','Viewership','Network_V']


#dictionaries for metric and gametype options, we will have different visualization for attendance and viewership as well as type of game, whether it is away or at home

metrics =[ {'label' : 'Attendance', 'value' : 'Attendance'},
         {'label' : 'Viewership', 'value' : 'Viewership'}]

gametype =[ {'label' : 'Home', 'value' : 'Home'},
         {'label' : 'Away', 'value' : 'Away'}]


# Creating an object for "options" in the dropdown menu of attendance. We do so by extract all the name of home team, which are more popular. Many of the team appears in Visit Team column only appears once or twice in a season or the whole dataset. We consider that it will not be worth in to include them in. So 64 home team here will be a reasonable number of options, given that most of them are fairly popular.

teamNames_attendance = ratings_df['HomeName_A'].dropna().unique()
teamNamesDict_attendance = [{'label' : tn, 'value': tn} for tn in teamNames_attendance]

#aggregate data for home game by year and team. This helps with the plot of yearly average attendance and viewership
avg_attendance_home = ratings_df.groupby(['HomeName_A','Year_A'])['Attendance'].mean().reset_index()
avg_viewership_home = ratings_df.groupby(['HomeName_V','Year_V'])['Viewership'].mean().reset_index()

#aggregate data for away game by year and team. This helps with the plot of yearly average attendance and viewership
avg_attendance_away = ratings_df.groupby(['VisitName_A','Year_A'])['Attendance'].mean().reset_index()
avg_viewership_away = ratings_df.groupby(['VisitName_V','Year_V'])['Viewership'].mean().reset_index()

#merge data for attendance and viewership. Choose inner because of the number of visit team are much higher than home team (explained). 

avg_attendance = avg_attendance_home.merge(avg_attendance_away, left_on=['HomeName_A','Year_A'], right_on=['VisitName_A','Year_A'],how='inner')
avg_viewership = avg_viewership_home.merge(avg_viewership_away, left_on=['HomeName_V','Year_V'], right_on=['VisitName_V','Year_V'],how='inner')

# Create the app with the stylesheet initialized earlier
app = dash.Dash(__name__,
               external_stylesheets = external_stylesheets)


# Create the layout
app.layout = html.Div(
    # title of the page
    [html.Div([html.H1('College Football Attendance and Viewership Visualization'),
        html.H2('A product by I20 Corp')], 
              style={'textAlign': 'center','color': 'blue'}),
     
     html.H5('Select a team and a desirable metrics to understand their popularity'),
     html.Br(),
     
     #radio button and dropdown (which allows multiple selections)
     html.Div([
         html.Label('Choose a metric'),
         dcc.RadioItems(id ='radio1',
                      options= metrics,
                       value = "Attendance")],
     style = {'width': '49%'}),
     
     html.Div([
          html.Label('Choose a team'),    
          dcc.Dropdown(id ='dropdown2',
                      options= teamNamesDict_attendance,
                      multi=True,
                      placeholder="Select a team")],
             style = {'width': '49%'}),
     
     #layout for visualization
     html.H3('Yearly data'),
     
     html.Div([
         #graph of yearly average with sliders to examine different year
     dcc.Graph (id='1st_graph'), 
     html.P('Slide to select a season you want to examine the trend'),
     html.Br(),
     dcc.Slider(
         #slider with range from 2012-2018 season
        id='year-slider',
        min=ratings_df['Year_A'].min()+1,
        max=ratings_df['Year_A'].max()-1,
        value=ratings_df['Year_A'].max()-1,
        marks={int(year): str(int(year)) for year in ratings_df['Year_A'].dropna().unique()},
        step=None)],
        style={'padding': '0 100 50 100'}),
     html.Br(),     
     #option for home or away game summary that each of our popular team played, default to be Home
     html.P('Select to examine the trend for each team home or away game'),
     html.Br(),
     dcc.RadioItems(id ='radio2',
                      options= gametype,
                      value = "Home",
                      labelStyle={'display': 'inline-block'}),
     html.Br(),
     html.H3('Data from 2012 - 2019'),
     html.Br(),
     dcc.Graph (id='2nd_graph'),
     
     
     #iteractive plot that show relationship between attendance and viewership of each team with available data for both metrics. This is an interactive scatter plot, in the sense that when you hover over a point, it will break down the average viewership and attendance for a season into home and away game that the team plays in the season. Note that not all the game has data for both viewership and attendance.
     html.Div([
        dcc.Graph(
            id='average_scatter',
            hoverData={'points': [{'customdata': "Tennessee"}]})], 
            style={'width': '49%', 'display': 'inline-block', 'padding': '0 100 0 100'}),
     # Hidden div inside the app that stores the intermediate value. We use this block to store data used to plot the interactive plot (using hover data)
    html.Div(id='intermediate-value', style={'display': 'none'}),
    
     #2 plots on right hand side of scatterplot
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series')], 
        style={'display': 'inline-block', 'width': '49%', 'padding': '0 100 0 100'}),
   
    #Second slider which offers user an option to examine relationship btw attendance and viewership in a certain year
    html.Div(dcc.Slider(
        id='year-slider2',
        min=ratings_df['Year_A'].min()+1,
        max=ratings_df['Year_A'].max()-1,
        value=ratings_df['Year_A'].max()-1,
        marks={int(year): str(int(year)) for year in ratings_df['Year_A'].dropna().unique()},
        step=None), 
             style={'width': '49%', 'padding': '0px 10px 20px 40px'}),
     
     #2 plots on below of scatterplot
     html.Div(
        dcc.Graph(id='w-time-series'),
        style={'display': 'inline-block','width': '49%', 'padding': '20 10 20 40'}),
     
     html.Div(
        dcc.Graph(id='z-time-series'),
        style={'display': 'inline-block', 'width': '49%', 'padding': '20 10 20 40'}),
    
     html.Br(),
     html.Br(),
     html.Br(),
     html.Br(),
     html.Br(),

     #Addition dcc and html we include to meet the requirement. Basically it is a textbox allows users to input a message. We add a button allow user submit text. This feature is thus there to add to the variery of dcc and html components used
     
     #define the textbox
     html.Div(
     dcc.Textarea(
        placeholder='Enter a value...',
        value='If you want more information on a certain team, please list those teams here and send us a request',
        style={'width': '88%'})),
     
     #confirmation log, just like a warning or confirmation button
     dcc.ConfirmDialogProvider(
        children=html.Button('Submit'),
        id='Submit',
        message='Do you want to send your inquiry?'),
     
     html.Br(),
     html.Br(),
     
     #add in an external link
     html.A("For business enquiry contact us at", href='https://haslam.utk.edu/business-analytics-statistics/msba', target="_blank")
     
       


    ] # Closes out the children of outermost html.Div of app.layout
) # closes app.layout outermost html.Div 


# 1st callback is for the 1st plot, showing the attendance and viewership for all the games that a team play in a season

#this callback depends on 1st radio button, the dropdown and the first year slider
@app.callback(
   dash.dependencies.Output('1st_graph', 'figure'),
    [dash.dependencies.Input('radio1', 'value'),
    dash.dependencies.Input('dropdown2', 'value'),
    dash.dependencies.Input('year-slider', 'value')])


def update_figure(metric, teamX,year_value):
    
    #For cases when users want to examine attendance
    if metric == 'Attendance':
        #this line helps to extract all the games in a season. A year will be selected by a slider. For instance if the year is 2018, a season is defined that all the game in 2018 except those in january, plus all those games in january 2019
        ratings_df_year = ratings_df[((ratings_df['Year_A'] == year_value) & (ratings_df['Month_A'] != 1))| ((ratings_df['Year_A'] == (year_value + 1)) & (ratings_df['Month_A'] == 1 ))]
        
        #this line prevents Dash from reading can't read property layout of null. As the list of team when we initialized the app is an empty list
        if teamX == None:
            return dash.no_update
        else:
            figure= {
                'data':[dict(
                 type = "scatter",
                 mode = "lines+markers",
                 #name x will be team that is in list of teamX that is chosen. And when we choose a team, as long as this team appear as home or away team in attendance data set, the data will be extracted and presented on the plot
                 x=ratings_df_year[(ratings_df_year["HomeName_A"] == x) | (ratings_df_year["VisitName_A"] == x)]["Date_A"],
                 y=ratings_df_year[(ratings_df_year["HomeName_A"] == x) | (ratings_df_year["VisitName_A"] == x)]["Attendance"],
                 name = x,
                 marker=dict(
                     opacity=.6,
                     size = 7),
                 hovertext = ratings_df_year[(ratings_df_year["HomeName_A"] == x) | (ratings_df_year["VisitName_A"] == x)]["Matchup_Full_TeamNames_A"]) for x in teamX],
                'layout':    {
                    'title': 'Yearly Attendance'
            }
        }
    
            return figure
    
    #this is exactly the same thing, just for the case when users want to examine viewership
    elif metric == "Viewership":
        ratings_df_year = ratings_df[((ratings_df['Year_V'] == year_value) & (ratings_df['Month_V'] != 1))| ((ratings_df['Year_V'] == (year_value + 1)) & (ratings_df['Month_V'] == 1 ))]
        if teamX == None:
            return dash.no_update
        else:
            figure= {
                 'data':[dict(
                 type = "scatter",
                 mode = "lines+markers",
                 x=ratings_df_year[(ratings_df_year["HomeName_V"] == x) | (ratings_df_year["VisitName_V"] == x)]["Date_A"],
                 y=ratings_df_year[(ratings_df_year["HomeName_V"] == x) | (ratings_df_year["VisitName_V"] == x)]["Viewership"],
                 name = x,
                 marker=dict(
                     opacity=.6,
                     size = 7),
                 hovertext = ratings_df_year[(ratings_df_year["HomeName_V"] == x) | (ratings_df_year["VisitName_V"] == x)]["GAME_V"]) for x in teamX],
                'layout':    {
                    'title': 'Yearly Viewership'
            }
        }
            return figure


#the second plot is the yearly average for either attendance from 2012 to 2018 season, for either home or away game of a team. It depends on the dropdown as well as 2 radio buttons
@app.callback(
   dash.dependencies.Output('2nd_graph', 'figure'),
    [dash.dependencies.Input('radio1', 'value'),
     dash.dependencies.Input('dropdown2', 'value'),
     dash.dependencies.Input('radio2', 'value')])

def update_figure2(metric,teamX,gametype):
    if metric == 'Attendance':
        
        if teamX == None:
            return dash.no_update
        
        else:
            #this is for average attendance at home
            if gametype == "Home":
                figure = {
                 'data':[dict(
                 type = "scatter",
                 mode = "lines+markers",
                 #this avg_attendance dataframe was created earlier, before we set up the app. It has average attendance for both home and away game with average attendance at home called Attendance_x and average attendance for away game is Attendance_y
                 x=avg_attendance[(avg_attendance["HomeName_A"] == x)]["Year_A"],
                 y=avg_attendance[(avg_attendance["HomeName_A"] == x)]["Attendance_x"],
                 name = x,
                 marker=dict(
                     opacity=.6,
                     size = 7),
                 hovertext = avg_attendance[(avg_attendance["HomeName_A"] == x)]["Year_A"]) for x in teamX],
                'layout': {
                    'title': 'Average Home Attendance (yearly)'
            }
        }
                #this is for average attendance for away game
            elif gametype == "Away":
                figure = {
                 'data':[dict(
                 type = "scatter",
                 mode = "lines+markers",
                 x=avg_attendance[(avg_attendance["HomeName_A"] == x)]["Year_A"],
                 y=avg_attendance[(avg_attendance["HomeName_A"] == x)]["Attendance_y"],
                 name = x,
                 marker=dict(
                     opacity=.6,
                     size = 7),
                 hovertext =avg_attendance[(avg_attendance["HomeName_A"] == x)]["Year_A"]) for x in teamX],
                'layout': {
                    'title': 'Average Away Attendance (yearly)'
            }
        }
            return figure 
    
    #same exaplanation as above but this is for viewership
    elif metric == 'Viewership':
        if teamX == None:
            return dash.no_update
            #this is for average viewership for home game
        else:
            if gametype == "Home":
                figure = {
                 'data':[dict(
                 type = "scatter",
                 mode = "lines+markers",
                 #in the merged dataset, Viewership_x is meant for home game and Viewership_y is meant for away game
                 x=avg_viewership[(avg_viewership["HomeName_V"] == x)]["Year_V"],
                 y=avg_viewership[(avg_viewership["HomeName_V"] == x)]["Viewership_x"],
                 name = x,
                 marker=dict(
                     opacity=.6,
                     size = 7),
                 hovertext = avg_viewership[(avg_viewership["HomeName_V"] == x)]["Year_V"]) for x in teamX],
                'layout': {
                    'title': 'Average Home Viewership (yearly)'
            }
        }
                #this is for average viewership for away game
            elif gametype == "Away":
                figure= {
                 'data':[dict(
                 type = "scatter",
                 mode = "lines+markers",
                 x=avg_viewership[(avg_viewership["VisitName_V"] == x)]["Year_V"],
                 y=avg_viewership[(avg_viewership["VisitName_V"] == x)]["Viewership_y"],
                 name = x,
                 marker=dict(
                     opacity=.6,
                     size = 7),
                 hovertext =avg_viewership[(avg_viewership["VisitName_V"] == x)]["Year_V"]) for x in teamX],
                'layout': {
                    'title': 'Average Away Viewership (yearly)'
                
            }
        }
    
            return figure


#this callback helps to create immediate value, which we store as a hidden value. Basic when we slide the 2nd slider, this will helps to extract the data frame for that season, the definition and logic behind creating dataframe for a season stays the same here.         
@app.callback(
    dash.dependencies.Output('intermediate-value', 'children'), 
    [dash.dependencies.Input('year-slider2', 'value')])

def intermediate_value(year_value):
    ratings_df_year = ratings_df.dropna()
    ratings_df_year = ratings_df[((ratings_df['Year_A'] == year_value) & (ratings_df['Month_A'] != 1))| ((ratings_df['Year_A'] == (year_value + 1)) & (ratings_df['Month_A'] == 1 ))]
    #in order to store the data, we converted the dataframe to json, additional date format argument helps us to not mess up with date data
    return ratings_df_year.to_json(orient='split',date_format='iso')

#this callback is for the scatter plot, it only depends on the hidden json data that we extracted. Nevertheless, it involves a lot of data prep, since it will relate to 4 other plots that we use hoverdata        
@app.callback(
    dash.dependencies.Output('average_scatter', 'figure'),
    [dash.dependencies.Input('intermediate-value', 'children')])

def update_figure3(jsonified_cleaned_data):
    #read the json data that we converted earlier. Transform it back to regular pd dataframe for manipulation
    ratings_df_year = pd.read_json(jsonified_cleaned_data, orient='split')
    
    #We want to find mean of attendance and viewership per team, for either home or away game. We also want to find the number of home and away team that each team play so that we can find the overall average later. Reset index is there to convert results of groupby into a data frame.
    avg_attendance_year_home = ratings_df_year.groupby(['HomeName_A'])['Attendance'].agg(['mean', 
                         'size']).reset_index()
    avg_viewership_year_home = ratings_df_year.groupby(['HomeName_V'])['Viewership'].agg(['mean', 
                         'size']).reset_index()
    avg_attendance_year_away = ratings_df_year.groupby(['VisitName_A'])['Attendance'].agg(['mean', 
                         'size']).reset_index()
    avg_viewership_year_away = ratings_df_year.groupby(['VisitName_V'])['Viewership'].agg(['mean', 
                         'size']).reset_index()
    
    #merge attedance and viewership together. Left merge as hometeam are always more popular teams. Many team in visitname columns only appear like once or twice.
    attendance = avg_attendance_year_home.merge(avg_attendance_year_away,left_on='HomeName_A', right_on='VisitName_A',how='left')
    viewership = avg_viewership_year_home.merge(avg_viewership_year_away,left_on='HomeName_V', right_on='VisitName_V',how='left')
    
    #combine the two dataset for plotting purpose
    attendance_viewership = attendance.merge(viewership, left_on='HomeName_A', right_on='HomeName_V', how = 'inner')
    
    #create 2 new column, which compute the average attedance and viewership. The formula is intuitive
    #Average attendance = (average attendance at home * number of home game + average attendance away * number of away game)/(number of home game + number of away game) for each team. Same thing applies for viewership
    #Where: mean_x_x & size_x_x are average attendance at home & number of home game 
    #mean_y_x & size_x_x are average attendance for away game & number of away game
    #mean_x_y & mean_y_y are average viewership at home & number of home game 
    #mean_y_y & size_y_y are average viewership for away game & number of away game
    attendance_viewership['Attendance'] = (attendance_viewership['mean_x_x'] * attendance_viewership['size_x_x'] + attendance_viewership['mean_y_x'] * attendance_viewership['size_y_x'])/ (attendance_viewership['size_x_x'] + attendance_viewership['size_y_x'])
    
    attendance_viewership['Viewership'] = (attendance_viewership['mean_x_y'] * attendance_viewership['size_x_y'] + attendance_viewership['mean_y_y'] * attendance_viewership['size_y_y'])/ (attendance_viewership['size_x_y'] + attendance_viewership['size_y_y'])
    
    
    
    figure = {
                 'data':[dict(
                 type = "scatter",
                 mode = "markers",
                     #plot the overal attendance anf viewership
                 x = attendance_viewership["Attendance"],
                 y = attendance_viewership['Viewership'],
                     #the customer data here is important for the hoverdata, it helps to extract the data belongs to each team in the next 4 plots
                 customdata = attendance_viewership['HomeName_A'],
                 marker=dict(
                     opacity=.6,
                     size = 7),
                 hovertext = attendance_viewership['HomeName_A'])],
                'layout':    dict(
                    xaxis={'title': 'Attendance'},
                    yaxis={'title': 'Viewership'},
                    margin={'l': 40, 'b': 30, 't': 10, 'r': 20},
                    height=450,
                    hovermode='closest')
        }
    return figure
     

#the last 4 callbacks are for 4 plots which use hoverdata from the scatter plot
    
@app.callback(
    #each of the next 4 callbacks take the scatter plot, and intermediate value (the json data we converted) as inputs
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('average_scatter', 'hoverData'),
    dash.dependencies.Input('intermediate-value', 'children')])

#This plot if for attendance for home game
def update_x_timeseries(hoverData, jsonified_cleaned_data):
    #convert json back to pd dataframe
    ratings_df_year = pd.read_json(jsonified_cleaned_data, orient='split')
    #extract the team name, check the customdata definition in the scatter plot
    team = hoverData['points'][0]['customdata']
    #extract data belongs to the team that we hover the cursor over
    attendance_viewership = ratings_df_year[(ratings_df_year['HomeName_A'] == team)]
    return  {
            'data': [dict(
            x=attendance_viewership['Date_A'],
            y=attendance_viewership['Attendance'],
            mode='bar',
            type='bar',
            hovertext = attendance_viewership['Matchup_Full_TeamNames_A'])],
            'layout': dict(
                yaxis={'title': 'Attendance at home game'},
                margin={'l': 40, 'b': 30, 't': 10, 'r': 20},
                height=225,
                hovermode='closest')
    }


@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('average_scatter', 'hoverData'),
    dash.dependencies.Input('intermediate-value', 'children')])

#This plot if for attendance for away game
def update_y_timeseries(hoverData, jsonified_cleaned_data):
    ratings_df_year = pd.read_json(jsonified_cleaned_data, orient='split')
    team = hoverData['points'][0]['customdata']
    attendance_viewership = ratings_df_year[(ratings_df_year['VisitName_A'] == team)]
    return  {
            'data': [dict(
            x=attendance_viewership['Date_A'],
            y=attendance_viewership['Attendance'],
            mode='bar',
            type='bar',
            hovertext = attendance_viewership['Matchup_Full_TeamNames_A'])],
            'layout': dict(
                yaxis={'title': 'Attendance at away game'},
            margin={'l': 40, 'b': 30, 't': 10, 'r': 20},
            height=225,
            hovermode='closest')
    }

@app.callback(
    dash.dependencies.Output('w-time-series', 'figure'),
    [dash.dependencies.Input('average_scatter', 'hoverData'),
    dash.dependencies.Input('intermediate-value', 'children')])

#This plot if for viewership for home game
def update_x_timeseries(hoverData, jsonified_cleaned_data):
    ratings_df_year = pd.read_json(jsonified_cleaned_data, orient='split')
    team = hoverData['points'][0]['customdata']
    attendance_viewership = ratings_df_year[(ratings_df_year['HomeName_V'] == team)]
    return  {
        'data': [dict(
            x=attendance_viewership['Date_V'],
            y=attendance_viewership['Viewership'],
            mode='bar',
            type='bar',
            hovertext = attendance_viewership['GAME_V'])],
            'layout': dict(
            yaxis={'title': 'Viewership at home game'},
            margin={'l': 40, 'b': 30, 't': 10, 'r': 20},
            height=225,
            hovermode='closest')
    }


@app.callback(
    dash.dependencies.Output('z-time-series', 'figure'),
    [dash.dependencies.Input('average_scatter', 'hoverData'),
    dash.dependencies.Input('intermediate-value', 'children')])

#This plot if for viewership for away game
def update_y_timeseries(hoverData, jsonified_cleaned_data):
    ratings_df_year = pd.read_json(jsonified_cleaned_data, orient='split')
    team = hoverData['points'][0]['customdata']
    attendance_viewership = ratings_df_year[(ratings_df_year['VisitName_V'] == team)]
    return  {
            'data': [dict(
            x=attendance_viewership['Date_A'],
            y=attendance_viewership['Viewership'],
            mode='bar',
            type='bar',
            hovertext = attendance_viewership['GAME_V'])],
            'layout': dict(
                yaxis={'title': 'Viewership at away game'},
                margin={'l': 40, 'b': 30, 't': 10, 'r': 20},
                height=225,
                hovermode='closest')
    }



#added to allow debug mode
if __name__ == "__main__":
    app.run_server(debug=True)
                      
        