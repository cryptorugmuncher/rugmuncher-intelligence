/**
 * MunchScan Data Feed Utilities
 * Mock data generators and WebSocket simulators for testing
 */

class DataFeed {
    constructor() {
        this.subscribers = [];
        this.isRunning = false;
    }

    /**
     * Generate OHLCV candlestick data
     * @param {number} count - Number of candles
     * @param {number} startPrice - Starting price
     * @param {string} timeframe - Time interval (1m, 5m, 15m, 1h, 4h, 1d)
     * @returns {Array} - Array of OHLCV objects
     */
    generateCandles(count = 100, startPrice = 65000, timeframe = '1h') {
        const data = [];
        let price = startPrice;
        const now = Math.floor(Date.now() / 1000);
        
        // Time multiplier based on timeframe
        const timeMultipliers = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400,
            '1w': 604800
        };
        const timeStep = timeMultipliers[timeframe] || 3600;
        
        for (let i = count; i > 0; i--) {
            const time = now - (i * timeStep);
            const volatility = price * 0.02; // 2% volatility
            const trend = Math.sin(i / 10) * volatility * 0.3; // Add trend cycles
            
            const open = price;
            const close = price + (Math.random() - 0.5) * volatility + trend;
            const high = Math.max(open, close) + Math.random() * volatility * 0.5;
            const low = Math.min(open, close) - Math.random() * volatility * 0.5;
            const volume = Math.floor(Math.random() * 1000000 + 500000);
            
            data.push({
                time: time,
                open: parseFloat(open.toFixed(2)),
                high: parseFloat(high.toFixed(2)),
                low: parseFloat(low.toFixed(2)),
                close: parseFloat(close.toFixed(2)),
                volume: volume
            });
            
            price = close;
        }
        
