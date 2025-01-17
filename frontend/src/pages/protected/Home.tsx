import React from 'react';
import SubjectItem from '../../components/SubjectItem';
import { useCourses } from '../../hooks/useApi';

const Home = () => {
  const teacherId = 1; 
  const { data: subjects, isLoading, error } = useCourses(teacherId);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {(error as Error).message}</div>;

  return (
    <div>
      <h1>Home</h1>

      <section>
        <h2>Subjects</h2>
        <div className='flex flex-row gap-5'>
          {subjects &&
            Object.entries(subjects).map(([id, name]) => (
              <SubjectItem key={id} id={parseInt(id)} name={name as string} />
            ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
