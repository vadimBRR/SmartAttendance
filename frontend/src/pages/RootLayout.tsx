import React from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

const RootLayout = () => {
	return (
		<div className='w-full '>
			<Navbar />
			<section className='flex flex-1 h-full'>
				<Outlet />
			</section>
			<Footer />
		</div>
	)
}

export default RootLayout
