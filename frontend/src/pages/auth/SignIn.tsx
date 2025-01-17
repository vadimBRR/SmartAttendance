import React, { useState } from 'react'
import CustomInput from '../../components/CustomInput'
import CustomButton from '../../components/CustomButton'
import { useAuth } from '../../providers/AuthProvider'
import { Link } from 'react-router-dom'

const SignIn = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const {login, isLoading, error} = useAuth()
  const handleLogin = async () => {
    console.log("object");
    await login(username, password)

  }
  return (
    <div>
      <p className='text-center text-2xl'>Sign In</p>
      <CustomInput name={username} setName={setUsername} title='Username' containerStyle='my-4'/>
      <CustomInput name={password} setName={setPassword} title='Password' containerStyle='my-4' isPassword={true}/>
      <CustomButton handleClick={handleLogin} text='Sign In' isLoading={isLoading}/>
      <p className="text-[#ff0000] mb-2">{error}</p>
      <div className='flex flex-row gap-1'>
				<p>Don't have an account?</p>
				<Link to='/sign-up'>
					<p className='text-primary'>Sign Up</p>
				</Link>
			</div>
    </div>
  )
}

export default SignIn