/* 模块三：笔试 / 面试 / 问答复盘 / 结果 / 题库 */
import { del, get, post, put, uploadFile } from './http'
import type { Exam, ExamReview, Interview, InterviewQa, InterviewResult, PageData, Question } from '@/types'

/* ---- 笔试 ---- */
export function listExams(params?: { application_id?: number; status?: string }) {
  return get<Exam[]>('/exams', params)
}
export const createExam = (data: Record<string, unknown>) => post<Exam>('/exams', data)
export const updateExam = (id: number, data: Record<string, unknown>) => put<Exam>(`/exams/${id}`, data)
export const deleteExam = (id: number) => del<null>(`/exams/${id}`)
export const getExamReview = (id: number) => get<ExamReview | null>(`/exams/${id}/review`)
export const saveExamReview = (id: number, data: Record<string, unknown>) => put<ExamReview>(`/exams/${id}/review`, data)

/* ---- 面试 ---- */
export function listInterviews(params?: { application_id?: number; status?: string; round?: string }) {
  return get<Interview[]>('/interviews', params)
}
export const createInterview = (data: Record<string, unknown>) => post<Interview>('/interviews', data)
export const updateInterview = (id: number, data: Record<string, unknown>) => put<Interview>(`/interviews/${id}`, data)
export const deleteInterview = (id: number) => del<null>(`/interviews/${id}`)

/* ---- 问答 ---- */
export const listInterviewQa = (interviewId: number) => get<InterviewQa[]>(`/interviews/${interviewId}/qa`)
export const createInterviewQa = (interviewId: number, data: Record<string, unknown>) =>
  post<InterviewQa>(`/interviews/${interviewId}/qa`, data)
export const updateInterviewQa = (qaId: number, data: Record<string, unknown>) =>
  put<InterviewQa>(`/interview-qa/${qaId}`, data)
export const deleteInterviewQa = (qaId: number) => del<null>(`/interview-qa/${qaId}`)

/* ---- 面试结果 / 录音 ---- */
export const getInterviewResult = (id: number) => get<InterviewResult | null>(`/interviews/${id}/result`)
export const saveInterviewResult = (id: number, data: Record<string, unknown>) =>
  put<InterviewResult>(`/interviews/${id}/result`, data)
export const uploadInterviewAudio = (id: number, file: File) =>
  uploadFile<InterviewResult>(`/interviews/${id}/audio`, file)

/* ---- 题库 ---- */
export function listQuestions(params?: {
  category?: string
  difficulty?: string
  review_status?: string
  keyword?: string
  tag?: string
  page?: number
  page_size?: number
}) {
  return get<Question[] | PageData<Question>>('/questions', params)
}
export const createQuestion = (data: Record<string, unknown>) => post<Question>('/questions', data)
export const updateQuestion = (id: number, data: Record<string, unknown>) => put<Question>(`/questions/${id}`, data)
export const deleteQuestion = (id: number) => del<null>(`/questions/${id}`)
export const setQuestionReviewStatus = (id: number, review_status: string) =>
  put<Question>(`/questions/${id}/review-status`, { review_status })