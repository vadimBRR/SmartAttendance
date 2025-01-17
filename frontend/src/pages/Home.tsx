import React, { useEffect, useState } from 'react'
import { useGetSubjects, useGetGroups } from '../api/index'
import SubjectItem from '../components/SubjectItem'

const Home = () => {
	const [subjects, setSubjects] = useState([
		{ id: 1, name: 'SMART-IOT' },
		{ id: 2, name: 'ISI' },
	])
	// const [groups, setGroups] = useState([]);
	const [loading, setLoading] = useState(true)
  

	useEffect(() => {
		const fetchData = async () => {
			try {
				const [fetchedSubjects, fetchedGroups] = await Promise.all([
					useGetSubjects(),
					useGetGroups(),
				])

				setSubjects(fetchedSubjects)
				// setGroups(fetchedGroups);
			} catch (error) {
				console.error('Error fetching data:', error)
			} finally {
				setLoading(false)
			}
		}

		fetchData()
	}, [])

	if (loading) {
		return <p>Loading...</p>
	}

	return (
		<div>
			<h1>Home</h1>

			<section>
				<h2>Subjects</h2>
        <div className='flex flex-row gap-5'>
          {subjects.map((subject: any, index: number) => (
            <SubjectItem key={index} id={subject.id} name={subject.name} />
          ))}

        </div>
			</section>

			{/* <section>
        <h2>Groups</h2>
        <ul>
          {groups.map((group: any, index: number) => (
            <li key={index}>{group.name}</li>
          ))}
        </ul>
      </section> */}
		</div>
	)
}

export default Home
