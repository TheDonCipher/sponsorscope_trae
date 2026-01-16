export type DataCompleteness = 
  | 'full' 
  | 'partial_no_comments' 
  | 'partial_no_images' 
  | 'text_only' 
  | 'archival' 
  | 'unavailable' 
  | 'failed';

export interface Evidence {
  evidence_id: string;
  type: 'post' | 'comment' | 'statistic';
  source_url: string;
  screenshot_path?: string;
  excerpt: string;
  timestamp: string;
}

export interface PillarScore {
  score: number;
  grade?: string; // A-F
  confidence: number; // 0.0 - 1.0
  flags: string[];
  evidence_links: string[];
}

export interface Report {
  id: string;
  handle: string;
  platform: string;
  generated_at: string;
  methodology_version: string;
  data_completeness: DataCompleteness;
  
  true_engagement: PillarScore;
  audience_authenticity: PillarScore;
  brand_safety: PillarScore;
  
  evidence_vault: Evidence[];
  warning_banners: string[];
}
