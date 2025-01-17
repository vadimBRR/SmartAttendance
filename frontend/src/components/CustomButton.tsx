import React from 'react'

type Props={
  handleClick: () => void
  text: string
  buttonStyle?: string
  textStyle?: string
  disabled?: boolean
  isLoading?: boolean
}
const CustomButton = ({handleClick, text, buttonStyle='', textStyle='', disabled=false, isLoading=false}:Props) => {
  return (
      <button onClick={handleClick} className={`bg-primary text-xl px-2 py-1 rounded-lg border border-[#ffffff]/20 ${buttonStyle} w-full`} disabled={disabled || isLoading}>
        <p className={`text-base ${textStyle}`}>{isLoading ? 'Loading...' : text}</p>
      </button>
  )
}

export default CustomButton