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
	login: (email: string, password: string) => Promise<void>
	register: (email: string, password: string) => Promise<void>
	logout: () => void
	isLoading: boolean
	error: string | null
  email: string | null
  isTeacher: boolean | null
  userId: string | null

  
}
const AuthContext = createContext<AuthContextType>({
	token: null,
	login: async () => {},
	register: async () => {},
	logout: () => {},
	isLoading: false,
	error: null,
  email: null,
  isTeacher: null,
  userId: null
})

export const AuthProvider = ({ children }: PropsWithChildren) => {
  const [email, setEmail] = useState<string | null>(localStorage.getItem('email'));
  const [isTeacher, setIsTeacher] = useState<boolean | null>(JSON.parse(localStorage.getItem('isTeacher') || 'false'));
  const [userId, setUserId] = useState<string | null>(localStorage.getItem('userId'));

	const [token, setToken] = useState(localStorage.getItem('token'))
	const [isLoading, setIsLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)
	const navigate = useNavigate()
	console.log("OPEEEEENNNN")

	const login = async (email: string, password: string) => {
    console.log("here");
    setIsLoading(true);
    setError(null);
    try {
        const data = await useLogin(email, password);
        console.log(data);
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('email', data.email);
        setToken(data.access_token);
        setEmail(email);

        try {
            const { isTeacher, id } = await verifyUserRole(data.email);
            localStorage.setItem('isTeacher', isTeacher.toString());
            localStorage.setItem('userId', id.toString());
            setIsTeacher(isTeacher);
            setUserId(id);
            console.log("isTeacher", isTeacher);
            console.log("id", id);
        } catch (verifyError: any) {
            if (verifyError.message.includes("Error verifying user role")) {
                console.log("Internal Server Error during role verification");
                localStorage.setItem('isTeacher', 'false');
                localStorage.setItem('userId', '-1');
                console.log("Dont exist");
                setIsTeacher(false);
            } else {
                throw verifyError; 
            }
        }

        navigate('/');
    } catch (error: any) {
        setError(error.message || 'Authentication failed');
    } finally {
        setIsLoading(false);
    }
};


const verifyUserRole = async (email: string) => {
    const response = await fetch(`http://147.232.205.226:8000/verify-email/teacher?email=${email}`);
    if (!response.ok) {
        throw new Error("Error verifying user role");
    }
    return await response.json();
};



	const register = async (email: string, password: string) => {
		setIsLoading(true)
		setError(null)
		try {
			await useRegister(email, password)
			await login(email, password)
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
			value={{ token, login, register, logout, isLoading, error,email, isTeacher, userId }}
		>
			{children}
		</AuthContext.Provider>
	)
}

export const useAuth = () => {
	return useContext(AuthContext)
}