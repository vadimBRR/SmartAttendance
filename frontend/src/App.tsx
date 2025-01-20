import { Route, Routes } from 'react-router-dom'
import Groups from './pages/protected/Groups'
import Attendance from './pages/protected/Attendance'
import CreateGroup from './pages/protected/CreateGroup'
import RootLayout from './pages/protected/RootLayout'
import SignIn from './pages/auth/SignIn'
import AuthLayout from './pages/auth/AuthLayout'
import SignUp from './pages/auth/SignUp'
import { useAuth } from './providers/AuthProvider'
import GroupsForStudent from './pages/protected/GroupsForStudent'
import GroupsForUnknown from './pages/protected/GroupsForUnknown'
import AttendanceStudent from './pages/protected/AttendanceStudent'

function App() {
	const { isTeacher, userId } = useAuth()
	return (
		<div className='flex h-screen w-full'>
			<Routes>
				<Route element={<AuthLayout />}>
					<Route path='/sign-in' element={<SignIn />} />
					<Route path='/sign-up' element={<SignUp />} />
				</Route>

				<Route element={<RootLayout />}>
					{userId === '-1' ? (
						<Route path='/' element={<GroupsForUnknown />} />
					) : isTeacher ? (
            <>
              <Route path='/' element={<Groups />} />
            <Route path='/attendance/:id' element={<Attendance />} />
            </>

					) : (
            <>
              <Route path='/' element={<GroupsForStudent />} />
            <Route path='/attendance/:id' element={<AttendanceStudent />} />
            </>

					)}

					<Route path='/create-group' element={<CreateGroup />} />{' '}
				</Route>
			</Routes>
		</div>
	)
}

export default App
