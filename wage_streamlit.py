import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px

st.title('Japanese wage data dashboard')

df_jp_ind=pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_全産業.csv',encoding='shift_jis')
df_jp_category=pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_大分類.csv',encoding='shift_jis')
df_pref_ind=pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv',encoding='shift_jis')

st.header("■2019 Heat Map of Average Wages per Person")

jp_lat_lon = pd.read_csv('./pref_lat_lon.csv')
jp_lat_lon=jp_lat_lon.rename(columns={'pref_name':'都道府県名'})

df_pref_map = df_pref_ind[(df_pref_ind['年齢']=='年齢計')&(df_pref_ind['集計年']==2019)]
#結合処理
df_pref_map = pd.merge(df_pref_map,jp_lat_lon, on ='都道府県名')
#正規化
df_pref_map['一人当たり賃金（相対値）'] = ((df_pref_map['一人当たり賃金（万円）']-df_pref_map['一人当たり賃金（万円）'].min())/(df_pref_map['一人当たり賃金（万円）'].max()-df_pref_map['一人当たり賃金（万円）'].min()))


#真ん中(東京）,拡大する値、角度
view = pdk.ViewState(
    longitude = 139.691648,
    latitude=35.689185,
    zoom =4,
    pitch = 40.5
)

layer = pdk.Layer(
    'HeatmapLayer',
    data = df_pref_map,
    opacity = 0.4,
    get_position=['lon','lat'],
    threshold = 0.3,
    get_weight = '一人当たり賃金（相対値）'
)

layer_map = pdk.Deck(
    layers=layer,
    initial_view_state=view
)

st.pydeck_chart(layer_map)

show_df = st.checkbox('Show DataFrame')
if show_df == True :
    st.write(df_pref_map)


st.header('■Transition of wage per person by years')

df_ts_mean = df_jp_ind[df_jp_ind['年齢']=='年齢計']
df_ts_mean = df_ts_mean.rename(columns={'一人当たり賃金（万円）':'全国_一人当たり賃金（万円）'})

df_pref_mean = df_pref_ind[df_pref_ind['年齢']=='年齢計']
pref_list = df_pref_mean['都道府県名'].unique()
option_pref=st.selectbox(
    '都道府県',
    (pref_list)
)
df_pref_mean = df_pref_mean[df_pref_mean['都道府県名']==option_pref]
#表を結合
df_mean_line = pd.merge(df_ts_mean,df_pref_mean,on='集計年')
#列を絞る
df_mean_line = df_mean_line[['集計年','全国_一人当たり賃金（万円）','一人当たり賃金（万円）']]
#列をINDEXに変更
df_mean_line = df_mean_line.set_index('集計年')
#折れ線グラフ
st.line_chart(df_mean_line)

st.header('■Avarage wage per person by years（￥10K）')

df_mean_bubble = df_jp_ind[df_jp_ind['年齢'] !='年齢計']

#アニメーション系はplotly
fig = px.scatter( df_mean_bubble,
                  x = "一人当たり賃金（万円）",
                  y = "年間賞与その他特別給与額（万円）",
                  range_x = [150,700],
                  range_y = [0,150],
                  size = "所定内給与額（万円）",
                  size_max = 38,
                  color = "年齢",
                  animation_frame="集計年",
                  animation_group="年齢"
)
st.plotly_chart(fig)

st.header('■Transition of wage by Category')

year_list = df_jp_category['集計年'].unique()
option_year = st.selectbox(
    '集計年',
    year_list
)
wage_list = ['一人当たり賃金（万円）','所定内給与額（万円）','年間賞与その他特別給与額（万円）']
option_wage = st.selectbox(
    '賃金の種類',
    wage_list
)
df_mean_categ = df_jp_category[df_jp_category['集計年']==option_year]

max_x = df_mean_categ[option_wage].max() +50

fig = px.bar(df_mean_categ,
            x=option_wage,
            y='産業大分類名',
            animation_frame='年齢',
            color ='産業大分類名',
            range_x=[0,max_x],
            orientation='h',
            width=800,
            height = 500
)
st.plotly_chart(fig)

st.text('Reference : RESAS（地域経済分析システム）')
st.text('This dashboard was made by editing data from RESAS（地域経済分析システム）')