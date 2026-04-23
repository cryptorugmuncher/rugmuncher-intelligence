/**
 * MunchScan Prediction Algorithms
 * Simple technical analysis and prediction algorithms for crypto charts
 * 
 * ⚠️ DISCLAIMER: These are for visualization purposes only!
 * NOT financial advice. Always DYOR (Do Your Own Research).
 */

class PredictionEngine {
    constructor() {
        this.indicators = {};
    }

    /**
     * Simple Moving Average (SMA)
     * @param {Array} data - Array of price data
     * @param {number} period - MA period
     * @returns {Array} - MA values
     */
    calculateSMA(data, period = 20) {
        const result = [];
        for (let i = period - 1; i < data.length; i++) {
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += data[i - j].close;
            }
            result.push({
                time: data[i].time,
                value: sum / period
            });
        }
        return result;
    }

    /**
     * Exponential Moving Average (EMA)
     * @param {Array} data - Array of price data
     * @param {number} period - EMA period
     * @returns {Array} - EMA values
     */
    calculateEMA(data, period = 20) {
        const multiplier = 2 / (period + 1);
        const result = [];
        let ema = data[0].close;
        
        for (let i = 0; i < data.length; i++) {
            ema = (data[i].close - ema) * multiplier + ema;
            result.push({
                time: data[i].time,
                value: ema
            });
        }
        return result;
    }

    /**
     * Relative Strength Index (RSI)
     * @param {Array} data - Array of price data
     * @param {number} period - RSI period (default 14)
     * @returns {Array} - RSI values (0-100)
     */
    calculateRSI(data, period = 14) {
        const result = [];
        let gains = 0;
        let losses = 0;

        // Calculate initial averages
        for (let i = 1; i <= period; i++) {
            const change = data[i].close - data[i - 1].close;
            if (change > 0) gains += change;
            else losses += Math.abs(change);
        }

        let avgGain = gains / period;
        let avgLoss = losses / period;

        for (let i = period; i < data.length; i++) {
            const change = data[i].close - data[i - 1].close;
            const gain = change > 0 ? change : 0;
            const loss = change < 0 ? Math.abs(change) : 0;

            avgGain = (avgGain * (period - 1) + gain) / period;
            avgLoss = (avgLoss * (period - 1) + loss) / period;

            const rs = avgGain / avgLoss;
            const rsi = 100 - (100 / (1 + rs));

            result.push({
                time: data[i].time,
                value: rsi
            });
        }

        return result;
    }

    /**
     * Bollinger Bands
     * @param {Array} data - Array of price data
     * @param {number} period - Period (default 20)
     * @param {number} stdDev - Standard deviations (default 2)
     * @returns {Object} - Upper, middle, lower bands
     */
    calculateBollingerBands(data, period = 20, stdDev = 2) {
        const upper = [];
        const middle = [];
        const lower = [];

        for (let i = period - 1; i < data.length; i++) {
            // Calculate SMA (middle band)
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += data[i - j].close;
            }
            const sma = sum / period;

            // Calculate standard deviation
            let squaredDiffs = 0;
            for (let j = 0; j < period; j++) {
                squaredDiffs += Math.pow(data[i - j].close - sma, 2);
            }
            const standardDeviation = Math.sqrt(squaredDiffs / period);

            upper.push({ time: data[i].time, value: sma + (standardDeviation * stdDev) });
            middle.push({ time: data[i].time, value: sma });
            lower.push({ time: data[i].time, value: sma - (standardDeviation * stdDev) });
        }

        return { upper, middle, lower };
    }

    /**
     * MACD (Moving Average Convergence Divergence)
     * @param {Array} data - Array of price data
     * @returns {Object} - MACD line, signal line, histogram
     */
    calculateMACD(data) {
        const ema12 = this.calculateEMA(data, 12);
        const ema26 = this.calculateEMA(data, 26);
        
        const macdLine = [];
        for (let i = 0; i < ema26.length; i++) {
            macdLine.push({
                time: ema26[i].time,
                value: ema12[i + 14].value - ema26[i].value
            });
        }

        // Signal line (9-day EMA of MACD)
        const signalLine = this.calculateEMA(macdLine, 9);
        
        // Histogram
        const histogram = [];
        for (let i = 0; i < signalLine.length; i++) {
            histogram.push({
                time: signalLine[i].time,
                value: macdLine[i + 8].value - signalLine[i].value
            });
        }

        return { macdLine, signalLine, histogram };
    }

    /**
     * Linear Regression Forecast
     * Predicts future prices based on linear trend
     * @param {Array} data - Array of price data
     * @param {number} periods - Number of periods to predict
     * @returns {Array} - Predicted values with confidence
     */
    linearRegressionForecast(data, periods = 24) {
        const n = data.length;
        const x = [];
        const y = [];
        
        for (let i = 0; i < n; i++) {
            x.push(i);
            y.push(data[i].close);
        }

        // Calculate slope and intercept
        let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
        for (let i = 0; i < n; i++) {
            sumX += x[i];
            sumY += y[i];
            sumXY += x[i] * y[i];
            sumX2 += x[i] * x[i];
        }

        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;

        // Generate predictions
        const predictions = [];
        let lastTime = data[data.length - 1].time;
        
        for (let i = 1; i <= periods; i++) {
            const predictedValue = slope * (n + i) + intercept;
            const confidence = Math.max(0, 100 - (i * 4)); // Confidence decreases over time
            
            predictions.push({
                time: lastTime + (i * 3600), // Assuming hourly data
                value: predictedValue,
                confidence: confidence,
                upperBound: predictedValue * (1 + (100 - confidence) / 500),
                lowerBound: predictedValue * (1 - (100 - confidence) / 500)
            });
        }

        return predictions;
    }

    /**
     * Volume Analysis
     * Detects volume spikes and trends
     * @param {Array} data - Array of OHLCV data
     * @returns {Object} - Volume analysis
     */
    analyzeVolume(data) {
        const volumes = data.map(d => d.volume);
        const avgVolume = volumes.reduce((a, b) => a + b, 0) / volumes.length;
        const lastVolume = volumes[volumes.length - 1];
        
        return {
            averageVolume: avgVolume,
            currentVolume: lastVolume,
            volumeRatio: lastVolume / avgVolume,
            isSpike: lastVolume > avgVolume * 2,
            trend: lastVolume > avgVolume ? 'above_average' : 'below_average'
        };
    }

    /**
     * Trend Analysis
     * Determines overall trend direction
     * @param {Array} data - Array of price data
     * @returns {Object} - Trend information
     */
    analyzeTrend(data) {
        const shortTerm = data.slice(-20);
        const longTerm = data.slice(-50);
        
        const shortMA = shortTerm.reduce((a, b) => a + b.close, 0) / shortTerm.length;
        const longMA = longTerm.reduce((a, b) => a + b.close, 0) / longTerm.length;
        
        const currentPrice = data[data.length - 1].close;
        
        // Determine trend
        let trend = 'neutral';
        let strength = 0;
        
        if (shortMA > longMA * 1.02) {
            trend = 'bullish';
            strength = (shortMA / longMA - 1) * 50;
        } else if (shortMA < longMA * 0.98) {
            trend = 'bearish';
            strength = (1 - shortMA / longMA) * 50;
        }

        // Calculate support and resistance (simplified)
        const prices = data.map(d => d.close);
        const support = Math.min(...prices.slice(-20));
        const resistance = Math.max(...prices.slice(-20));

        return {
            direction: trend,
            strength: Math.min(strength, 100),
            shortMA,
            longMA,
            support,
            resistance,
            distanceToSupport: ((currentPrice - support) / support * 100).toFixed(2),
            distanceToResistance: ((resistance - currentPrice) / currentPrice * 100).toFixed(2)
        };
    }

    /**
     * Generate Trading Signal
     * Combines multiple indicators for a signal
     * @param {Array} data - Array of price data
     * @returns {Object} - Trading signal
     */
    generateSignal(data) {
        const rsi = this.calculateRSI(data);
        const macd = this.calculateMACD(data);
        const trend = this.analyzeTrend(data);
        const bb = this.calculateBollingerBands(data);
        
        const lastRSI = rsi[rsi.length - 1]?.value || 50;
        const lastMACD = macd.macdLine[macd.macdLine.length - 1]?.value || 0;
        const lastSignal = macd.signalLine[macd.signalLine.length - 1]?.value || 0;
        const currentPrice = data[data.length - 1].close;
        const bbLower = bb.lower[bb.lower.length - 1]?.value || currentPrice;
        const bbUpper = bb.upper[bb.upper.length - 1]?.value || currentPrice;
        
        let signal = 'neutral';
        let confidence = 50;
        let reasons = [];

        // RSI signals
        if (lastRSI < 30) {
            signal = 'buy';
            confidence += 15;
            reasons.push('RSI oversold');
        } else if (lastRSI > 70) {
            signal = 'sell';
            confidence += 15;
            reasons.push('RSI overbought');
        }

        // MACD signals
        if (lastMACD > lastSignal && lastMACD > 0) {
            if (signal === 'buy') confidence += 10;
            else if (signal === 'neutral') { signal = 'buy'; confidence = 60; }
            reasons.push('MACD bullish crossover');
        } else if (lastMACD < lastSignal && lastMACD < 0) {
            if (signal === 'sell') confidence += 10;
            else if (signal === 'neutral') { signal = 'sell'; confidence = 60; }
            reasons.push('MACD bearish crossover');
        }

        // Bollinger Bands signals
        if (currentPrice < bbLower) {
            if (signal === 'buy') confidence += 10;
            else if (signal === 'neutral') { signal = 'buy'; confidence = 55; }
            reasons.push('Price below lower BB');
        } else if (currentPrice > bbUpper) {
            if (signal === 'sell') confidence += 10;
            else if (signal === 'neutral') { signal = 'sell'; confidence = 55; }
            reasons.push('Price above upper BB');
        }

        // Trend alignment
        if (trend.direction === 'bullish' && signal === 'buy') {
            confidence += 10;
            reasons.push('Bullish trend aligned');
        } else if (trend.direction === 'bearish' && signal === 'sell') {
            confidence += 10;
            reasons.push('Bearish trend aligned');
        }

        return {
            signal,
            confidence: Math.min(confidence, 95),
            trend: trend.direction,
            trendStrength: trend.strength,
            reasons,
            timestamp: Date.now()
        };
    }

    /**
     * Get prediction summary for display
     * @param {Array} data - OHLCV data
     * @returns {Object} - Formatted prediction data
     */
    getPredictionSummary(data) {
        const forecast = this.linearRegressionForecast(data, 24);
        const trend = this.analyzeTrend(data);
        const signal = this.generateSignal(data);
        const volume = this.analyzeVolume(data);
        
        const currentPrice = data[data.length - 1].close;
        const predictedPrice = forecast[23].value;
        const priceChange = ((predictedPrice - currentPrice) / currentPrice * 100).toFixed(2);
        
        return {
            currentPrice,
            predictedPrice: predictedPrice.toFixed(2),
            priceChange,
            confidence: forecast[23].confidence,
            trend: trend.direction,
            trendStrength: trend.strength.toFixed(1),
            signal: signal.signal,
            signalConfidence: signal.confidence,
            volumeStatus: volume.trend,
            isVolumeSpike: volume.isSpike,
            support: trend.support.toFixed(2),
            resistance: trend.resistance.toFixed(2),
            forecast: forecast.map(f => ({
                time: f.time,
                price: f.value.toFixed(2),
                confidence: f.confidence
            }))
        };
    }
}

// Export for use in browser or Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PredictionEngine;
} else {
    window.PredictionEngine = PredictionEngine;
}
