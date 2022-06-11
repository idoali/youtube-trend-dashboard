# Data processing libraries
import pandas as pd
import pickle
import json
from datetime import date
from PIL import Image

# Dashboard library
import streamlit as st

# Data visualizations library
import plotly.express as px
px.defaults.template = "plotly_dark"
px.defaults.color_continuous_scale = "reds"

# Membuka file pickle dan json
with open("data_input/trending.pickle", "rb") as f: 
    df = pickle.load(f) 
    
with open("data_input/category.json", 'rb') as f:
    category_json = json.load(f)
    json_norm = pd.json_normalize(category_json, record_path="items")
    category = {int(x):y for x, y in zip(json_norm['id'], json_norm['snippet.title'])}

# Mengubah nilai yang ada pada kolom kategori
category_nums = category.keys()
df['category_id'] = [category[x] if x in category_nums else "Unknown" for x in df['category_id']]

category_ids = pd.DataFrame(list(df['category_id'].value_counts().keys()) + ['All Categories']).sort_values(0)[0].tolist()

# Mengubah nilai NA menjadi 0
df.loc[:, ['like', 'dislike', 'view', 'comment']] = df.loc[:, ['like', 'dislike', 'view', 'comment']].fillna(0)

# Menambahkan kolom waktu yang lebih spesifik
df['trending_date'] = df['trending_time'].dt.date

youtube_unique = df.drop_duplicates(subset=['channel_name', 'title'], keep='first').copy()

# Tampilan logo YouTube
image = Image.open('assets/youtube.png')
st.sidebar.image(image)

# Input tanggal
min_date = youtube_unique['trending_date'].min()
max_date = youtube_unique['trending_date'].max()
selected_start_date, selected_end_date = st.sidebar.date_input(
    label='Trending Date Range',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date])

# Input kategori
selected_category = st.sidebar.selectbox(
    label='Video Category',
    options=category_ids)

# Filter data sesuai dengan input
# Input tanggal
selected_data = youtube_unique[
    (youtube_unique['trending_date'] >= selected_start_date) &
    (youtube_unique['trending_date'] <= selected_end_date)]

# Input kategori
if selected_category != "All Categories":
    selected_data = selected_data[selected_data["category_id"] == selected_category]

# bar chart
st.header(':video_camera: Channels')
data = selected_data['channel_name'].value_counts().nlargest(10).sort_values(ascending=True)
fig = px.bar(
    data,
    orientation='h',
    title=f'Top 10 Trending Channels in {selected_category}',
    labels=dict(index='', value='Video Count'),
    color=data)
fig.update_layout(coloraxis_showscale=False, xaxis_separatethousands=True)
fig.update_traces(hovertemplate='<b>%{y}</b><br>%{x} Videos', name='')
st.plotly_chart(fig)

# scatter plot
st.header(':bulb: Engagement')
metric_choices = ['like', 'dislike', 'comment']
col1, col2 = st.columns(2)
var_x = col1.selectbox(label='Horizontal Axis',
                       options=metric_choices, index=0)
var_y = col2.selectbox(label='Vertical Axis', options=metric_choices, index=1)

fig = px.scatter(
    selected_data,
    x=var_x,
    y=var_y,
    size='view',
    title=f'{var_x.title()} vs {var_y.title()} in {selected_category}',
    hover_name='channel_name',
    hover_data=['title'])
st.plotly_chart(fig)
