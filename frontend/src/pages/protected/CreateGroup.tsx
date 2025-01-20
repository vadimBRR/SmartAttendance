import React, { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import CustomDropdown from '../../components/CustomDropdown'
import StickyAlert from '../../components/StickyAlert'
import SearchBar from '../../components/SearchBar'
import {
	useAddLesson,
	useStudentsWithoutGroup,
	useCourses,
	useCurrentWeek,
} from '../../hooks/useApi'

interface Course {
	id: number
	name: string
	short_name?: string
}

interface Student {
	id: number
	name: string
}

const CreateGroup = () => {
	const [searchParams] = useSearchParams()
	const navigate = useNavigate()
	const addLessonMutation = useAddLesson()

	const day = searchParams.get('day') || ''
	const start_time = searchParams.get('start_time') || ''
	const finish_time = searchParams.get('finish_time') || ''
	const isTest = searchParams.get('is_test')
		? searchParams.get('is_test') === 'true'
		: false

	const teacher_id = 1
	const classroom_id = 1

	const {
		data: courses,
		isLoading: isCoursesLoading,
		error: coursesError,
	} = useCourses(teacher_id)
	const current_week = useCurrentWeek().data || 0

	const [selectedCourseId, setSelectedCourseId] = useState<number | null>(
		isTest ? 404 : null
	)
	console.log(selectedCourseId)
	const {
		data: students,
		isLoading: isStudentsLoading,
		error: studentsError,
	} = useStudentsWithoutGroup(selectedCourseId || 0)

	console.log(students)

	const [searchQuery, setSearchQuery] = useState('')
	const [selectedStudents, setSelectedStudents] = useState<number[]>([])
	const [attendance, setAttendance] = useState<
		Record<number, (boolean | null)[]>
	>({})
	const [testDuration, setTestDuration] = useState<string>('')
	const [alertMessage, setAlertMessage] = useState<string | null>(null)

	const filteredStudents = students?.filter((student: Student) =>
		student.name.toLowerCase().includes(searchQuery.toLowerCase())
	)

	const test_course = [
		{
			id: 404,
			name: 'Test course',
		},
	]

	useEffect(() => {
		if (students && selectedCourseId) {
			setAttendance(
				students.reduce(
					(acc: Record<number, (boolean | null)[]>, student: Student) => {
						acc[student.id] = Array(current_week).fill(true)
						return acc
					},
					{} as Record<number, (boolean | null)[]>
				)
			)
		}
	}, [students, selectedCourseId])

	useEffect(() => {
		if (isTest) {
			setSelectedCourseId(404)
		} else if (courses && courses.length > 0) {
			setSelectedCourseId(courses[0].id)
		}
	}, [courses])

	const toggleStudentSelection = (id: number) => {
		setSelectedStudents(prev =>
			prev.includes(id)
				? prev.filter(studentId => studentId !== id)
				: [...prev, id]
		)
	}

	const cycleAttendance = (studentId: number, weekIndex: number) => {
		setAttendance(prev => ({
			...prev,
			[studentId]: prev[studentId].map((value, index) => {
				if (index !== weekIndex) return value
				if (value === true) return false
				if (value === false) return null
				return true
			}),
		}))
	}

	const [isFormSubmitted, setIsFormSubmitted] = useState(false)
	const formatCreatedAt = (): string => {
		const date = new Date()
		return date.toISOString().split('Z')[0]
	}

	const handleSubmit = () => {
    if (!selectedCourseId) {
      setAlertMessage('Please select a course before submitting.');
      return;
    }
    if (selectedStudents.length === 0) {
      setAlertMessage('Please select at least one student.');
      return;
    }
  
    const formatTime = (time: Date): string => {
      const hour = time.getHours().toString().padStart(2, '0');
      const minute = time.getMinutes().toString().padStart(2, '0');
      const second = time.getSeconds().toString().padStart(2, '0');
      return `${hour}:${minute}:${second}`;
    };

  
    const calculateFinishTime = (startTime: Date, duration: number): Date => {
      const finishTime = new Date(startTime);
      finishTime.setMinutes(finishTime.getMinutes() + duration);
      return finishTime;
    };
		const formatTimeString = (time: string): string => {
			const [hour, minute, second] = time.split(':')
			return `${hour.padStart(2, '0')}:${minute}:${second || '00'}`
		}
  
    const fullDayNames = {
      Mon: 'Monday',
      Tue: 'Tuesday',
      Wed: 'Wednesday',
      Thu: 'Thursday',
      Fri: 'Friday',
      Sat: 'Saturday',
      Sun: 'Sunday',
    };
  
    let startTime = start_time;
    let finishTime = finish_time;
  
    if (isTest) {
      const now = new Date();
      const duration1 = parseInt('11', 10) || 0;

      startTime = formatTime(calculateFinishTime(now, 11));
      const duration = parseInt(testDuration, 10) || 0;
      finishTime = formatTime(calculateFinishTime(now, duration));
    }
  
    const payload = {
      course_id: selectedCourseId,
      teacher_id,
      classroom_id,
      students: selectedStudents
        .map(id => {
          const student = students?.find(
            (student: Student) => student.id === id
          );
          return student
            ? {
                student_id: id,
                name: student.name as string,
                attendance: [
                  {
                    present: attendance[id],
                    arrival_time: attendance[id].map(() => null),
                  },
                ],
              }
            : null;
        })
        .filter(Boolean),
      created_at: formatCreatedAt(),
      day_of_week: fullDayNames[day as keyof typeof fullDayNames] || day,
      start_time: !isTest ? formatTimeString(startTime) : startTime,
      finish_time: !isTest ? formatTimeString(finishTime) : finishTime,
    };
  
    console.log(payload);
    if (isFormSubmitted) return;
  
    setIsFormSubmitted(true);
    addLessonMutation.mutate(payload, {
      onSuccess: () => {
        setIsFormSubmitted(false);
        if(isTest){
          navigate('/attendance_test');
        }else{
          navigate('/');
        }
      },
      onError: (error: any) => {
        setAlertMessage(error.message || 'Failed to add lesson.');
        setIsFormSubmitted(false);
      },
    });
  };
  

	useEffect(() => {
		return () => {
			setIsFormSubmitted(false)
			setSelectedCourseId(null)
			setSelectedStudents([])
			setAttendance({})
		}
	}, [])

	if (isCoursesLoading) {
		return <div>Loading courses...</div>
	}

	if (coursesError) {
		return <div>Error loading courses: {coursesError.message}</div>
	}

	return (
		<div className='p-6 relative'>
			{alertMessage && (
				<StickyAlert
					message={alertMessage}
					onClose={() => setAlertMessage(null)}
				/>
			)}
      <h1 className="text-3xl font-bold mb-6 text-[#2596be]">Create Group</h1>

			{!isTest ? (
				<div className='bg-gray-100 p-4 rounded shadow'>
					<p className='text-lg'>
						<strong>Day:</strong> {day}
					</p>
					<p className='text-lg'>
						<strong>Start Time:</strong> {start_time}
					</p>
					<p className='text-lg'>
						<strong>Finish Time:</strong> {finish_time}
					</p>
				</div>
			) : (
				<div>
					<h2 className='text-2xl font-semibold mb-2 text-[#2596be]'>
						Test Duration (minutes)
					</h2>
					<input
						type='number'
						value={testDuration}
						onChange={e => setTestDuration(e.target.value)}
						className='p-2 border border-gray-300 rounded w-full bg-white text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#2596be] focus:border-[#2596be]'
						placeholder='Enter test duration'
					/>
				</div>
			)}
			<div className='space-y-6'>
				<div>
					<h2 className='text-2xl font-semibold mb-2 text-[#2596be]'>
						Select Course
					</h2>
					<CustomDropdown
						options={
							isTest
								? test_course.map((course: Course) => ({
										id: course.id,
										label: course.name,
								  }))
								: courses?.map((course: Course) => ({
										id: course.id,
										label: course.name,
								  })) || []
						}
						selectedOption={isTest ? 404 : selectedCourseId}
						onSelect={setSelectedCourseId}
					/>
				</div>

				<div>
					<h2 className='text-2xl font-semibold mb-4 text-[#2596be]'>
						Search Students
					</h2>
					<SearchBar query={searchQuery} setQuery={setSearchQuery} />
				</div>

				<div>
					<h2 className='text-2xl font-semibold mb-4 text-[#2596be]'>
						Select Students
					</h2>
					{filteredStudents?.length === 0 ? (
						<p className='text-center text-gray-500'>
							All students have been added to this course.
						</p>
					) : (
						<div className='space-y-4'>
							{filteredStudents?.map((student: Student, index: number) => (
								<div
									key={student.id}
									className={`p-4 rounded shadow flex items-center justify-between transition cursor-pointer ${
										selectedStudents.includes(student.id)
											? 'bg-[#2596be] text-white'
											: 'bg-gray-100'
									}`}
									onClick={() => toggleStudentSelection(student.id)}
								>
									<span className='font-semibold'>
										{index + 1}. {student.name}
									</span>
								</div>
							))}
						</div>
					)}
				</div>

				{selectedStudents.length > 0 && (
					<div>
						<h2 className='text-2xl font-semibold mb-4 text-[#2596be]'>
							Set Attendance
						</h2>
						<div className='space-y-6'>
							{selectedStudents.map(studentId => (
								<div
									key={studentId}
									className='p-6 rounded shadow bg-gray-50 flex flex-col gap-4'
								>
									<h3 className='font-bold text-lg text-gray-800'>
										{
											students?.find(
												(student: Student) => student.id === studentId
											)?.name
										}
									</h3>
									<div className='flex flex-wrap gap-2'>
										{[...Array(current_week)].map((_, weekIndex) => (
											<div
												key={weekIndex}
												className={`w-12 h-12 flex items-center justify-center rounded-lg cursor-pointer transition ${
													attendance[studentId][weekIndex] === true
														? 'bg-green-500 text-white'
														: attendance[studentId][weekIndex] === false
														? 'bg-red-500 text-white'
														: 'bg-gray-200 text-gray-700'
												}`}
												onClick={() => cycleAttendance(studentId, weekIndex)}
												title={`Week ${weekIndex + 1}`}
											>
												{weekIndex + 1}
											</div>
										))}
									</div>
								</div>
							))}
						</div>
					</div>
				)}

				<div className='flex justify-center'>
					<button
						onClick={handleSubmit}
						disabled={isFormSubmitted || addLessonMutation.isPending}
						className={`px-6 py-3 font-semibold rounded shadow transition ${
							isFormSubmitted || addLessonMutation.isPending
								? 'bg-gray-400 text-gray-700 cursor-not-allowed'
								: 'bg-[#2596be] text-white hover:bg-[#197b9b]'
						}`}
					>
						{isFormSubmitted || addLessonMutation.isPending
							? 'Submitting...'
							: 'Submit'}
					</button>
				</div>
			</div>
		</div>
	)
}

export default CreateGroup
