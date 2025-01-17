import {
	createContext,
	PropsWithChildren,
	useContext,
	useEffect,
	useState,
} from 'react'
import { useNavigate } from 'react-router-dom'
import { useLogin, useVerifyToken, useRegister } from '../api'

type AuthContextType = {
	token: string | null
	login: (username: string, password: string) => Promise<void>
	register: (username: string, password: string) => Promise<void>
	logout: () => void
	isLoading: boolean
	error: string | null
  username: string | null
  
}
const AuthContext = createContext<AuthContextType>({
	token: null,
	login: async () => {},
	register: async () => {},
	logout: () => {},
	isLoading: false,
	error: null,
  username: null
})

export const AuthProvider = ({ children }: PropsWithChildren) => {
  const [username, setUsername] = useState<string | null>(localStorage.getItem('username'));
	const [token, setToken] = useState(localStorage.getItem('token'))
	const [isLoading, setIsLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)
	const navigate = useNavigate()

	const login = async (username: string, password: string) => {
    console.log("here");
		setIsLoading(true)
		setError(null)
		try {
      console.log("here");
			const data = await useLogin(username, password)
      console.log(data);
      console.log(data);
			localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', data.username);
			setToken(data.access_token)
      setUsername(username)
			navigate('/')
		} catch (error: any) {
			setError(error.message || 'Authentication failed')
		} finally {
			setIsLoading(false)
		}
	}


	const register = async (username: string, password: string) => {
		setIsLoading(true)
		setError(null)
		try {
			await useRegister(username, password)
			await login(username, password)
		} catch (error: any) {
			setError(error.message || 'Registration failed')
		} finally {
			setIsLoading(false)
		}
	}

	const logout = () => {
		localStorage.removeItem('token')
		setToken(null)
		navigate('/')
	}

	const verifyToken = async () => {
		try {
			await useVerifyToken(token as string)
		} catch (error) {
			logout()
		}
	}

	useEffect(() => {
		if (token) {
			verifyToken()
		}
	}, [token])

	return (
		<AuthContext.Provider
			value={{ token, login, register, logout, isLoading, error,username }}
		>
			{children}
		</AuthContext.Provider>
	)
}

export const useAuth = () => {
	return useContext(AuthContext)
}