        return data;
    }

    /**
     * Generate order book data
     * @param {number} currentPrice - Current market price
     * @param {number} levels - Number of price levels
     * @returns {Object} - Bids and asks
     */
    generateOrderBook(currentPrice = 67420, levels = 20) {
        const bids = [];
        const asks = [];
        
        let bidPrice = currentPrice - 0.5;
        let askPrice = currentPrice + 0.5;
        let bidVolume = Math.random() * 2 + 0.5;
        let askVolume = Math.random() * 2 + 0.5;
        
        for (let i = 0; i < levels; i++) {
            bids.push({
                price: parseFloat(bidPrice.toFixed(2)),
                volume: parseFloat(bidVolume.toFixed(4)),
                total: parseFloat((bidVolume * bidPrice).toFixed(2))
            });
            
            asks.push({
                price: parseFloat(askPrice.toFixed(2)),
                volume: parseFloat(askVolume.toFixed(4)),
                total: parseFloat((askVolume * askPrice).toFixed(2))
            });
            
            // Prices get further apart as you go down the book
            bidPrice -= Math.random() * 2 + 0.5;
            askPrice += Math.random() * 2 + 0.5;
            
            // Volumes increase deeper in the book
            bidVolume += Math.random() * 1.5 + 0.5;
            askVolume += Math.random() * 1.5 + 0.5;
        }
        
        return { bids, asks };
    }

    /**
     * Generate recent trades
     * @param {number} count - Number of trades
     * @param {number} currentPrice - Base price
     * @returns {Array} - Array of trade objects
     */
    generateTrades(count = 50, currentPrice = 67420) {
        const trades = [];
        const now = Date.now();
        
        for (let i = 0; i < count; i++) {
            const isBuy = Math.random() > 0.45; // Slightly more buys
            const price = currentPrice + (Math.random() - 0.5) * 10;
            const volume = Math.random() * 0.5 + 0.01;
            
            trades.push({
                id: `trade_${now}_${i}`,
                time: now - (i * 1000),
                price: parseFloat(price.toFixed(2)),
                volume: parseFloat(volume.toFixed(4)),
                side: isBuy ? 'buy' : 'sell',
                total: parseFloat((price * volume).toFixed(2))
            });
        }
        
        return trades;
    }

    /**
     * Generate token metadata
     * @returns {Object} - Token info
     */
    generateTokenInfo() {
        const tokens = [
            { symbol: 'BTC', name: 'Bitcoin', price: 67420, change24h: 2.34 },
            { symbol: 'ETH', name: 'Ethereum', price: 3520, change24h: 1.87 },
            { symbol: 'SOL', name: 'Solana', price: 148, change24h: 5.21 },
            { symbol: 'DOGE', name: 'Dogecoin', price: 0.16, change24h: -1.23 },
            { symbol: 'ADA', name: 'Cardano', price: 0.58, change24h: 0.89 },
            { symbol: 'AVAX', name: 'Avalanche', price: 38.5, change24h: 3.45 },
            { symbol: 'LINK', name: 'Chainlink', price: 18.2, change24h: -0.56 },
            { symbol: 'DOT', name: 'Polkadot', price: 7.8, change24h: 1.12 }
        ];
        
        return tokens.map(token => ({
            ...token,
            marketCap: (token.price * Math.random() * 1000000).toFixed(0),
            volume24h: (Math.random() * 1000000000).toFixed(0),
            high24h: (token.price * 1.05).toFixed(2),
            low24h: (token.price * 0.95).toFixed(2)
        }));
    }

    /**
     * Simulate real-time WebSocket feed
     * @param {Function} callback - Function to call with new data
     * @param {number} interval - Update interval in ms
     */
    subscribe(callback, interval = 1000) {
        this.subscribers.push(callback);
        
        if (!this.isRunning) {
            this.isRunning = true;
            this.startSimulation(interval);
        }
        
        // Return unsubscribe function
        return () => {
            const index = this.subscribers.indexOf(callback);
            if (index > -1) {
                this.subscribers.splice(index, 1);
            }
            
            if (this.subscribers.length === 0) {
                this.stopSimulation();
            }
        };
    }

    startSimulation(interval) {
        let lastPrice = 67420;
        
        this.simulationInterval = setInterval(() => {
            // Generate slight price movement
            const change = (Math.random() - 0.5) * 50;
            lastPrice += change;
            
            const data = {
                type: 'tick',
                price: parseFloat(lastPrice.toFixed(2)),
                change: parseFloat(change.toFixed(2)),
                timestamp: Date.now(),
                volume: Math.random() * 0.5 + 0.01,
                side: Math.random() > 0.5 ? 'buy' : 'sell'
            };
            
            // Notify all subscribers
            this.subscribers.forEach(callback => {
                try {
                    callback(data);
                } catch (err) {
                    console.error('Subscriber error:', err);
                }
            });
        }, interval);
    }

    stopSimulation() {
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
            this.isRunning = false;
        }
    }

    /**
     * Fetch historical data (mock)
     * @param {string} symbol - Trading pair
     * @param {string} timeframe - Time interval
     * @param {number} limit - Number of candles
     * @returns {Promise} - Resolves with candle data
     */
    async fetchHistoricalData(symbol = 'BTC/USD', timeframe = '1h', limit = 100) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const basePrice = symbol.includes('BTC') ? 65000 : 
                         symbol.includes('ETH') ? 3500 : 
                         symbol.includes('SOL') ? 150 : 1;
        
        return this.generateCandles(limit, basePrice, timeframe);
    }

    /**
     * Format price for display
     * @param {number} price - Price value
     * @param {number} decimals - Decimal places
     * @returns {string} - Formatted price
     */
    formatPrice(price, decimals = 2) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(price);
    }

    /**
     * Format large numbers (K, M, B, T)
     * @param {number} num - Number to format
     * @returns {string} - Formatted number
     */
    formatCompactNumber(num) {
        const formatter = Intl.NumberFormat('en', { notation: 'compact' });
        return formatter.format(num);
    }

    /**
     * Calculate price change percentage
     * @param {number} current - Current price
     * @param {number} previous - Previous price
     * @returns {string} - Formatted percentage
     */
    calculateChange(current, previous) {
        const change = ((current - previous) / previous) * 100;
        const sign = change >= 0 ? '+' : '';
        return `${sign}${change.toFixed(2)}%`;
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataFeed;
} else {
    window.DataFeed = DataFeed;
}
