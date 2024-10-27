#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="IlluminateMe Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Color illuminateMe #599191
# Color in eye #51be9e
# Color orange #ffd966
# Color blue in eye #2a2f64

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


#######################
# Load data
df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')
df_results = pd.read_csv('data/ai-model/results_20241024_all_points_training_7200min.csv')
df_sports = pd.read_csv('data/wearable/SPORT_1729522447097.csv')
df_sleep = pd.read_csv('data/wearable/SLEEP_1729522445075.csv')
df_remember = pd.read_csv('data/calendar/remember_2024.csv')
#######################
# Selection functions

### GENERAL
def weekday_text(day_digit):
    day = ''
    if day_digit == 0:
        day = 'Monday'
    if day_digit == 1:
        day = 'Tuesday'
    if day_digit == 2:
        day = 'Wednesday'
    if day_digit == 3:
        day = 'Thursday'
    if day_digit == 4:
        day = 'Friday'
    if day_digit == 5:
        day = 'Saturday'
    if day_digit == 6:
        day = 'Sunday'
    return day     

### SPORT
def sports_prepp(df_sports):
    df_sports['date_time'] = pd.to_datetime(df_sports['startTime'], format="%Y-%m-%d %H:%M:%S+0000")
    df_sports['date'] = pd.to_datetime(df_sports['date_time'], format="%Y-%m-%d")
    
    # 1 RUN
    # 6 WALK
    # 8 INDOOR RUNNING
    # 10 CYKEL
    # 14 SWIM
    # 16 ?? FRI RÖRELSE ??
    # 50 CORE
    # 52 STYRKETRÄNING
    # 60 ?? FRI RÖRELSE ??
    
    dict_sports = {
        1:  "- Running        ", 
        6:  "- Walking        ", 
        8:  "- Indoor running", 
        10: "- Cycling       ", 
        14: "- Swimming      ", 
        16: "- Free movement ", 
        50: "- Core          ", 
        52: "- Strength      ",
        60: "- Unknown       "
    }
    
    df_sports['type_text'] = df_sports['type'].map(dict_sports)
    return df_sports

def sport_selection(df_sports_prepp, selected_date):
    sport_selection = []
    
    # Select date
    for i in range(0, len(df_sports_prepp)):
        if str(df_sports_prepp['date'].iloc[i].date()) == selected_date:
            sport_selection.append(df_sports_prepp.iloc[i])
    df_sport_date= pd.concat(sport_selection, axis = 1).T.sort_values(by=['date_time'])
    
    # Select time
    time_sport = []    
    for i in range(0, len(df_sport_date)):
        time_sport.append(df_sport_date['date'].iloc[i].strftime("%H:%M"))
    df_sport_date['time'] = time_sport
    
    # Select label
    bar_labels = [] 
    types = df_sport_date['type_text'].values
    for i in range(0, len(time_sport)):
        bar_labels.append(time_sport[i] + ' ' + types[i])
    df_sport_date['labels'] = bar_labels
    
    return df_sport_date


### SLEEP
def define_hours(x):
    import datetime
    return str(datetime.timedelta(minutes=x)) + ' hours'


def sleep_prepp(df_sleep):
    column_names = ['deepSleepTime', 'shallowSleepTime', 'wakeTime']
    df_sleep['total_sleep']= df_sleep[column_names].sum(axis=1)      
    df_sleep['total_hours'] = df_sleep['total_sleep'].apply(define_hours)
    return df_sleep


def sleep_selection(df_sleep, selected_date):
    df_sleep_date = df_sleep[df_sleep['date'] == selected_date]
    sleep_time = df_sleep_date['total_hours'].values
    df_sleep_date = df_sleep_date[['deepSleepTime', 'shallowSleepTime', 'wakeTime', 'total_sleep']]
    total_sleep = df_sleep_date['total_sleep'].values[0]
    df_sleep_date = df_sleep_date.div(total_sleep).round(4) * 100
    return df_sleep_date, sleep_time


### CALENDAR
def calendar_prepp(df_remember):
    start_time = df_remember['start_date_time']
    date_time_list = []
    date_list = []
    time_list = []
    for i in range(0, len(start_time)):
        this_day = start_time.iloc[i]
        sep = this_day[20:25]
        if sep == '00:00':
            date_time_list.append(pd.to_datetime(this_day, format='%Y-%m-%d %H:%M:%S+00:00'))
        if sep == '02:00':
            date_time_list.append(pd.to_datetime(this_day, format='%Y-%m-%d %H:%M:%S+02:00'))
        time_string = str(date_time_list[i].time())
        time_list.append(time_string[0:5])
        date_string = str(date_time_list[i].date())
        date_list.append(date_string)
    df_remember['date_time'] = date_time_list
    df_remember['time'] = time_list
    df_remember['date'] = date_list
    return df_remember

def calendar_selection(df_remember, selected_date):
    calendar_selection = []
    
    # Select date
    for i in range(0, len(df_remember)):
        if str(df_remember['date_time'].iloc[i].date()) == selected_date:
            calendar_selection.append(df_remember.iloc[i])
    if len(calendar_selection) == 0:
        data = {
            'date_time': ['-'],
            'event': ['No events registered at this date']
            }
        df_remember = pd.DataFrame(data)
    else:
        df_remember= pd.concat(calendar_selection, axis = 1).T.sort_values(by=['date_time'])   
        
    return df_remember


