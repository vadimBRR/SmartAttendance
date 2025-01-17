import { Eye, EyeClosed } from 'lucide-react'
import React, { useState } from 'react'
type Props  = {
  name: string,
  setName: React.Dispatch<React.SetStateAction<string>>
  title?:string
  containerStyle?:string
  isPassword?:boolean
  inputStyle?:string
}

const CustomInput = ({name, setName,title='',containerStyle='', isPassword, inputStyle}: Props) => {
  const [isPasswordVisible, setPasswordVisible] = useState(false)

  return (
    <div className={`${containerStyle} `}>
      {title && <p className='text-xl mb-1'>{title}</p>}
      <div className=''>
        <input name={name} onChange={(e)=>setName(e.currentTarget.value)} className={`bg-[#aaaaaa]/50 text-xl px-2 py-1 rounded-lg border border-[#ffffff]/20 ${inputStyle}`} type={isPassword ? (isPasswordVisible ? 'text' : 'password') : 'text'} />
        {isPassword && <div className='flex flex-row gap-1 mt-2'>
          <input type='checkbox' checked={isPasswordVisible} onChange={(e)=>setPasswordVisible(e.currentTarget.checked)}/>
          <p className='text-base'>{isPasswordVisible ? 'Hide Password' : 'Show Password'}</p>
          </div>}
      </div>
      
    </div>
  )
}

export default CustomInput