import React, { useState } from 'react'
import CustomInput from '../../components/CustomInput'
import CustomButton from '../../components/CustomButton'
import { useAuth } from '../../providers/AuthProvider'
import { Link } from 'react-router-dom'

const SignIn = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const {login, isLoading, error} = useAuth()
  const handleLogin = async () => {
    console.log("object");
    await login(email, password)

  }

  console.log("TESTTTTTTTTTTTTT")
  return (
    <div>
      <div className='flex flex-col justify-center items-center bg-gray-400/10 py-6 px-12 rounded-xl' style={
        {
          boxShadow: ' 10px 10px 10px rgba(0, 0, 0, 0.15  )',
        }
      }>

        <p className='text-center text-2xl'>Sign In</p>
        <CustomInput name={email} setName={setEmail} title='Username' containerStyle='my-4'/>
        <CustomInput name={password} setName={setPassword} title='Password' containerStyle='my-4' isPassword={true}/>
        <CustomButton handleClick={handleLogin} text='Sign In' isLoading={isLoading}/>
        {/*<p className="text-[#ff0000] mb-2">{error}</p>*/}
        <div className='flex flex-row gap-1'>
          <p>Don't have an account?</p>
          <Link to='/sign-up'>
            <p className='text-primary'>Sign Up</p>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default SignIn