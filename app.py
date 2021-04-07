# 基本モジュール
import streamlit as st
import pandas as pd

# 便率なツール
import streamlit.components.v1 as comp

# データ読み込みに使用
import yfinance as yf
from pandas_datareader import data as wb

# データの表示に使用
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# 日付の取得に使用
import datetime


st.title('Stock Analyzer')

# サイドバー 会社選択のためのデータフレーム
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
df_spc = pd.read_html(url)
df_spc = df_spc[0]['Symbol']

main_company = st.sidebar.selectbox('会社を選択', df_spc.unique().tolist())
main_data = yf.Ticker(main_company) #ここが時間かかる
main_symbol = main_data.info['symbol']
main_name = main_data.info['shortName']
st.sidebar.write(main_name)
comp_list = st.sidebar.multiselect('比較対象', df_spc.unique().tolist())


# 選択した会社の情報を元にデータフレームを作成
today = datetime.date.today()
date_latest = today - datetime.timedelta(days=3)
date_range = st.slider('表示期間', datetime.date(2013,1,1), date_latest, value=(datetime.date(2013,1,1), date_latest))
date_start = date_range[0]
date_end = date_range[1]
df = main_data.history(period='1d', start=date_start, end=date_end)


# 選択した会社の基礎的な情報を表示
with st.beta_expander('Company Information'):
    # st.write(main_data.info)    
    st.write(main_data.info['sector'])
    st.write(main_data.info['longBusinessSummary'])
    st.subheader('選択した会社の終値の推移(Close)と取引量(Volume)')
    st.line_chart(df.Close)
    st.line_chart(df.Volume)

    # Dateフィールドを使いたいのでreset_index
    df = df.reset_index()

    data1 = go.Line(x=df['Date'], y=df['Close'], text=df['Close'], name='Close', yaxis='y1')
    data2 = go.Bar(x=df['Date'], y=df['Volume'], text=df['Volume'], name='Volume', yaxis='y2')
    layout = go.Layout(
        title='TITLE',
        xaxis=dict(title='Date', showgrid=False, range=[date_start, date_end]),
        yaxis=dict(title='Close', side='left', showgrid=False),
        yaxis2=dict(title='Volume', side='right', overlaying='y', showgrid=False),
        )
    fig = go.Figure(data=[data1, data2], layout=layout)
    st.plotly_chart(fig)


with st.beta_expander('Stock Information'):
    # 比較対象があればグラフを表示
    if len(comp_list) > 0:
        st.subheader('比較グラフ')
        df_adj = pd.DataFrame()
        df_adj[main_symbol] = wb.DataReader(main_symbol, data_source='yahoo', start=date_start, end=date_end)['Adj Close']

        for i, comp in enumerate(comp_list):
            # st.sidebar.write(comp_list[i])
            st.sidebar.write(yf.Ticker(comp_list[i]).info['shortName'])
            comp_symbol = comp_list[i]
            df_adj[comp_symbol] = wb.DataReader(comp_symbol, data_source='yahoo', start=date_start, end=date_end)['Adj Close']

        st.line_chart(df_adj)
            
        st.subheader('スタートを100としてグラフ化')
        st.line_chart((df_adj / df_adj.iloc[0] * 100))

        st.subheader('相関係数')
        df_corr = df_adj.corr()
        st.write(df_corr)
        st.write('ヒートマップ')
        fig, ax = plt.subplots()
        sns.heatmap(df_corr, annot=True, ax=ax)
        st.pyplot(fig)
    else:
        st.write('比較対象がありません。')

    # st.write(df_spc)

    # 辞書の情報をデータフレームにする
    # dict_info={}
    # for k,v in main_data.info.items():
    #     dict_info[k]=pd.Series(v)
    # st.dataframe(dict_info)

    

