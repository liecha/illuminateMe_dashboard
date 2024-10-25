#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Color illuminateMe #599191

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
df_results = pd.read_csv('data/results_20241024_all_points_training_7200min.csv')
df_sports = pd.read_csv('data/SPORT_1729522447097.csv')

#######################
# Selection functions

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
        1: "- Running", 
        6: "- Walking", 
        8: "- Indoor running", 
        10: "- Cycling", 
        14: "- Swimming", 
        16: "- Free movement", 
        50: "- Core", 
        52: "- Strength",
        60: "- Unknown"
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

#######################
# Sidebar
with st.sidebar:
    #st.title('🏂 US Population Dashboard')
    st.image("illuminateMe_logo.png")
    
    
    # SCORE SELECTION
    # Stress scale:
    # 1: diff == 0-5
    # 2: diff == 5-10
    # 4: diff == 10-20
    # 6: diff == 20-30
    # 8: diff == 30-40
    # 10: diff == 40-   
    stress_scores = [10, 8, 6, 4, 2, 1]
    selected_score = st.selectbox('Select score', stress_scores)
    df_score = df_results[df_results.score >= selected_score]

       
    # DATE SELECTION
    date_list_score = df_score.groupby(['date']).count()
    date_list = date_list_score.index
 
    
    # SELECTED DATES
    selected_date = st.selectbox('Select a date', date_list)
    df_date = df_score[df_score.date == selected_date]

    
    # SPORT
    df_sports_prepp = sports_prepp(df_sports)
    df_sport_date = sport_selection(df_sports_prepp, selected_date)


    
    # OLD CODE
    year_list = list(df_reshaped.year.unique())[::-1]    
    selected_year = st.selectbox('Select a year', year_list)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#######################
# Plots

# Barplot
def make_barplot(input_df, input_y, input_x, input_color, input_color_theme):    
    barplot = alt.Chart(input_df).mark_bar().encode(
            x=input_x, #'labels',
            y=input_y, #'sportTime(s)'
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
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

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


# Donut chart
def make_donut(input_response, input_text, input_color):
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
col = st.columns((3.0, 5.5), gap='medium')

with col[0]:
    st.markdown('#### Stress peaks')
    
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


    st.markdown('#### Quality')
    st.dataframe(df_selected_year_sorted,
                 column_order=("states", "population"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "states": st.column_config.TextColumn(
                        "States",
                    ),
                    "population": st.column_config.ProgressColumn(
                        "Population",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.population),
                     )}
                 )

with col[1]:
    st.markdown('#### Stress factors')
       
    barplot_sport = make_barplot(df_sport_date, 'sportTime(s)', 'labels', 'type_text', selected_color_theme)
    st.altair_chart(barplot_sport, use_container_width=True)
            
    choropleth = make_choropleth(df_selected_year, 'states_code', 'population', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)