#######################
# Sidebar
with st.sidebar:
    st.image("illuminateMe_logo.png")
    #t.markdown('Emelie Chandni Jutvik')    
    
    # SCORE OVERVIEW
    
    # SCORE SELECTION
    # Stress scale:
    # 1: diff == 0-5
    # 2: diff == 5-10
    # 4: diff == 10-20
    # 6: diff == 20-30
    # 8: diff == 30-40
    # 10: diff == 40-   
    stress_scores = [10, 8, 6, 4, 2, 1]
    all_weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    selected_score = st.selectbox('Select score', stress_scores)
    df_score = df_results[df_results.score >= selected_score]

       
    # DATE SELECTION
    date_list_score = df_score.groupby(['date']).count()
    date_list = date_list_score.index
  
    # SELECTED DATES
    selected_date = st.selectbox('Select a date', date_list)
    df_date = df_score[df_score.date == selected_date]
    df_date_score = df_results[df_results.date == selected_date]
    weekday_digit = df_date_score['weekday'].iloc[0]
    selected_weekday = weekday_text(weekday_digit)

    # SPORT
    df_sports_prepp = sports_prepp(df_sports)
    df_sport_date = sport_selection(df_sports_prepp, selected_date)

    # SLEEP
    df_sleep_prepp = sleep_prepp(df_sleep)
    df_sleep_date, sleep_time = sleep_selection(df_sleep_prepp, selected_date)
    
    # CALENDAR
    df_cal_rem_prepp = calendar_prepp(df_remember)
    df_cal_remember = calendar_selection(df_cal_rem_prepp, selected_date)
    print(df_cal_remember)


#######################
# Plots

# Line plit
def make_lineplot(input_df, input_y, input_x):   
    line_plot = alt.Chart(input_df).mark_line().encode(
        x=input_x, # time
        y=input_y # score
    )
    return line_plot

# Barplot
def make_barplot(input_df, input_y, input_x):    
    barplot = alt.Chart(input_df).mark_bar().encode(
            x=input_x, #'labels',
            y=input_y, #'sportTime(s)'
        ) 
    return barplot

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# Donut chart
def make_donut(source):    
    donut_chart =  alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="value",
        color="category:N",
    ).properties(width=130, height=130)
    return donut_chart

def old_make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

# Convert population to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Calculation year-over-year population migrations
def calculate_population_difference(input_df, input_year):
  selected_year_data = input_df[input_df['year'] == input_year].reset_index()
  previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
  selected_year_data['population_difference'] = selected_year_data.population.sub(previous_year_data.population, fill_value=0)
  return pd.concat([selected_year_data.states, selected_year_data.id, selected_year_data.population, selected_year_data.population_difference], axis=1).sort_values(by="population_difference", ascending=False)


#######################
# Dashboard Main Panel
st.title('Your summary')
col = st.columns((3.0, 5.5), gap='medium')
with col[0]:
    #st.subheader('Your ovreview')
    st.markdown('#### Stress peaks')
    st.caption("The selected day is a _:blue[" + selected_weekday + "]_")
    st.dataframe(df_date,
                 column_order=("date", "time", "score"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "date": st.column_config.TextColumn(
                        "Date",
                    ),
                    "time": st.column_config.TextColumn(
                        "Time",
                    ),
                    "weekday": st.column_config.TextColumn(
                        "Weekday",
                    ),
                    "score": st.column_config.ProgressColumn(
                        "Score",
                        format="%f",
                        min_value=0,
                        max_value=max(df_date.score),
                     )}
                 )
    
    st.markdown('#### Sleep')
    st.caption("You where sleeping for _:blue[" + sleep_time[0][0:1] +" hours and " + sleep_time[0][2:4] + " minutes]_  at selected date")
    categories_sleep = ['deep sleep', 'shallow sleep', 'awake']
    values = df_sleep_date[['deepSleepTime', 'shallowSleepTime', 'wakeTime']].values[0]
    source = pd.DataFrame({
        "category": categories_sleep,
        "value": values
    })
    donut_sleep = make_donut(source)
    st.altair_chart(donut_sleep, use_container_width=True)
    
    with st.expander('About deep sleep', expanded=True):
        st.caption('''
            Deep sleep typically happen during the first half of the night. 
            It is recommended to aim for about _:blue[13 to 23 percent]_ of your sleep 
            to be in this stages. This means - if you sleep 8 hours, you should 
            aim to get between an hour or just under two hours of deep sleep.
            ''')
    

with col[1]:
    #st.subheader('Indicators')             
    st.markdown('#### Events') 
    st.caption("_:blue[Calendar notes]_ from selected day")
    st.dataframe(df_cal_remember,
                 column_order=("date", "time", "event"),
                 hide_index=True,
                 width=600,
                 column_config={
                    "date": st.column_config.TextColumn(
                        "Date",
                    ),
                    "time": st.column_config.TextColumn(
                        "Time",
                    ),
                    "event": st.column_config.TextColumn(
                        "Description",
                    )}
                 )
    
    st.markdown('#### Activity')  
    st.caption("_:blue[Wearable activities]_ from selected day")
    barplot_sport = make_barplot(df_sport_date, 'labels', 'sportTime(s)')
    st.altair_chart(barplot_sport, use_container_width=True)
    
    st.markdown('#### Day overview') 
    st.caption("All _:blue[stress scores]_ at selected day")
    lineplot_score = make_lineplot(df_date_score, 'score', 'time')
    st.altair_chart(lineplot_score, use_container_width=True)