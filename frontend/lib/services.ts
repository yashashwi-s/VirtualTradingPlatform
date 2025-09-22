import api from './api';
import {
  User,
  Portfolio,
  Position,
  Trade,
  Quote,
  MarketData,
  LoginForm,
  RegisterForm,
  TradeForm,
  AuthResponse,
} from '../types';

// Auth API
export const authApi = {
  login: (data: LoginForm): Promise<AuthResponse> =>
    api.post('/auth/login', data).then(res => res.data),
  
  register: (data: RegisterForm): Promise<User> =>
    api.post('/auth/register', data).then(res => res.data),
  
  getProfile: (): Promise<User> =>
    api.get('/auth/me').then(res => res.data),
};

// Portfolio API
export const portfolioApi = {
  getPortfolios: (): Promise<Portfolio[]> =>
    api.get('/portfolios').then(res => res.data),
  
  createPortfolio: (data: { name: string }): Promise<Portfolio> =>
    api.post('/portfolios', data).then(res => res.data),
  
  getPositions: (portfolioId: number): Promise<Position[]> =>
    api.get(`/portfolios/${portfolioId}/positions`).then(res => res.data),
  
  getSummary: (portfolioId: number): Promise<any> =>
    api.get(`/portfolios/${portfolioId}/summary`).then(res => res.data),
};

// Trading API
export const tradingApi = {
  placeTrade: (data: TradeForm): Promise<Trade> =>
    api.post('/trades', data).then(res => res.data),
  
  getTrades: (): Promise<Trade[]> =>
    api.get('/trades').then(res => res.data),
  
  getTrade: (tradeId: number): Promise<Trade> =>
    api.get(`/trades/${tradeId}`).then(res => res.data),
};

// Market API
export const marketApi = {
  getQuote: (symbol: string): Promise<Quote> =>
    api.get(`/market/quote/${symbol}`).then(res => res.data),
  
  getIntradayData: (symbol: string, interval: string = '5min'): Promise<MarketData> =>
    api.get(`/market/intraday/${symbol}`, { params: { interval } }).then(res => res.data),
  
  searchStocks: (keywords: string): Promise<any[]> =>
    api.get('/market/search', { params: { keywords } }).then(res => res.data),
};