export interface ResumeUploadResponse {
  id: number;
  original_filename: string;
  stored_filename: string;
  uploaded_at: string;
  message: string;
}

export interface ResumeParseResponse {
  id: number;
  original_filename: string;
  parsing_status: string;
  extracted_characters: number;
  parsing_error: string | null;
  parsed_at: string | null;
  message: string;
}

export interface ResumeContact {
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
}

export interface ResumeStatistics {
  character_count: number;
  word_count: number;
  section_count: number;
}

export interface ResumeStructuredResponse {
  id: number;
  original_filename: string;
  contact: ResumeContact;
  skills: Record<string, string[]>;
  certifications: string[];
  detected_sections: string[];
  statistics: ResumeStatistics;
}

export interface ResumeScoreBreakdown {
  contact_information: number;
  essential_sections: number;
  technical_skills: number;
  professional_experience: number;
  education: number;
  certifications_projects: number;
  content_quality: number;
}

export interface ResumeScoreResponse {
  id: number;
  original_filename: string;
  score: number;
  max_score: number;
  grade: string;
  breakdown: ResumeScoreBreakdown;
  strengths: string[];
  improvements: string[];
}

export interface KeywordCoverage {
  matched: number;
  required: number;
}

export interface ResumeJobMatchResponse {
  id: number;
  original_filename: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  resume_skills: string[];
  job_description_skills: string[];
  keyword_coverage: KeywordCoverage;
}

export interface ResumeFeedbackResponse {
  id: number;
  original_filename: string;
  summary: string;
  resume_score: number;
  resume_grade: string;
  job_match_score: number | null;
  priority_improvements: string[];
  matched_strengths: string[];
  resume_strengths: string[];
  resume_improvements: string[];
}
