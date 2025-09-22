import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  ArrowUpIcon, 
  ArrowTrendingDownIcon 
} from '@heroicons/react/24/outline';
import { portfolioApi, tradingApi } from '../lib/services';
import { Portfolio, Trade } from '../types';

export default function Dashboard() {
  const { data: portfolios, isLoading: portfoliosLoading } = useQuery('portfolios', portfolioApi.getPortfolios);
  const { data: trades, isLoading: tradesLoading } = useQuery('trades', tradingApi.getTrades);

  const mainPortfolio = portfolios?.[0];

  const recentTrades = trades?.slice(0, 5) || [];
  const totalGainLoss = mainPortfolio ? mainPortfolio.total_value - 100000 : 0; // Assuming starting balance of $100,000
  const gainLossPercent = mainPortfolio ? ((totalGainLoss / 100000) * 100) : 0;

  if (portfoliosLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-600">
          Overview of your trading performance and portfolio
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CurrencyDollarIcon className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Portfolio Value
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  ${mainPortfolio?.total_value?.toLocaleString() || '0'}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Cash Balance
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  ${mainPortfolio?.cash_balance?.toLocaleString() || '0'}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {totalGainLoss >= 0 ? (
                <ArrowUpIcon className="h-8 w-8 text-success-600" />
              ) : (
                <ArrowTrendingDownIcon className="h-8 w-8 text-danger-600" />
              )}
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total Gain/Loss
                </dt>
                <dd className={`text-lg font-medium ${totalGainLoss >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
                  ${totalGainLoss.toLocaleString()} ({gainLossPercent.toFixed(2)}%)
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total Trades
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {trades?.length || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Trades */}
      <div className="card">
        <div className="px-4 py-5 sm:p-0">
          <div className="sm:px-6 sm:py-4 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Recent Trades
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Your latest trading activity
            </p>
          </div>
          
          {recentTrades.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No trades yet. Start trading to see your activity here.</p>
            </div>
          ) : (
            <div className="overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Symbol
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentTrades.map((trade: Trade) => (
                    <tr key={trade.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {trade.symbol}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          trade.order_type === 'BUY' 
                            ? 'bg-success-100 text-success-800' 
                            : 'bg-danger-100 text-danger-800'
                        }`}>
                          {trade.order_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {trade.quantity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${trade.price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${trade.total_amount.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          trade.status === 'EXECUTED' 
                            ? 'bg-success-100 text-success-800' 
                            : trade.status === 'PENDING'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {trade.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}