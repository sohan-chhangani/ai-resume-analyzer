import type {
  ResumeFeedbackResponse,
  ResumeJobMatchResponse,
  ResumeParseResponse,
  ResumeScoreResponse,
  ResumeStructuredResponse,
  ResumeUploadResponse,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, options);

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const data = await response.json();

      if (typeof data.detail === "string") {
        message = data.detail;
      }
    } catch {
      // Preserve the fallback message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function uploadResume(
  file: File,
): Promise<ResumeUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return request<ResumeUploadResponse>("/upload/", {
    method: "POST",
    body: formData,
  });
}

export async function parseResume(
  resumeId: number,
): Promise<ResumeParseResponse> {
  return request<ResumeParseResponse>(
    `/resumes/${resumeId}/parse`,
    {
      method: "POST",
    },
  );
}

export async function getStructuredResume(
  resumeId: number,
): Promise<ResumeStructuredResponse> {
  return request<ResumeStructuredResponse>(
    `/resumes/${resumeId}/structured`,
  );
}

export async function getResumeScore(
  resumeId: number,
): Promise<ResumeScoreResponse> {
  return request<ResumeScoreResponse>(
    `/resumes/${resumeId}/score`,
  );
}

export async function matchResume(
  resumeId: number,
  jobDescription: string,
): Promise<ResumeJobMatchResponse> {
  return request<ResumeJobMatchResponse>(
    `/resumes/${resumeId}/match`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_description: jobDescription,
      }),
    },
  );
}

export async function getResumeFeedback(
  resumeId: number,
  jobDescription?: string,
): Promise<ResumeFeedbackResponse> {
  return request<ResumeFeedbackResponse>(
    `/resumes/${resumeId}/feedback`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_description: jobDescription || null,
      }),
    },
  );
}
