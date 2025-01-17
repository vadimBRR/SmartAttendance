import { Route, Router, Routes } from 'react-router-dom'
import Home from './pages/Home'

import Navbar from './components/Navbar'
import Groups from './pages/Groups'
import Attendance from './pages/Attendance'

function App() {
	return (
		<div className='flex h-screen relative w-full'>
			<div className='absolute top-0'>
				{/* <Navbar /> */}
			</div>
			<div className='w-full h-screen mt-12 mx-10'>
				<Routes>
					<Route path='/' element={<Home />} />
          <Route path="/groups/:id" element={<Groups />} />
          <Route path="/attendance/:id" element={<Attendance />} />
				</Routes>
			</div>
		</div>
	)
}

export default App
