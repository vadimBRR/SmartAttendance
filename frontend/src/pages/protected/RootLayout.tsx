import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import Footer from '../../components/Footer'
import { useAuth } from '../../providers/AuthProvider'
import Navbar from '../../components/Navbar'

const RootLayout = () => {
	const { token,isTeacher } = useAuth();
  console.log(isTeacher);

	if (!token) {
	  return <Navigate to="/sign-in" />;
	}

	console.log("OPEEEEENNNN")
	return (
		<div className='w-full h-screen'>
			<section className='flex-1 h-full w-full px-2 my-5'>
				<Outlet />
			</section>
		</div>
	)
}

export default RootLayout
