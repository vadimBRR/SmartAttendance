import React from 'react'
import { useNavigate } from 'react-router-dom'

const SubjectItem = ({id,name}:{id:number,name:string}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/groups/${id}`);
  };
  return (
    <div className='bg-black/20 w-64 h-36 rounded-lg flex justify-center items-center border shadow-sm hover:bg-black/30 transition cursor-pointer'  onClick={handleClick}>
      <p className='text-4xl'>{name}</p>
    </div>
  )
}

export default SubjectItem