# Nifty 50 Market Sentiment Dashboard

Real-time news and AI sentiment analysis for Nifty 50 stocks, powered by OpenRouter.

---

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get an API key** from [openrouter.ai](https://openrouter.ai) and add it to your `.env` file
   ```env
   OPENROUTER_API_KEY=your-key-here
   OPENROUTER_MODEL=openai/gpt-4o-mini
   ```

3. **Run the dashboard**
   ```bash
   streamlit run news_dashboard_3.py
   ```

Opens at `http://localhost:8501`.

---

## Notes

- Change the stock list or model inside `news_dashboard_3.py`
- Never commit your `.env` file
- Any model from [openrouter.ai/models](https://openrouter.ai/models) works
