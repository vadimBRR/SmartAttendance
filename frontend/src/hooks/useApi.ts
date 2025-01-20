import { useMutation, useQuery } from '@tanstack/react-query';
import { fetchCourses, fetchLessons, fetchLessonAttendance, fetchStudentsWithoutGroup, addLesson, addLessonAttendance, fetchCurrentWeek, fetchPicoState, fetchLessonsByStudent, fetchLessonAttendanceByStudent, changeClassroom, fetchClassrooms, fetchCurrentClassroom, deleteTestLesson, fetchTestLesson } from '../api';

export const useCourses = (teacherId: number) => {
  return useQuery({
    queryKey: ['courses', teacherId],
    queryFn: () => fetchCourses(teacherId),
  });
};

export const useLessons = ( teacherId: string) => {
  return useQuery({
    queryKey: ['lessons',  teacherId],
    queryFn: () => fetchLessons(teacherId),
  });
};

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
  const { refetch: refetchLessonAttendance } = useLessonAttendance(lessonId);

  return useMutation({
    mutationFn: ({
      lessonId,
      weekNumber,
      studentId,
      present,
    }: {
      lessonId: number;
      weekNumber: number;
      studentId: number;
      present: boolean | null;
    }) => addLessonAttendance({ lessonId, weekNumber, studentId, present }),
    onSuccess: () => {
      console.log('Attendance added successfully');
      refetchLessonAttendance(); 
    },
    onError: (error: any) => {
      console.error('Failed to add attendance:', error.message || error);
    },
  });
};

export const useCurrentWeek = () => {
  return useQuery({
    queryKey: ['currentWeek'],
    queryFn: fetchCurrentWeek,
  });
};

export const usePicoState = () => {
  return useQuery({
    queryKey: ['picoState'],
    queryFn: fetchPicoState,
  });
};


export const useLessonsByStudent = (studentId: string) => {
  return useQuery({
    queryKey: ['lessonsByStudent', studentId],
    queryFn: () => fetchLessonsByStudent(studentId),
  });
};


export const useLessonAttendanceByStudent = (lessonId: number, studentId: string) => {
  return useQuery({
    queryKey: ['lessonAttendanceByStudent', lessonId, studentId],
    queryFn: () => fetchLessonAttendanceByStudent(lessonId, studentId),
  });
};

export const useClassrooms = () => {
  return useQuery({
    queryKey: ['classrooms'],
    queryFn: fetchClassrooms,
  });
};

export const useChangeClassroom = () => {
  return useMutation({
    mutationFn: changeClassroom,
    onSuccess: () => {
      console.log('Classroom changed successfully');
    },
    onError: (error: any) => {
      console.error('Failed to change classroom:', error.message || error);
    },
  });
};

export const useCurrentClassroom = () => {
  return useQuery({
    queryKey: ['currentClassroom'],
    queryFn: fetchCurrentClassroom,
  });
};

export const useTestLesson = () => {
  console.log("test lesson");
  return useQuery({
    queryKey: ['testLesson'],
    queryFn: fetchTestLesson,
  });
};

export const useDeleteTestLesson = () => {
  return useMutation({
    mutationFn: deleteTestLesson,
    onSuccess: () => {
      console.log('Test lesson deleted successfully');
    },
    onError: (error: any) => {
      console.error('Failed to delete test lesson:', error.message || error);
    },
  });
};