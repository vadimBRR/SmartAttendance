import { Route, Router, Routes } from 'react-router-dom'
import Home from './pages/protected/Home'

import Navbar from './components/Navbar'
import Groups from './pages/protected/Groups'
import Attendance from './pages/protected/Attendance'
import RootLayout from './pages/protected/RootLayout'
import SignIn from './pages/auth/SignIn'
import AuthLayout from './pages/auth/AuthLayout'

function App() {
	return (
		<div className='flex h-screen w-full'>
			{/* <div className='w-full h-screen mt-12 mx-10'>
				<Routes>
					<Route path='/' element={<Home />} />
					<Route path='/groups/:id' element={<Groups />} />
					<Route path='/attendance/:id' element={<Attendance />} />
				</Routes>
        <div className='flex h-screen'> */}
			<Routes>
				{/* <Route element={<AuthLayout />}>
					<Route path='/sign-in' element={<SignIn />} />
				</Route> */}

				<Route element={<RootLayout />}>
					<Route path='/' element={<Home />} />
					<Route path='/groups/:id' element={<Groups />} />
					<Route path='/attendance/:id' element={<Attendance />} />
				</Route>
			</Routes>
		</div>
	)
}

export default App
