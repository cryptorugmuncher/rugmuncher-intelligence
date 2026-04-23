export interface UserProfile {
  id?: string;
  user_id?: string;
  display_name?: string;
  bio?: string;
  avatar_url?: string;
  website?: string;
  twitter_handle?: string;
  telegram_username?: string;
  role: string;
  badges: any[];
  onboarding_completed: boolean;
  interests: string[];
  chains: string[];
  created_at?: string;
  updated_at?: string;
}

export interface UserScan {
  id: string;
  contract_address: string;
  chain: string;
  risk_score: number;
  result_json: any;
  created_at: string;
}

export interface UserBadge {
  id: string;
  badge_type: string;
  awarded_at: string;
  metadata: any;
}
