import { Route, Routes } from 'react-router-dom';
import Home from './pages/protected/Home';
import Navbar from './components/Navbar';
import Groups from './pages/protected/Groups';
import Attendance from './pages/protected/Attendance';
import CreateGroup from './pages/protected/CreateGroup'; // Імпортуємо компонент CreateGroup
import RootLayout from './pages/protected/RootLayout';
import SignIn from './pages/auth/SignIn';
import AuthLayout from './pages/auth/AuthLayout';

function App() {
  return (
    <div className='flex h-screen w-full'>
      <Routes>
        {/* Авторизаційний макет */}
        {/* <Route element={<AuthLayout />}>
          <Route path='/sign-in' element={<SignIn />} />
        </Route> */}

        {/* Основний макет */}
        <Route element={<RootLayout />}>
          <Route path='/' element={<Home />} />
          <Route path='/groups/:id' element={<Groups />} />
          <Route path='/attendance/:id' element={<Attendance />} />
          <Route path='/create-group' element={<CreateGroup />} /> {/* Додано маршрут */}
        </Route>
      </Routes>
    </div>
  );
}

export default App;
