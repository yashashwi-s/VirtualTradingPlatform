import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import {
  PlusIcon,
  PlayIcon,
  PauseIcon,
  StopIcon,
  ChartBarIcon,
  CogIcon
} from '@heroicons/react/24/outline';

interface Strategy {
  id: number;
  name: string;
  description: string;
  strategy_type: string;
  status: string;
  capital_allocation: number;
  total_trades: number;
  winning_trades: number;
  total_return: number;
  created_at: string;
}

interface StrategyForm {
  name: string;
  description: string;
  strategy_type: string;
  portfolio_id: number;
  capital_allocation: number;
  max_position_size: number;
  webhook_url?: string;
}

const strategyApi = {
  getStrategies: (): Promise<Strategy[]> =>
    fetch('/api/v1/strategies').then(res => res.json()),
  
  createStrategy: (data: StrategyForm): Promise<Strategy> =>
    fetch('/api/v1/strategies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(res => res.json()),
  
  activateStrategy: (id: number): Promise<any> =>
    fetch(`/api/v1/strategies/${id}/activate`, { method: 'POST' }).then(res => res.json()),
  
  pauseStrategy: (id: number): Promise<any> =>
    fetch(`/api/v1/strategies/${id}/pause`, { method: 'POST' }).then(res => res.json()),
  
  stopStrategy: (id: number): Promise<any> =>
    fetch(`/api/v1/strategies/${id}/stop`, { method: 'POST' }).then(res => res.json()),
  
  getPerformance: (id: number): Promise<any> =>
    fetch(`/api/v1/strategies/${id}/performance`).then(res => res.json())
};

export default function Strategies() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  
  const queryClient = useQueryClient();
  
  const { data: strategies, isLoading } = useQuery('strategies', strategyApi.getStrategies);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<StrategyForm>();

  const createStrategyMutation = useMutation(strategyApi.createStrategy, {
    onSuccess: () => {
      queryClient.invalidateQueries('strategies');
      setShowCreateForm(false);
      reset();
    }
  });

  const activateMutation = useMutation(strategyApi.activateStrategy, {
    onSuccess: () => queryClient.invalidateQueries('strategies')
  });

  const pauseMutation = useMutation(strategyApi.pauseStrategy, {
    onSuccess: () => queryClient.invalidateQueries('strategies')
  });

  const stopMutation = useMutation(strategyApi.stopStrategy, {
    onSuccess: () => queryClient.invalidateQueries('strategies')
  });

  const onSubmit = (data: StrategyForm) => {
    createStrategyMutation.mutate({
      ...data,
      portfolio_id: 1, // Use default portfolio for now
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'paused': return 'text-yellow-600 bg-yellow-100';
      case 'stopped': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Trading Strategies</h1>
          <p className="mt-1 text-sm text-gray-600">
            Create and manage automated trading strategies
          </p>
        </div>
        
        <button 
          onClick={() => setShowCreateForm(true)}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Strategy
        </button>
      </div>

      {/* Create Strategy Form */}
      {showCreateForm && (
        <div className="card mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Create New Strategy</h2>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Strategy Name
                </label>
                <input
                  type="text"
                  {...register('name', { required: 'Name is required' })}
                  className="input-field"
                  placeholder="My Trading Strategy"
                />
                {errors.name && <p className="text-red-600 text-sm mt-1">{errors.name.message}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Strategy Type
                </label>
                <select
                  {...register('strategy_type', { required: 'Type is required' })}
                  className="input-field"
                >
                  <option value="">Select type</option>
                  <option value="MANUAL">Manual</option>
                  <option value="ALGORITHMIC">Algorithmic</option>
                  <option value="WEBHOOK">Webhook</option>
                </select>
                {errors.strategy_type && <p className="text-red-600 text-sm mt-1">{errors.strategy_type.message}</p>}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                {...register('description')}
                className="input-field"
                rows={3}
                placeholder="Describe your trading strategy..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Capital Allocation ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  {...register('capital_allocation', { required: 'Capital allocation is required', min: 1 })}
                  className="input-field"
                  placeholder="10000"
                />
                {errors.capital_allocation && <p className="text-red-600 text-sm mt-1">{errors.capital_allocation.message}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Position Size (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  max="1"
                  {...register('max_position_size', { required: 'Max position size is required' })}
                  className="input-field"
                  placeholder="0.1"
                />
                {errors.max_position_size && <p className="text-red-600 text-sm mt-1">{errors.max_position_size.message}</p>}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Webhook URL (Optional)
              </label>
              <input
                type="url"
                {...register('webhook_url')}
                className="input-field"
                placeholder="https://your-strategy-service.com/webhook"
              />
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={createStrategyMutation.isLoading}
                className="btn-primary"
              >
                {createStrategyMutation.isLoading ? 'Creating...' : 'Create Strategy'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Strategies List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {strategies?.map((strategy) => (
          <div key={strategy.id} className="card">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-medium text-gray-900">{strategy.name}</h3>
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(strategy.status)}`}>
                {strategy.status}
              </span>
            </div>
            
            <p className="text-sm text-gray-600 mb-4">{strategy.description}</p>
            
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Capital:</span>
                <span className="font-medium">${strategy.capital_allocation.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Total Trades:</span>
                <span className="font-medium">{strategy.total_trades}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Win Rate:</span>
                <span className="font-medium">
                  {strategy.total_trades > 0 
                    ? `${((strategy.winning_trades / strategy.total_trades) * 100).toFixed(1)}%`
                    : '0%'
                  }
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Total Return:</span>
                <span className={`font-medium ${strategy.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ${strategy.total_return.toFixed(2)}
                </span>
              </div>
            </div>
            
            <div className="flex space-x-2">
              {strategy.status === 'DRAFT' || strategy.status === 'STOPPED' ? (
                <button
                  onClick={() => activateMutation.mutate(strategy.id)}
                  className="flex-1 btn-success text-sm flex items-center justify-center"
                  disabled={activateMutation.isLoading}
                >
                  <PlayIcon className="h-4 w-4 mr-1" />
                  Activate
                </button>
              ) : strategy.status === 'ACTIVE' ? (
                <button
                  onClick={() => pauseMutation.mutate(strategy.id)}
                  className="flex-1 btn-warning text-sm flex items-center justify-center"
                  disabled={pauseMutation.isLoading}
                >
                  <PauseIcon className="h-4 w-4 mr-1" />
                  Pause
                </button>
              ) : (
                <button
                  onClick={() => activateMutation.mutate(strategy.id)}
                  className="flex-1 btn-success text-sm flex items-center justify-center"
                  disabled={activateMutation.isLoading}
                >
                  <PlayIcon className="h-4 w-4 mr-1" />
                  Resume
                </button>
              )}
              
              {strategy.status !== 'STOPPED' && (
                <button
                  onClick={() => stopMutation.mutate(strategy.id)}
                  className="flex-1 btn-danger text-sm flex items-center justify-center"
                  disabled={stopMutation.isLoading}
                >
                  <StopIcon className="h-4 w-4 mr-1" />
                  Stop
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Empty state */}
      {!strategies || strategies.length === 0 ? (
        <div className="text-center py-12">
          <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No strategies yet</h3>
          <p className="text-gray-600 mb-4">Create your first automated trading strategy to get started.</p>
          <button 
            onClick={() => setShowCreateForm(true)}
            className="btn-primary"
          >
            Create Strategy
          </button>
        </div>
      ) : null}
    </div>
  );
}