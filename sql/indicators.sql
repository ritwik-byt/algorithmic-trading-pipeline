USE trading_platform;

-- Drop table if it already exists to avoid errors when rewriting
DROP TABLE IF EXISTS TradingSignals;

-- Create a new table to store calculated trading indicators
CREATE TABLE TradingSignals AS
WITH BaseCalculations AS (
    SELECT 
        Date,
        Ticker,
        Close,
        Volume,
        -- 1. Calculate Daily Financial Return using LAG()
        (Close - LAG(Close, 1) OVER (PARTITION BY Ticker ORDER BY Date)) / LAG(Close, 1) OVER (PARTITION BY Ticker ORDER BY Date) AS DailyReturn,
        
        -- 2. Calculate the 20-Day Simple Moving Average (Short-term Trend)
        AVG(Close) OVER (PARTITION BY Ticker ORDER BY Date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS MA20,
        
        -- 3. Calculate the 50-Day Simple Moving Average (Long-term Trend)
        AVG(Close) OVER (PARTITION BY Ticker ORDER BY Date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS MA50,
        
        -- 4. Calculate Rolling Volatility (30-day Standard Deviation)
        STDDEV_SAMP(Close) OVER (PARTITION BY Ticker ORDER BY Date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS Volatility30,
        
        -- 5. Track the Peak Historical Price up to today for Drawdown calculation
        MAX(Close) OVER (PARTITION BY Ticker ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS HistoricalPeak,
        
        -- 6. Track the 20-Day Average Volume to find institutional trading volume spikes
        AVG(Volume) OVER (PARTITION BY Ticker ORDER BY Date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS AvgVolume20
    FROM StockPrices
),
SignalGeneration AS (
    SELECT 
        *,
        -- 7. Calculate Peak-to-Trough Drawdown (Max loss from the highest peak)
        ((Close - HistoricalPeak) / HistoricalPeak) * 100 AS DrawdownPct,
        
        -- 8. Volume Spike Flag (1 if today's volume is double the 20-day average)
        CASE WHEN Volume > (2 * AvgVolume20) THEN 1 ELSE 0 END AS VolumeSpike,
        
        -- 9. Moving Average Crossover Strategy (BUY when short trend passes long trend)
        CASE WHEN MA20 > MA50 THEN 'BUY' ELSE 'SELL' END AS SignalFlag
    FROM BaseCalculations
)
SELECT * FROM SignalGeneration;

-- Verify our engineering calculations by selecting the top rows
SELECT * FROM TradingSignals LIMIT 10;