import React, { useState } from 'react'
import GroupItem from '../components/GroupItem'
import { useParams } from 'react-router-dom'

const time = ['7:30', '9:10', '10:50', '13:30', '15:10']
const week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const temp_group = [
	{ id: 1, time: '7:30', day: 'Mon' },
	{ id: 2, time: '10:50', day: 'Mon' },
	{ id: 3, time: '9:10', day: 'Tue' },
]

const Groups = () => {
  const { id } = useParams<{ id: string }>();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(false);


  if (loading) {
    return <p>Loading...</p>;
  }

	return (
		<div className='flex flex-col gap-2 bg-white p-6 rounded shadow'>
			<div
				className='grid'
				style={{ gridTemplateColumns: `100px repeat(${time.length}, 1fr)` }}
			>
				<div></div>
				{time.map((t, index) => (
					<div
						key={index}
						className='text-center font-bold text-gray-800 border-b'
					>
						{t}
					</div>
				))}
			</div>

			{week_days.map((day, rowIndex) => (
				<div
					key={rowIndex}
					className='grid '
					style={{ gridTemplateColumns: `100px repeat(${time.length}, 1fr)` }}
				>
					<div className='text-center font-bold text-gray-800 border-r flex items-center justify-center'>
						{day}
					</div>

					{time.map((t, colIndex) => {
						const group = temp_group.find(g => g.time === t && g.day === day)
						return <GroupItem key={colIndex} group={group} />
					})}
				</div>
			))}
		</div>
	)
}

export default Groups
