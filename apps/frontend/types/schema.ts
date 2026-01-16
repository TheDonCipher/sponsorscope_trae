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

export type EpistemicStatus = 'ROBUST' | 'PARTIAL' | 'FRAGILE';

export interface EpistemicState {
  status: EpistemicStatus;
  reason: string;
  data_points_analyzed: number;
}

export interface PillarScore {
  signal_strength: number; // Formerly score. 0-100 credibility index.
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
  epistemic_state: EpistemicState;
  
  true_engagement: PillarScore;
  audience_authenticity: PillarScore;
  brand_safety: PillarScore;
  
  evidence_vault: Evidence[];
  warning_banners: string[];
  known_limitations: string[];
}
