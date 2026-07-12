"use client";

import { ChangeEvent, useState } from "react";

import {
  getResumeFeedback,
  getResumeScore,
  getStructuredResume,
  matchResume,
  parseResume,
  uploadResume,
} from "@/lib/api";

import type {
  ResumeFeedbackResponse,
  ResumeJobMatchResponse,
  ResumeScoreResponse,
  ResumeStructuredResponse,
} from "@/lib/types";

type Status =
  | "idle"
  | "uploading"
  | "parsing"
  | "analyzing"
  | "complete"
  | "error";

function formatLabel(value: string): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function ScoreCard({
  score,
  grade,
}: {
  score: number;
  grade: string;
}) {
  return (
    <div className="rounded-3xl border border-slate-700 bg-slate-900 p-8 text-center shadow-xl">
      <p className="text-sm font-semibold uppercase tracking-widest text-cyan-400">
        Resume Score
      </p>

      <div className="mx-auto mt-6 flex h-40 w-40 items-center justify-center rounded-full border-8 border-cyan-400 bg-slate-950">
        <div>
          <p className="text-5xl font-bold text-white">{score}</p>
          <p className="text-sm text-slate-400">out of 100</p>
        </div>
      </div>

      <p className="mt-5 text-2xl font-bold text-white">
        Grade {grade}
      </p>
    </div>
  );
}

