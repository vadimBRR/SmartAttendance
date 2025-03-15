import React, { useEffect } from 'react'
import { useAuth } from '../../providers/AuthProvider'
import { Navigate, Outlet } from 'react-router-dom'

const AuthLayout = () => {
  const { token } = useAuth()
  console.log(token);
  if (token) {
    return <Navigate to='/' />
  }
  return (
    <section className='flex flex-1 justify-center items-center py-10'>
      <Outlet />
    </section>
  )
}

export default AuthLayout