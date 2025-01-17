import React, { useEffect } from 'react'
import { useAuth } from '../../providers/AuthProvider'
import { Navigate, Outlet } from 'react-router-dom'

const AuthLayout = () => {
	const { token } = useAuth()

  useEffect(() => {
    if (token) {
      <Navigate to='/' />
    }
  },[token])
	return (
		<section className='flex flex-1 justify-center items-center py-10'>
			<Outlet />
		</section>
	)
}

export default AuthLayout