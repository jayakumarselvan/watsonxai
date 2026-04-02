"""
CrewAI Stock Analysis & Recommendation System
Using IBM WatsonX.ai as LLM backend

Fix: CrewAI >= 0.70 requires its own crewai.LLM wrapper (backed by LiteLLM),
not a raw LangChain LLM object.  WatsonX is supported via the
"watsonx/<model_id>" provider string in LiteLLM.
"""

import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Optional


# ─────────────────────────────────────────────
# 1.  WatsonX LLM Configuration  (CrewAI-native)
# ─────────────────────────────────────────────


def get_watsonx_llm(
    model_id: str = "meta-llama/llama-3-3-70b-instruct",
    temperature: float = 0.1,
    max_tokens: int = 2048,
) -> LLM:
    """
    Returns a CrewAI LLM backed by IBM WatsonX via LiteLLM.

    Required environment variables:
        WATSONX_APIKEY        – IBM Cloud API key
        WATSONX_URL           – e.g. https://us-south.ml.cloud.ibm.com
        WATSONX_PROJECT_ID    – WatsonX project ID

    LiteLLM provider string format:  "watsonx/<model_id>"
    Docs: https://docs.litellm.ai/docs/providers/watsonx
    """
    api_key = os.environ.get("WATSONX_APIKEY")
    url = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    project_id = os.environ.get("WATSONX_PROJECT_ID")

    if not api_key or not project_id:
        raise EnvironmentError(
            "Missing WatsonX credentials.\n"
            "Please set: WATSONX_APIKEY, WATSONX_URL, WATSONX_PROJECT_ID"
        )

    # LiteLLM reads WATSONX_* env vars automatically; we also pass them
    # explicitly so the LLM object is self-contained.
    return LLM(
        model=f"watsonx/{model_id}",
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
        base_url=url,
        extra_headers={"project_id": project_id},
    )


# ─────────────────────────────────────────────
# 2.  Custom Tools
# ─────────────────────────────────────────────


class StockPriceTool(BaseTool):
    name: str = "stock_price_fetcher"
    description: str = (
        "Fetches current stock price, historical OHLCV data, and key metrics "
        "for a given ticker symbol. Input: ticker symbol (e.g. 'AAPL')."
    )

    def _run(self, ticker: str) -> str:
        try:
            ticker = ticker.strip().upper()
            stock = yf.Ticker(ticker)
            info = stock.info

            # Last 30 days of daily closes
            hist = stock.history(period="1mo")
            if hist.empty:
                return f"No price data found for {ticker}."

            current_price = hist["Close"].iloc[-1]
            prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else current_price
            daily_change_pct = ((current_price - prev_price) / prev_price) * 100

            # Simple moving averages
            sma_7 = hist["Close"].tail(7).mean()
            sma_20 = hist["Close"].tail(20).mean() if len(hist) >= 20 else None

            result = f"""
=== {ticker} Price Data ===
Current Price : ${current_price:.2f}
Daily Change  : {daily_change_pct:+.2f}%
7-Day SMA     : ${sma_7:.2f}
20-Day SMA    : ${sma_20:.2f if sma_20 else 'N/A'}
52-Week High  : ${info.get('fiftyTwoWeekHigh', 'N/A')}
52-Week Low   : ${info.get('fiftyTwoWeekLow', 'N/A')}
Avg Volume    : {info.get('averageVolume', 'N/A'):,}

Recent Closes (last 5 days):
{hist['Close'].tail(5).to_string()}
"""
            return result
        except Exception as e:
            return f"Error fetching price data for {ticker}: {str(e)}"


