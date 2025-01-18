import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import Footer from '../../components/Footer'
import { useAuth } from '../../providers/AuthProvider'
import Navbar from '../../components/Navbar'

const RootLayout = () => {
	// const { token } = useAuth();

	// if (!token) {
	//   return <Navigate to="/sign-in" />;
	// }
	return (
		<div className='w-full h-screen'>
			{/* <Navbar/> */}
			<section className='flex-1 h-full w-full px-2 my-5'>
				<Outlet />
			</section>
			{/* <Footer /> */}
		</div>
	)
}

export default RootLayout
