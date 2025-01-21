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

export interface Lesson {
  id: number;
  day_of_week: string;
  start_time: string;
  finish_time: string;
  short_course_name: string;
}

export const fetchLessons = async ( teacherId: string): Promise<{ lessons: Lesson[] }>  => {
	const response = await fetch(
		`${API_BASE_URL}/lessons/${teacherId}`,
		{
			method: 'GET',
			headers: {
				'Content-Type': 'application/json', 
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
				'Content-Type': 'application/json', 
			},
		}
	)
	if (!response.ok) {
		throw new Error('Failed to fetch lesson attendance')
	}
	return response.json()
}

export const fetchStudentsWithoutGroup = async (courseId: number) => {
  const response = await fetch(
    `${API_BASE_URL}/create_group?course_id=${courseId}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch students without group');
  }

  const data = await response.json();

  // Перетворюємо id студентів в рядки, щоб уникнути округлення
  const students = data.map((student: { id: any; name: string; email: string }) => ({
    ...student,
    id: String(student.id), // Перетворюємо ID в рядок
  }));

  console.log("Formatted students:", students);
  return students;
};

export const addLesson = async (payload: {
  course_id: number;
  students: {
    student_id: number;
    name: string;
    attendance: {
      present: (boolean | null)[];
      arrival_time: (string | null)[];
    }[];
  }[];
  created_at: string;
  day_of_week: string;
  start_time: string;
  finish_time: string;
  teacher_id: number;
  classroom_id: number;
}) => {
  const response = await fetch(`${API_BASE_URL}/add_lesson/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to add lesson');
  }

  return response.json();
};
export const addLessonAttendance = async ({
  lessonId,
  weekNumber,
  studentId,
  present,
}: {
  lessonId: number;
  weekNumber: number;
  studentId: number;
  present: boolean | null;
}) => {
  const url = new URL(`${API_BASE_URL}/lessons/lesson_${lessonId}/attendance/${weekNumber}/${studentId}`);

  const presentMapping: { [key: string]: number } = {
    true: 1,
    false: 2,
    null: 3,
  };

  url.searchParams.append('present', String(presentMapping[String(present)])); 

  const response = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to add attendance');
  }

  return response.json();
};

export const fetchCurrentWeek = async (): Promise<number> => {
  const response = await fetch(`${API_BASE_URL}/get-current-week`);
  if (!response.ok) {
    throw new Error('Failed to fetch current week');
  }
  return response.json();
};

export const fetchPicoState = async (): Promise<{ status: "online" | "offline" | "sleep" }> => {
  const response = await fetch(`${API_BASE_URL}/get-pico-state`);
  if (!response.ok) {
    throw new Error('Failed to fetch Pico state');
  }
  return response.json();
};




export interface LoginResponse {
	access_token: string
	email: string
}
export interface PredictionResponse {
	predicted_total_price: number
}

export const useLogin = async (
	email: string,
	password: string
): Promise<LoginResponse> => {
	console.log(email)
	const formDetails = new URLSearchParams()
	formDetails.append('username', email)
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
	email: string,
	password: string
): Promise<void> => {
	const response = await fetch('http://127.0.0.1:8000/register', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ email, password }),
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


export const fetchLessonsByStudent = async (studentId: string): Promise<{ lessons: Lesson[] }> => {
  const response = await fetch(`${API_BASE_URL}/lessons/student/${studentId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch lessons for student');
  }

  return response.json();
};

export const fetchLessonAttendanceByStudent = async (
  lessonId: number,
  studentId: string
): Promise<{ present: boolean | null; arrival_time: string | null, course_name: string,  short_course_name: string}[]> => {
  const response = await fetch(
    `${API_BASE_URL}/lessons${lessonId}/attendance/${studentId}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch lesson attendance for student');
  }

  return response.json();
};

export const changeClassroom = async (classroomId: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/change-classroom?classroom_id=${classroomId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ classroom_id: classroomId }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to change classroom');
  }
};

export const fetchClassrooms = async (): Promise<{ id: string; label: string }[]> => {
  const response = await fetch(`${API_BASE_URL}/get-classrooms`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch classrooms');
  }

  return response.json();
};

export const fetchCurrentClassroom = async (): Promise<{ id: string; label: string }> => {
  const response = await fetch(`${API_BASE_URL}/get-current-classroom`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch current classroom');
  }

  return response.json();
};

export const fetchTestLesson = async (): Promise<{
  students: {
    student_id: string;
    student_name: string;
    course_name: string;
    short_course_name: string;
    lesson_id: number;
    attendance: { present: boolean | null; arrival_time: string | null }[];
  }[];
}> => {
  const response = await fetch(`${API_BASE_URL}/get_test_lesson`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch test lesson');
  }

  return response.json();
};

export const deleteTestLesson = async (): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/delete_test_lesson`, {
    method: 'GET', // Якщо це видалення, розгляньте можливість змінити метод на 'DELETE'
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to delete test lesson');
  }
};


export const fetchIsTest = async (): Promise<{ is_in_test_mode: boolean}> => {
  const response = await fetch(`${API_BASE_URL}/is_test`);
  if (!response.ok) {
    throw new Error('Failed to fetch test mode status');
  }
  return response.json();
};
