import { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  ChartBarIcon,
  ArrowUpIcon,
  ArrowTrendingDownIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { portfolioApi } from '../lib/services';

export default function Portfolio() {
  const { data: portfolios, isLoading } = useQuery('portfolios', portfolioApi.getPortfolios);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);
  
  const { data: positions } = useQuery(
    ['positions', selectedPortfolioId],
    () => selectedPortfolioId ? portfolioApi.getPositions(selectedPortfolioId) : null,
    { enabled: !!selectedPortfolioId }
  );

  const { data: summary } = useQuery(
    ['portfolio-summary', selectedPortfolioId],
    () => selectedPortfolioId ? portfolioApi.getSummary(selectedPortfolioId) : null,
    { enabled: !!selectedPortfolioId }
  );

  const mainPortfolio = portfolios?.[0];

  // Set default selected portfolio
  useState(() => {
    if (mainPortfolio && !selectedPortfolioId) {
      setSelectedPortfolioId(mainPortfolio.id);
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading portfolio...</div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Portfolio</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your investments and track performance
          </p>
        </div>
        
        <button className="btn-primary flex items-center">
          <PlusIcon className="h-5 w-5 mr-2" />
          New Portfolio
        </button>
      </div>

      {/* Portfolio Summary */}
      {mainPortfolio && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Value
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${mainPortfolio.total_value.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-success-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Cash Balance
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${mainPortfolio.cash_balance.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                {(summary?.performance?.total_gain_loss || 0) >= 0 ? (
                  <ArrowUpIcon className="h-8 w-8 text-success-600" />
                ) : (
                  <ArrowTrendingDownIcon className="h-8 w-8 text-danger-600" />
                )}
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Unrealized P&L
                  </dt>
                  <dd className={`text-lg font-medium ${
                    (summary?.performance?.total_gain_loss || 0) >= 0 ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    ${(summary?.performance?.total_gain_loss || 0).toLocaleString()}
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
                    Day Change
                  </dt>
                  <dd className={`text-lg font-medium ${
                    (summary?.performance?.total_gain_loss_percent || 0) >= 0 ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {(summary?.performance?.total_gain_loss_percent || 0).toFixed(2)}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Positions Table */}
      <div className="card">
        <div className="px-4 py-5 sm:p-0">
          <div className="sm:px-6 sm:py-4 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Positions
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Your current stock positions
            </p>
          </div>
          
          {!positions || positions.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No positions yet. Start trading to build your portfolio.</p>
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
                      Quantity
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg Cost
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Current Price
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Market Value
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Unrealized P&L
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {positions?.map((position) => (
                    <tr key={position.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {position.symbol}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {position.quantity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${position.average_cost.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${position.current_price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${position.market_value.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={position.unrealized_pnl >= 0 ? 'text-success-600' : 'text-danger-600'}>
                          ${position.unrealized_pnl.toFixed(2)}
                          {' '}
                          ({((position.unrealized_pnl / (position.average_cost * position.quantity)) * 100).toFixed(2)}%)
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