class FundamentalsTool(BaseTool):
    name: str = "stock_fundamentals"
    description: str = (
        "Returns fundamental financial data for a stock ticker: "
        "P/E ratio, EPS, revenue, profit margin, debt/equity, market cap, etc. "
        "Input: ticker symbol (e.g. 'MSFT')."
    )

    def _run(self, ticker: str) -> str:
        try:
            ticker = ticker.strip().upper()
            info = yf.Ticker(ticker).info

            def fmt(val, prefix="", suffix="", scale=1):
                if val is None or val == "N/A":
                    return "N/A"
                try:
                    return f"{prefix}{val / scale:.2f}{suffix}"
                except Exception:
                    return str(val)

            result = f"""
=== {ticker} Fundamental Data ===
Company        : {info.get('longName', 'N/A')}
Sector         : {info.get('sector', 'N/A')}
Industry       : {info.get('industry', 'N/A')}

Valuation
  Market Cap   : {fmt(info.get('marketCap'), '$', '', 1e9)}B
  P/E Ratio    : {fmt(info.get('trailingPE'))}
  Forward P/E  : {fmt(info.get('forwardPE'))}
  PEG Ratio    : {fmt(info.get('pegRatio'))}
  P/B Ratio    : {fmt(info.get('priceToBook'))}

Profitability
  EPS (TTM)    : {fmt(info.get('trailingEps'), '$')}
  Revenue (TTM): {fmt(info.get('totalRevenue'), '$', '', 1e9)}B
  Profit Margin: {fmt(info.get('profitMargins'), '', '%')}
  ROE          : {fmt(info.get('returnOnEquity'), '', '%')}

Financial Health
  Debt/Equity  : {fmt(info.get('debtToEquity'))}
  Current Ratio: {fmt(info.get('currentRatio'))}
  Free Cash Flow: {fmt(info.get('freeCashflow'), '$', '', 1e9)}B

Dividends
  Dividend Yield: {fmt(info.get('dividendYield'), '', '%')}
  Payout Ratio  : {fmt(info.get('payoutRatio'), '', '%')}

Analyst Consensus: {info.get('recommendationKey', 'N/A').upper()}
Target Mean Price: {fmt(info.get('targetMeanPrice'), '$')}
"""
            return result
        except Exception as e:
            return f"Error fetching fundamentals for {ticker}: {str(e)}"


class TechnicalIndicatorTool(BaseTool):
    name: str = "technical_indicators"
    description: str = (
        "Calculates RSI, MACD, Bollinger Bands, and momentum indicators "
        "for a given ticker. Input: ticker symbol."
    )

    def _run(self, ticker: str) -> str:
        try:
            ticker = ticker.strip().upper()
            hist = yf.Ticker(ticker).history(period="6mo")
            if hist.empty or len(hist) < 26:
                return f"Not enough data to compute indicators for {ticker}."

            close = hist["Close"]

            # RSI (14-period)
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_now = rsi.iloc[-1]

            # MACD
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_hist = macd_line - signal_line

            # Bollinger Bands (20-period, 2σ)
            sma20 = close.rolling(20).mean()
            std20 = close.rolling(20).std()
            bb_upper = sma20 + 2 * std20
            bb_lower = sma20 - 2 * std20
            price_now = close.iloc[-1]

            # Momentum
            momentum_10 = (
                ((price_now - close.iloc[-11]) / close.iloc[-11]) * 100
                if len(close) > 10
                else None
            )

            rsi_signal = (
                "Overbought"
                if rsi_now > 70
                else ("Oversold" if rsi_now < 30 else "Neutral")
            )
            macd_signal = "Bullish" if macd_hist.iloc[-1] > 0 else "Bearish"
            bb_signal = (
                "Near Upper Band (overbought zone)"
                if price_now >= bb_upper.iloc[-1]
                else (
                    "Near Lower Band (oversold zone)"
                    if price_now <= bb_lower.iloc[-1]
                    else "Within Bands (neutral)"
                )
            )

            result = f"""
=== {ticker} Technical Indicators ===
Current Price    : ${price_now:.2f}

RSI (14)         : {rsi_now:.1f}  → {rsi_signal}
MACD Line        : {macd_line.iloc[-1]:.4f}
Signal Line      : {signal_line.iloc[-1]:.4f}
MACD Histogram   : {macd_hist.iloc[-1]:.4f}  → {macd_signal} crossover
10-Day Momentum  : {f'{momentum_10:+.2f}%' if momentum_10 else 'N/A'}

Bollinger Bands (20, 2σ)
  Upper Band     : ${bb_upper.iloc[-1]:.2f}
  Middle (SMA20) : ${sma20.iloc[-1]:.2f}
  Lower Band     : ${bb_lower.iloc[-1]:.2f}
  Position       : {bb_signal}

Overall Technical Signal: {'BULLISH' if macd_signal == 'Bullish' and rsi_now < 70 else 'BEARISH' if macd_signal == 'Bearish' and rsi_now > 30 else 'MIXED/NEUTRAL'}
"""
            return result
        except Exception as e:
            return f"Error computing indicators for {ticker}: {str(e)}"


