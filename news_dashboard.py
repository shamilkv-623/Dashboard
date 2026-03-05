import streamlit as st
import feedparser
import requests
import pandas as pd
import time
import urllib.parse
import yfinance as yf

feedparser.USER_AGENT = "Mozilla/5.0"

# =========================
# CONFIG
# =========================

# use your api key and model here

OPENROUTER_API_KEY = ""
MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"

stocks = [
"Adani Enterprises","Adani Ports","Apollo Hospitals","Asian Paints","Axis Bank",
"Bajaj Auto","Bajaj Finance","Bajaj Finserv","Bharat Electronics","Bharti Airtel",
"BPCL","Britannia Industries","Cipla","Coal India","Divis Laboratories",
"Dr Reddys Laboratories","Eicher Motors","Grasim Industries","HCL Technologies",
"HDFC Bank","HDFC Life","Hero MotoCorp","Hindalco Industries",
"Hindustan Unilever","ICICI Bank","ITC","IndusInd Bank","Infosys",
"JSW Steel","Kotak Mahindra Bank","Larsen & Toubro","LTIMindtree",
"Mahindra & Mahindra","Maruti Suzuki","Nestle India","NTPC","ONGC",
"Power Grid","Reliance Industries","SBI Life Insurance",
"State Bank of India","Sun Pharma","TCS","Tata Consumer Products",
"Tata Motors","Tata Steel","Tech Mahindra","Titan","UltraTech Cement","Wipro"
]

# =========================
# FETCH NEWS
# =========================

def fetch_news(query):

    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"

    feed = feedparser.parse(url)

    articles = []

    for entry in feed.entries[:5]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })

    return articles


# =========================
# LLM ANALYSIS
# =========================

def analyze_news(article):

    prompt = f"""
You are a financial analyst.

Classify the impact of this headline on the stock.

Headline:
{article}

Return format:

Impact: Positive / Negative / Neutral
Reason: one short sentence
"""

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "Stock Dashboard"
            },
            json={
                "model": MODEL,
                "messages":[
                    {"role":"user","content":prompt}
                ]
            }
        )

        result = response.json()

        if "choices" not in result:
            return "Neutral"

        return result["choices"][0]["message"]["content"]

    except:
        return "Neutral"


# =========================
# STOCK PRICE SNAPSHOT
# =========================

def get_stock_price(stock):

    try:
        ticker = stock.replace(" ","") + ".NS"
        data = yf.Ticker(ticker)

        price = data.history(period="1d")

        if len(price) > 0:

            current = price["Close"].iloc[-1]
            open_price = price["Open"].iloc[-1]

            change = ((current - open_price) / open_price) * 100

            return round(current,2), round(change,2)

    except:
        pass

    return None, None


# =========================
# UI
# =========================

st.title("📈 AI Stock News Dashboard")

selected_stock = st.selectbox("Select Stock",stocks)

price,change = get_stock_price(selected_stock)

if price:

    col1,col2 = st.columns(2)

    col1.metric("Price",f"₹{price}")
    col2.metric("Daily Change",f"{change} %")

# =========================
# NEWS SECTION
# =========================

if st.button("Fetch News"):

    results=[]

    articles=fetch_news(selected_stock)

    for article in articles:

        sentiment=analyze_news(article["title"])

        results.append({
            "Company":selected_stock,
            "Date":article["published"],
            "Headline":article["title"],
            "Analysis":sentiment,
            "Link":article["link"]
        })

        time.sleep(0.5)

    df=pd.DataFrame(results)

    df["Date"]=pd.to_datetime(df["Date"],errors="coerce")

    df=df.sort_values("Date",ascending=False)

    st.subheader("📰 Latest News")

    st.dataframe(df)

    # sentiment counts
    positive=len(df[df["Analysis"].str.contains("Positive")])
    negative=len(df[df["Analysis"].str.contains("Negative")])
    neutral=len(df)-positive-negative

    chart_df=pd.DataFrame({
        "Sentiment":["Positive","Negative","Neutral"],
        "Count":[positive,negative,neutral]
    })

    st.subheader("📊 News Sentiment")
    st.bar_chart(chart_df.set_index("Sentiment"))

    # detailed news cards
    for _,row in df.iterrows():

        with st.container():

            st.markdown(f"### {row['Headline']}")
            st.write(row["Analysis"])
            st.markdown(f"[Read Article]({row['Link']})")

            st.divider()


# =========================
# MARKET SENTIMENT
# =========================

st.sidebar.header("📊 Market Sentiment")

positive=0
negative=0
neutral=0

for stock in stocks[:8]:

    news=fetch_news(stock)

    for article in news:

        sentiment=analyze_news(article["title"])

        if "Positive" in sentiment:
            positive+=1
        elif "Negative" in sentiment:
            negative+=1
        else:
            neutral+=1


col1,col2,col3=st.sidebar.columns(3)

col1.metric(" Positive",positive)
col2.metric(" Negative",negative)
col3.metric(" Neutral",neutral)


# =========================
# TRENDING STOCKS
# =========================

st.sidebar.header("Trending Stocks")

trend_data=[]

for stock in stocks[:6]:

    news=fetch_news(stock)

    trend_data.append({
        "Stock":stock,
        "News Count":len(news)
    })

trend_df=pd.DataFrame(trend_data)

trend_df=trend_df.sort_values("News Count",ascending=False)

st.sidebar.dataframe(trend_df)


# =========================
# ECONOMIC NEWS
# =========================

st.sidebar.header(" Economic News")

macro_news=fetch_news("India economy OR RBI OR inflation OR GDP")

for article in macro_news:

    st.sidebar.write("•",article["title"])

