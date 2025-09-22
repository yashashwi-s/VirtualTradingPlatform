import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ChartProps {
  symbol: string;
  data: any[];
  height?: number;
  width?: number;
}

const TradingViewChart: React.FC<ChartProps> = ({ 
  symbol, 
  data = [], 
  height = 400
}) => {
  // Transform data for recharts
  const chartData = data.map((item: any) => ({
    time: new Date(item.timestamp || item.time).toLocaleTimeString(),
    price: parseFloat(item.close_price || item.close || item.value || 0),
    volume: parseInt(item.volume || '0'),
  })).slice(-50); // Show last 50 data points

  return (
    <div className="w-full">
      <div className="mb-2 px-2">
        <h3 className="text-lg font-semibold text-gray-900">{symbol} Price Chart</h3>
      </div>
      <div 
        className="border border-gray-200 rounded-lg p-4"
        style={{ height: `${height}px` }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="time" 
              stroke="#666"
              fontSize={12}
              tickLine={false}
            />
            <YAxis 
              stroke="#666"
              fontSize={12}
              tickLine={false}
              domain={['dataMin - 1', 'dataMax + 1']}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #ccc',
                borderRadius: '4px',
              }}
              formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
            />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#2563eb" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#2563eb' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TradingViewChart;