function ListCard({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <section className="rounded-3xl border border-slate-700 bg-slate-900 p-6">
      <h3 className="text-xl font-bold text-white">{title}</h3>

      {items.length === 0 ? (
        <p className="mt-4 text-slate-400">No items detected.</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {items.map((item, index) => (
            <li
              key={`${item}-${index}`}
              className="rounded-xl bg-slate-950 px-4 py-3 text-sm leading-6 text-slate-300"
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");

  const [resumeId, setResumeId] = useState<number | null>(null);
  const [structured, setStructured] =
    useState<ResumeStructuredResponse | null>(null);
  const [score, setScore] =
    useState<ResumeScoreResponse | null>(null);
  const [feedback, setFeedback] =
    useState<ResumeFeedbackResponse | null>(null);

  const [jobDescription, setJobDescription] = useState("");
  const [jobMatch, setJobMatch] =
    useState<ResumeJobMatchResponse | null>(null);
  const [matching, setMatching] = useState(false);

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const selectedFile = event.target.files?.[0] ?? null;

    setFile(selectedFile);
    setError("");
  }

  async function analyzeResume() {
    if (!file) {
      setError("Choose a PDF or DOCX resume first.");
      return;
    }

    try {
      setError("");
      setStructured(null);
      setScore(null);
      setFeedback(null);
      setJobMatch(null);

      setStatus("uploading");
      setStatusMessage("Uploading your resume...");

      const upload = await uploadResume(file);
      setResumeId(upload.id);

      setStatus("parsing");
      setStatusMessage("Extracting and processing resume content...");

      await parseResume(upload.id);

      setStatus("analyzing");
      setStatusMessage("Analyzing skills, structure, and resume quality...");

      const [
        structuredResult,
        scoreResult,
        feedbackResult,
      ] = await Promise.all([
        getStructuredResume(upload.id),
        getResumeScore(upload.id),
        getResumeFeedback(upload.id),
      ]);

      setStructured(structuredResult);
      setScore(scoreResult);
      setFeedback(feedbackResult);

      setStatus("complete");
      setStatusMessage("Resume analysis complete.");
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "An unexpected error occurred.";

      setError(message);
      setStatus("error");
      setStatusMessage("");
    }
  }

  async function analyzeJobMatch() {
    if (resumeId === null) {
      setError("Analyze a resume before matching a job description.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Paste a job description first.");
      return;
    }

    try {
      setMatching(true);
      setError("");

      const [matchResult, feedbackResult] = await Promise.all([
        matchResume(resumeId, jobDescription),
        getResumeFeedback(resumeId, jobDescription),
      ]);

      setJobMatch(matchResult);
      setFeedback(feedbackResult);
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "Job matching failed.";

      setError(message);
    } finally {
      setMatching(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="border-b border-slate-800 bg-gradient-to-b from-cyan-950/40 to-slate-950">
        <div className="mx-auto max-w-6xl px-6 py-20 text-center">
          <p className="text-sm font-bold uppercase tracking-[0.3em] text-cyan-400">
            AI Resume Analyzer
          </p>

          <h1 className="mx-auto mt-5 max-w-4xl text-4xl font-black tracking-tight text-white sm:text-6xl">
            Analyze your resume. Measure job fit. Find what to improve.
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-400">
            Upload a PDF or DOCX resume to receive deterministic scoring,
            skill extraction, job-description matching, and actionable
            feedback.
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-6xl space-y-10 px-6 py-12">
        <section className="rounded-3xl border border-slate-700 bg-slate-900 p-6 shadow-2xl sm:p-10">
          <h2 className="text-2xl font-bold text-white">
            Upload your resume
          </h2>

          <p className="mt-2 text-slate-400">
            Supported formats: PDF and DOCX.
          </p>

          <label className="mt-6 block cursor-pointer rounded-2xl border-2 border-dashed border-slate-600 bg-slate-950 p-10 text-center transition hover:border-cyan-400">
            <input
              type="file"
              accept=".pdf,.docx"
              className="hidden"
              onChange={handleFileChange}
            />

            <span className="text-lg font-semibold text-white">
              {file ? file.name : "Choose a resume file"}
            </span>

            <span className="mt-2 block text-sm text-slate-500">
              Click to browse from your device
            </span>
          </label>

          <button
            type="button"
            onClick={analyzeResume}
            disabled={
              !file ||
              status === "uploading" ||
              status === "parsing" ||
              status === "analyzing"
            }
            className="mt-6 w-full rounded-xl bg-cyan-400 px-6 py-4 font-bold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {status === "uploading" ||
            status === "parsing" ||
            status === "analyzing"
              ? "Analyzing..."
              : "Analyze Resume"}
          </button>

          {statusMessage && (
            <p className="mt-4 text-center text-sm text-cyan-300">
              {statusMessage}
            </p>
          )}

          {error && (
            <div className="mt-5 rounded-xl border border-red-900 bg-red-950/40 px-4 py-3 text-red-300">
              {error}
            </div>
          )}
        </section>

        {score && structured && (
          <>
            <section className="grid gap-6 lg:grid-cols-[320px_1fr]">
              <ScoreCard score={score.score} grade={score.grade} />

              <div className="rounded-3xl border border-slate-700 bg-slate-900 p-6">
                <h2 className="text-2xl font-bold text-white">
                  Score breakdown
                </h2>

                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  {Object.entries(score.breakdown).map(
                    ([category, value]) => (
                      <div
                        key={category}
                        className="rounded-xl bg-slate-950 p-4"
                      >
                        <p className="text-sm text-slate-400">
                          {formatLabel(category)}
                        </p>
                        <p className="mt-1 text-2xl font-bold text-cyan-300">
                          {value}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-2">
              <ListCard
                title="Resume strengths"
                items={score.strengths}
              />

              <ListCard
                title="Improvements"
                items={score.improvements}
              />
            </section>

            <section className="rounded-3xl border border-slate-700 bg-slate-900 p-6">
              <h2 className="text-2xl font-bold text-white">
                Detected technical skills
              </h2>

              <div className="mt-6 space-y-6">
                {Object.entries(structured.skills).map(
                  ([category, skills]) => (
                    <div key={category}>
                      <h3 className="font-semibold text-cyan-300">
                        {formatLabel(category)}
                      </h3>

                      <div className="mt-3 flex flex-wrap gap-2">
                        {skills.map((skill) => (
                          <span
                            key={`${category}-${skill}`}
                            className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1.5 text-sm text-slate-300"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  ),
                )}
              </div>
            </section>

            <section className="grid gap-4 sm:grid-cols-3">
              {Object.entries(structured.statistics).map(
                ([label, value]) => (
                  <div
                    key={label}
                    className="rounded-2xl border border-slate-700 bg-slate-900 p-6 text-center"
                  >
                    <p className="text-3xl font-black text-white">
                      {value}
                    </p>
                    <p className="mt-2 text-sm text-slate-400">
                      {formatLabel(label)}
                    </p>
                  </div>
                ),
              )}
            </section>

            <section className="rounded-3xl border border-slate-700 bg-slate-900 p-6 sm:p-8">
              <h2 className="text-2xl font-bold text-white">
                Match against a job description
              </h2>

              <p className="mt-2 text-slate-400">
                Paste a job description to measure skill alignment and
                identify missing keywords.
              </p>

              <textarea
                value={jobDescription}
                onChange={(event) =>
                  setJobDescription(event.target.value)
                }
                rows={10}
                placeholder="Paste the complete job description here..."
                className="mt-6 w-full resize-y rounded-2xl border border-slate-700 bg-slate-950 p-4 text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-cyan-400"
              />

              <button
                type="button"
                onClick={analyzeJobMatch}
                disabled={matching || !jobDescription.trim()}
                className="mt-4 rounded-xl bg-cyan-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {matching ? "Matching..." : "Analyze Job Match"}
              </button>
            </section>
          </>
        )}

        {jobMatch && (
          <section className="space-y-6">
            <div className="rounded-3xl border border-cyan-800 bg-cyan-950/20 p-8 text-center">
              <p className="text-sm font-bold uppercase tracking-widest text-cyan-400">
                Job Match Score
              </p>

              <p className="mt-4 text-6xl font-black text-white">
                {jobMatch.match_score}%
              </p>

              <p className="mt-3 text-slate-400">
                {jobMatch.keyword_coverage.matched} of{" "}
                {jobMatch.keyword_coverage.required} recognized job
                skills matched
              </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <ListCard
                title="Matched skills"
                items={jobMatch.matched_skills}
              />

              <ListCard
                title="Missing skills"
                items={jobMatch.missing_skills}
              />
            </div>
          </section>
        )}

        {feedback && (
          <section className="rounded-3xl border border-slate-700 bg-slate-900 p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-white">
              Personalized feedback
            </h2>

            <p className="mt-4 rounded-2xl bg-slate-950 p-5 leading-7 text-slate-300">
              {feedback.summary}
            </p>

            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              <ListCard
                title="Priority improvements"
                items={feedback.priority_improvements}
              />

              <ListCard
                title="Matched strengths"
                items={feedback.matched_strengths}
              />
            </div>
          </section>
        )}
      </div>

      <footer className="border-t border-slate-800 px-6 py-8 text-center text-sm text-slate-500">
        AI Resume Analyzer · FastAPI · PostgreSQL · Next.js
      </footer>
    </main>
  );
}
