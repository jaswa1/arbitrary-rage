/**
 * TypeScript type definitions for API responses and requests.
 */

export interface Product {
  id: string;
  name: string;
  set_name?: string;
  product_type: 'sealed' | 'single';
  category: 'mtg' | 'pokemon' | 'yugioh' | 'lego' | 'sports';
  tcg_product_id?: string;
  ebay_product_id?: string;
  amazon_asin?: string;
  description?: string;
  image_url?: string;
  is_active: boolean;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductWithPricing extends Product {
  current_price?: number;
  last_price_update?: string;
  seller_count?: number;
  price_trend?: 'up' | 'down' | 'stable';
}

export interface ArbitrageOpportunity {
  id: string;
  sealed_product_id: string;
  sealed_price: number;
  singles_value: number;
  margin_percentage: number;
  confidence_score: number;
  risk_level: 'low' | 'medium' | 'high';
  seller_count?: number;
  competition_level?: 'low' | 'medium' | 'high' | 'unknown';
  status: 'active' | 'expired' | 'executed' | 'cancelled';
  execution_quantity: number;
  execution_notes?: string;
  created_at: string;
  updated_at: string;
  expires_at?: string;
  executed_at?: string;
  potential_profit?: number;
  is_active: boolean;
  is_high_confidence: boolean;
}

export interface ArbitrageOpportunityWithProduct extends ArbitrageOpportunity {
  sealed_product: Product;
}

export interface PriceHistory {
  id: string;
  product_id: string;
  price: number;
  condition: string;
  source: string;
  source_url?: string;
  seller_count?: number;
  available_quantity?: number;
  shipping_cost?: number;
  price_type: string;
  is_foil: boolean;
  confidence_level: string;
  data_source_quality: number;
  recorded_at: string;
  created_at: string;
}

export interface OpportunityFilters {
  min_margin?: number;
  max_margin?: number;
  min_confidence?: number;
  max_risk?: 'low' | 'medium' | 'high';
  status?: 'active' | 'expired' | 'executed' | 'cancelled' | 'all';
  category?: string;
  created_after?: string;
  created_before?: string;
  expires_after?: string;
  expires_before?: string;
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface OpportunityStats {
  total_opportunities: number;
  active_opportunities: number;
  executed_opportunities: number;
  expired_opportunities: number;
  average_margin: number;
  average_confidence: number;
  total_potential_profit: number;
  high_confidence_count: number;
  low_risk_count: number;
}

export interface OpportunityExecution {
  quantity: number;
  notes?: string;
}

// API Response wrappers
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Error types
export interface ApiError {
  detail: string;
  status_code: number;
  type?: string;
}

// Filter and search types
export interface ProductSearch {
  query?: string;
  category?: string;
  product_type?: 'sealed' | 'single';
  is_active?: boolean;
  is_featured?: boolean;
  skip?: number;
  limit?: number;
}

// Chart data types for dashboard
export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface MarginDistribution {
  range: string;
  count: number;
  percentage: number;
}

export interface CategoryStats {
  category: string;
  opportunities: number;
  average_margin: number;
  total_profit: number;
}