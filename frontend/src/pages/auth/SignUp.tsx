import React, { useState } from 'react'
import CustomInput from '../../components/CustomInput'
import CustomButton from '../../components/CustomButton'
import { useAuth } from '../../providers/AuthProvider'
import { Link } from 'react-router-dom'

const SignUp = () => {
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const { register, isLoading, error } = useAuth()
	const handleRegister = async () => {
		await register(username, password)
	}
	return (
		<div>
			<p className='text-center text-2xl'>Sign Up </p>
			<CustomInput
				name={username}
				setName={setUsername}
				title='Username'
				containerStyle='my-4'
			/>
			<CustomInput
				name={password}
				setName={setPassword}
				title='Password'
				containerStyle='my-4'
				isPassword={true}
			/>
			<CustomButton
				handleClick={handleRegister}
				text='Sign In'
				isLoading={isLoading}
			/>
			<p className='text-[#ff0000] mb-2'>{error}</p>
			<div className='flex flex-row gap-1'>
				<p>Already have an account? </p>
				<Link to='/sign-in'>
					<p className='text-primary'>Sign In</p>
				</Link>
			</div>
		</div>
	)
}

export default SignUp