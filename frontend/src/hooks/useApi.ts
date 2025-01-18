import { useMutation, useQuery } from '@tanstack/react-query';
import { fetchCourses, fetchLessons, fetchLessonAttendance, fetchStudentsWithoutGroup, addLesson, addLessonAttendance } from '../api';

// Хук для отримання курсів за `teacher_id`
export const useCourses = (teacherId: number) => {
  return useQuery({
    queryKey: ['courses', teacherId],
    queryFn: () => fetchCourses(teacherId),
  });
};

// Хук для отримання уроків за `course_id` і `teacher_id`
export const useLessons = ( teacherId: number) => {
  return useQuery({
    queryKey: ['lessons',  teacherId],
    queryFn: () => fetchLessons(teacherId),
  });
};

// Хук для отримання відвідуваності уроку за `lesson_id`
export const useLessonAttendance = (lessonId: number) => {
  return useQuery({
    queryKey: ['lessonAttendance', lessonId],
    queryFn: () => fetchLessonAttendance(lessonId),
  });
};

export const useStudentsWithoutGroup = (courseId: number) => {
	return useQuery({
		queryKey: ['studentsWithoutGroup', courseId],
		queryFn: () => fetchStudentsWithoutGroup(courseId),
	})
}

export const useAddLesson = () => {
  return useMutation({
    mutationFn: addLesson,
    onSuccess: () => {
      console.log('Lesson added successfully');
    },
    onError: (error: any) => {
      console.error('Failed to add lesson:', error.message || error);
    },
  });
};

export const useAddLessonAttendance = (lessonId: number) => {
  // Використовуємо хук для отримання даних про відвідуваність
  const { refetch: refetchLessonAttendance } = useLessonAttendance(lessonId);

  return useMutation({
    mutationFn: ({ lessonId, weekNumber, studentId }: { lessonId: number; weekNumber: number; studentId: number }) =>
      addLessonAttendance({ lessonId, weekNumber, studentId }),
    onSuccess: () => {
      console.log('Attendance added successfully');
      // Після успішного додавання відвідуваності робимо запит для отримання актуальних даних
      refetchLessonAttendance();
    },
    onError: (error: any) => {
      console.error('Failed to add attendance:', error.message || error);
    },
  });
};