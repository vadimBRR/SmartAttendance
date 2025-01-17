const API_BASE_URL = 'http://127.0.0.1:8000'

export const fetchCourses = async (teacherId: number) => {
	const response = await fetch(`${API_BASE_URL}/courses/${teacherId}`, {
		method: 'GET',

	})
	if (!response.ok) {
		throw new Error('Failed to fetch courses')
	}
	return response.json()
}

export const fetchLessons = async (courseId: number, teacherId: number) => {
	const response = await fetch(
		`${API_BASE_URL}/lessons/${courseId}/${teacherId}`,
		{
			method: 'GET',
			headers: {
				'Content-Type': 'application/json', // Додано
			},
			mode: 'cors',
		}
	)
	if (!response.ok) {
		throw new Error('Failed to fetch lessons')
	}
	return response.json()
}

export const fetchLessonAttendance = async (lessonId: number) => {
	const response = await fetch(
		`${API_BASE_URL}/lessons${lessonId}/attendance`,
		{
			method: 'GET',
			headers: {
				'Content-Type': 'application/json', // Додано
			},
		}
	)
	if (!response.ok) {
		throw new Error('Failed to fetch lesson attendance')
	}
	return response.json()
}

import { useQuery, useMutation } from '@tanstack/react-query'

import { useAuth } from '../providers/AuthProvider'

export interface LoginResponse {
	access_token: string
	username: string
}
export interface PredictionResponse {
	predicted_total_price: number
}

export const useLogin = async (
	username: string,
	password: string
): Promise<LoginResponse> => {
	console.log(username)
	const formDetails = new URLSearchParams()
	formDetails.append('username', username)
	formDetails.append('password', password)

	const response = await fetch('http://127.0.0.1:8000/token', {
		method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		body: formDetails,
	})

	if (!response.ok) {
		const errorData = await response.json()
		throw new Error(errorData.detail || 'Authentication failed')
	}

	return await response.json()
}

export const useRegister = async (
	username: string,
	password: string
): Promise<void> => {
	const response = await fetch('http://127.0.0.1:8000/register', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ username, password }),
	})

	if (!response.ok) {
		const errorData = await response.json()
		throw new Error(errorData.detail || 'Registration failed')
	}
}
export const useVerifyToken = async (token: string): Promise<void> => {
	const response = await fetch(`http://127.0.0.1:8000/verify-token/${token}`)
	if (!response.ok) {
		throw new Error('Token verification failed')
	}
}

export const useGetUser = async (token: string): Promise<void> => {
	const response = await fetch(`http://127.0.0.1:8000/me`, {
		headers: {
			Authorization: `Bearer ${token}`,
		},
	})
	if (!response.ok) {
		throw new Error('User retrieval failed')
	}
}
