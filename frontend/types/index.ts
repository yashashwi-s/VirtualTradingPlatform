// API Types
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  created_at: string;
}

export interface Portfolio {
  id: number;
  user_id: number;
  name: string;
  cash_balance: number;
  total_value: number;
  created_at: string;
  updated_at?: string;
}

export interface Position {
  id: number;
  portfolio_id: number;
  symbol: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
}

export interface Trade {
  id: number;
  user_id: number;
  portfolio_id: number;
  symbol: string;
  order_type: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  total_amount: number;
  status: 'PENDING' | 'EXECUTED' | 'CANCELLED';
  executed_at?: string;
  created_at: string;
}

export interface Quote {
  symbol: string;
  price: number;
  change: number;
  change_percent: string;
  timestamp: string;
}

export interface MarketData {
  symbol: string;
  interval: string;
  data: {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }[];
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
}

export interface TradeForm {
  portfolio_id: number;
  symbol: string;
  order_type: 'BUY' | 'SELL';
  quantity: number;
  price: number;
}

// Response Types
export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail: string;
}