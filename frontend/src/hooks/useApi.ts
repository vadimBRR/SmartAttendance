import { useQuery } from '@tanstack/react-query';
import { fetchCourses, fetchLessons, fetchLessonAttendance } from '../api';

// Хук для отримання курсів за `teacher_id`
export const useCourses = (teacherId: number) => {
  return useQuery({
    queryKey: ['courses', teacherId],
    queryFn: () => fetchCourses(teacherId),
  });
};

// Хук для отримання уроків за `course_id` і `teacher_id`
export const useLessons = (courseId: number, teacherId: number) => {
  return useQuery({
    queryKey: ['lessons', courseId, teacherId],
    queryFn: () => fetchLessons(courseId, teacherId),
  });
};

// Хук для отримання відвідуваності уроку за `lesson_id`
export const useLessonAttendance = (lessonId: number) => {
  return useQuery({
    queryKey: ['lessonAttendance', lessonId],
    queryFn: () => fetchLessonAttendance(lessonId),
  });
};