class NewsAndSentimentTool(BaseTool):
    name: str = "news_sentiment"
    description: str = (
        "Retrieves recent news headlines for a stock ticker and summarises "
        "the news context. Input: ticker symbol."
    )

    def _run(self, ticker: str) -> str:
        try:
            ticker = ticker.strip().upper()
            stock = yf.Ticker(ticker)
            news = stock.news

            if not news:
                return f"No recent news found for {ticker}."

            headlines = []
            for item in news[:8]:  # top 8 articles
                title = item.get("title", "No title")
                publisher = item.get("publisher", "Unknown")
                ts = item.get("providerPublishTime", 0)
                date_str = (
                    datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d") if ts else "N/A"
                )
                headlines.append(f"  [{date_str}] {title}  — {publisher}")

            return f"=== {ticker} Recent News ===\n" + "\n".join(headlines)
        except Exception as e:
            return f"Error fetching news for {ticker}: {str(e)}"


# ─────────────────────────────────────────────
# 3.  Agents
# ─────────────────────────────────────────────


def build_crew(ticker: str) -> Crew:
    llm = get_watsonx_llm()

    tools_price = [StockPriceTool()]
    tools_fund = [FundamentalsTool()]
    tools_tech = [TechnicalIndicatorTool()]
    tools_news = [NewsAndSentimentTool()]
    tools_all = tools_price + tools_fund + tools_tech + tools_news

    # --- Agent 1: Market Data Analyst ---
    market_analyst = Agent(
        role="Senior Market Data Analyst",
        goal=(
            f"Gather comprehensive price data and technical indicators for {ticker}. "
            "Identify trends, support/resistance levels, and price momentum."
        ),
        backstory=(
            "You are a seasoned quantitative analyst with 15 years of experience "
            "in equity markets. You specialise in reading price action and technical "
            "patterns to forecast near-term stock movements."
        ),
        tools=tools_price + tools_tech,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # --- Agent 2: Fundamental Analyst ---
    fundamental_analyst = Agent(
        role="Fundamental Research Analyst",
        goal=(
            f"Analyse the financial health and intrinsic value of {ticker}. "
            "Evaluate earnings quality, growth trajectory, and valuation multiples."
        ),
        backstory=(
            "You are a CFA charterholder with deep expertise in financial statement "
            "analysis. You assess companies using bottom-up fundamental research and "
            "compare them against sector peers."
        ),
        tools=tools_fund,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # --- Agent 3: News & Sentiment Analyst ---
    sentiment_analyst = Agent(
        role="News & Sentiment Analyst",
        goal=(
            f"Assess the current news sentiment and macro narrative around {ticker}. "
            "Identify any catalysts, risks, or events that may drive price action."
        ),
        backstory=(
            "You are an expert in media analysis and behavioural finance. You track "
            "market-moving headlines and quantify how news flow affects investor sentiment "
            "and stock volatility."
        ),
        tools=tools_news,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # --- Agent 4: Chief Investment Strategist (synthesiser) ---
    strategist = Agent(
        role="Chief Investment Strategist",
        goal=(
            f"Synthesise insights from all analysts to produce a clear BUY / HOLD / SELL "
            f"recommendation for {ticker} with supporting rationale and risk factors."
        ),
        backstory=(
            "You are a portfolio manager who has led a top-quartile equity fund for a decade. "
            "You integrate technical, fundamental, and sentiment signals into a single, "
            "actionable investment thesis, clearly communicating conviction and risk."
        ),
        tools=tools_all,
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )

    # ─────────────────────────────────────────────
    # 4.  Tasks
    # ─────────────────────────────────────────────

    task_technical = Task(
        description=(
            f"Perform a full technical analysis of {ticker}. "
            "Fetch current price data and compute RSI, MACD, and Bollinger Bands. "
            "Identify key support and resistance levels, trend direction, and any "
            "technical buy or sell signals."
        ),
        expected_output=(
            "A structured technical analysis report including:\n"
            "- Current price and recent price action summary\n"
            "- RSI, MACD, and Bollinger Band readings with interpretation\n"
            "- Key support / resistance levels\n"
            "- Overall technical bias (Bullish / Bearish / Neutral) with reasoning"
        ),
        agent=market_analyst,
    )

    task_fundamental = Task(
        description=(
            f"Conduct a thorough fundamental analysis of {ticker}. "
            "Retrieve valuation multiples (P/E, PEG, P/B), profitability metrics, "
            "financial health indicators, and analyst consensus. "
            "Determine whether the stock is overvalued, fairly valued, or undervalued."
        ),
        expected_output=(
            "A structured fundamental analysis report including:\n"
            "- Company overview (sector, industry)\n"
            "- Valuation assessment with key ratios\n"
            "- Profitability and growth metrics\n"
            "- Balance sheet health\n"
            "- Intrinsic value assessment and analyst consensus"
        ),
        agent=fundamental_analyst,
    )

    task_sentiment = Task(
        description=(
            f"Analyse recent news and sentiment for {ticker}. "
            "Review the latest headlines and identify positive or negative catalysts, "
            "regulatory concerns, earnings surprises, or macro risks."
        ),
        expected_output=(
            "A sentiment summary including:\n"
            "- List of top recent headlines\n"
            "- Overall sentiment tone (Positive / Negative / Neutral)\n"
            "- Key catalysts or risks identified\n"
            "- Potential near-term impact on stock price"
        ),
        agent=sentiment_analyst,
    )

    task_recommendation = Task(
        description=(
            f"Based on the technical, fundamental, and sentiment analyses for {ticker}, "
            "produce a final investment recommendation. "
            "Provide a clear BUY / HOLD / SELL rating with:\n"
            "  - A concise investment thesis (3-5 sentences)\n"
            "  - Price target (12-month)\n"
            "  - Key upside catalysts\n"
            "  - Key downside risks\n"
            "  - Suggested position sizing (high / medium / low conviction)\n"
            "Format as a professional equity research note."
        ),
        expected_output=(
            "A professional equity research note with:\n"
            "1. RATING: BUY / HOLD / SELL\n"
            "2. Price Target (12-month)\n"
            "3. Investment Thesis\n"
            "4. Supporting Evidence (technical + fundamental + sentiment)\n"
            "5. Catalysts\n"
            "6. Risks\n"
            "7. Conviction Level"
        ),
        agent=strategist,
        context=[task_technical, task_fundamental, task_sentiment],
    )

    # ─────────────────────────────────────────────
    # 5.  Crew
    # ─────────────────────────────────────────────

    crew = Crew(
        agents=[market_analyst, fundamental_analyst, sentiment_analyst, strategist],
        tasks=[task_technical, task_fundamental, task_sentiment, task_recommendation],
        process=Process.sequential,
        verbose=True,
    )

    return crew


# ─────────────────────────────────────────────
# 6.  Entry Point
# ─────────────────────────────────────────────


def analyse_stock(ticker: str) -> str:
    print(f"\n{'='*60}")
    print(f"  CREWAI STOCK ANALYSIS: {ticker.upper()}")
    print(f"  Powered by IBM WatsonX.ai")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    crew = build_crew(ticker)
    result = crew.kickoff()
    return result


if __name__ == "__main__":
    # ── Example: analyse Apple ──────────────────
    # You can change this or accept CLI input
    import sys

    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    report = analyse_stock(ticker)
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(report)
