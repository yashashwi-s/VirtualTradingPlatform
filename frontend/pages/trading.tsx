import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import {
  MagnifyingGlassIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline';
import { portfolioApi, tradingApi, marketApi } from '../lib/services';
import { TradeForm, Quote } from '../types';

export default function Trading() {
  const [searchSymbol, setSearchSymbol] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [currentQuote, setCurrentQuote] = useState<Quote | null>(null);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  
  const queryClient = useQueryClient();

  const { data: portfolios } = useQuery('portfolios', portfolioApi.getPortfolios);
  const { data: trades } = useQuery('trades', tradingApi.getTrades);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch
  } = useForm<TradeForm>();

  const watchOrderType = watch('order_type');
  const watchQuantity = watch('quantity');
  const watchPrice = watch('price');

  const placeTradeM = useMutation(tradingApi.placeTrade, {
    onSuccess: () => {
      queryClient.invalidateQueries('trades');
      queryClient.invalidateQueries('portfolios');
      queryClient.invalidateQueries('positions');
      reset();
      setCurrentQuote(null);
      setSelectedSymbol('');
    },
  });

  const searchStocks = async () => {
    if (searchSymbol.length < 1) return;
    
    try {
      const results = await marketApi.searchStocks(searchSymbol);
      setSearchResults(results || []);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const selectSymbol = async (symbol: string) => {
    setSelectedSymbol(symbol);
    setValue('symbol', symbol);
    setSearchSymbol('');
    setSearchResults([]);
    
    try {
      const quote = await marketApi.getQuote(symbol);
      setCurrentQuote(quote);
      setValue('price', quote.price);
    } catch (error) {
      console.error('Failed to get quote:', error);
    }
  };

  const refreshQuote = async () => {
    if (!selectedSymbol) return;
    
    try {
      const quote = await marketApi.getQuote(selectedSymbol);
      setCurrentQuote(quote);
      setValue('price', quote.price);
    } catch (error) {
      console.error('Failed to refresh quote:', error);
    }
  };

  const onSubmit = async (data: TradeForm) => {
    if (!portfolios || portfolios.length === 0) {
      alert('No portfolio available');
      return;
    }

    try {
      await placeTradeM.mutateAsync({
        ...data,
        portfolio_id: portfolios[0].id // Use main portfolio
      });
      alert('Trade placed successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Trade failed');
    }
  };

  const estimatedTotal = watchQuantity && watchPrice ? watchQuantity * watchPrice : 0;

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Trading</h1>
        <p className="mt-1 text-sm text-gray-600">
          Buy and sell stocks in your virtual portfolio
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Trading Panel */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Place Order</h2>
          
          {/* Symbol Search */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Symbol
            </label>
            <div className="relative">
              <input
                type="text"
                value={searchSymbol}
                onChange={(e) => setSearchSymbol(e.target.value)}
                className="input-field pr-10"
                placeholder="Enter stock symbol (e.g., AAPL)"
                onKeyPress={(e) => e.key === 'Enter' && searchStocks()}
              />
              <button
                onClick={searchStocks}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </button>
            </div>
            
            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="mt-2 bg-white border border-gray-300 rounded-md shadow-sm max-h-60 overflow-y-auto">
                {searchResults.map((stock, index) => (
                  <div
                    key={index}
                    onClick={() => selectSymbol(stock.symbol)}
                    className="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-200 last:border-b-0"
                  >
                    <div className="font-medium text-gray-900">{stock.symbol}</div>
                    <div className="text-sm text-gray-500">{stock.name}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Current Quote */}
          {currentQuote && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {currentQuote.symbol}
                  </h3>
                  <div className="flex items-center mt-1">
                    <span className="text-2xl font-bold text-gray-900">
                      ${currentQuote.price.toFixed(2)}
                    </span>
                    <div className={`ml-2 flex items-center ${
                      parseFloat(currentQuote.change_percent) >= 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {parseFloat(currentQuote.change_percent) >= 0 ? (
                        <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                      ) : (
                        <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                      )}
                      <span className="text-sm font-medium">
                        {currentQuote.change_percent}%
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={refreshQuote}
                  className="btn-secondary text-sm"
                >
                  Refresh
                </button>
              </div>
            </div>
          )}

          {/* Trading Form */}
          {selectedSymbol && (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <input
                type="hidden"
                {...register('symbol', { required: true })}
              />
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Order Type
                  </label>
                  <select
                    {...register('order_type', { required: 'Order type is required' })}
                    className="input-field"
                  >
                    <option value="">Select type</option>
                    <option value="BUY">Buy</option>
                    <option value="SELL">Sell</option>
                  </select>
                  {errors.order_type && (
                    <p className="mt-1 text-sm text-red-600">{errors.order_type.message}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Quantity
                  </label>
                  <input
                    type="number"
                    {...register('quantity', { 
                      required: 'Quantity is required',
                      min: { value: 1, message: 'Minimum quantity is 1' }
                    })}
                    className="input-field"
                    placeholder="Number of shares"
                  />
                  {errors.quantity && (
                    <p className="mt-1 text-sm text-red-600">{errors.quantity.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Price per Share
                </label>
                <input
                  type="number"
                  step="0.01"
                  {...register('price', { 
                    required: 'Price is required',
                    min: { value: 0.01, message: 'Price must be greater than 0' }
                  })}
                  className="input-field"
                  placeholder="0.00"
                />
                {errors.price && (
                  <p className="mt-1 text-sm text-red-600">{errors.price.message}</p>
                )}
              </div>

              {/* Order Summary */}
              {estimatedTotal > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">
                      Estimated Total:
                    </span>
                    <span className="text-lg font-bold text-gray-900">
                      ${estimatedTotal.toFixed(2)}
                    </span>
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={placeTradeM.isLoading}
                className={`w-full py-2 px-4 rounded-lg font-medium transition-colors duration-200 ${
                  watchOrderType === 'BUY' 
                    ? 'btn-success' 
                    : watchOrderType === 'SELL'
                    ? 'btn-danger'
                    : 'btn-primary'
                }`}
              >
                {placeTradeM.isLoading 
                  ? 'Placing Order...' 
                  : watchOrderType 
                    ? `${watchOrderType} ${selectedSymbol}` 
                    : 'Place Order'
                }
              </button>
            </form>
          )}
        </div>

        {/* Recent Trades */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Trades</h2>
          
          {!trades || trades.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No trades yet. Place your first order to get started!</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {trades.slice(0, 10).map((trade) => (
                <div key={trade.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full mr-3 ${
                      trade.order_type === 'BUY' 
                        ? 'bg-success-100 text-success-800' 
                        : 'bg-danger-100 text-danger-800'
                    }`}>
                      {trade.order_type}
                    </span>
                    <div>
                      <div className="font-medium text-gray-900">
                        {trade.symbol} × {trade.quantity}
                      </div>
                      <div className="text-sm text-gray-500">
                        ${trade.price.toFixed(2)} per share
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium text-gray-900">
                      ${trade.total_amount.toFixed(2)}
                    </div>
                    <div className={`text-sm ${
                      trade.status === 'EXECUTED' 
                        ? 'text-success-600' 
                        : trade.status === 'PENDING'
                        ? 'text-yellow-600'
                        : 'text-gray-500'
                    }`}>
                      {trade.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}