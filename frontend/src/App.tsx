import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import './App.css'

import HomePage from './pages/HomePage';
import Login from './pages/Login';
import { useAppSelector } from './redux/store';
import SignUp from './pages/SignUp';
import Navbar from './components/navbar';

function App() {
  const user = useAppSelector(state => state.user.user);

  return (
    <Router>
      <div className="min-h-screen bg-white">
        <Navbar />
        <Routes>
          <Route path='/login' element={!user ? <Login /> : <Navigate to='/' />} />
          <Route path='/' element={!user ? <Login /> : <Navigate to='/' />} />
          <Route path='/signup' element={!user ? <SignUp /> : <Navigate to='/' />} />
          <Route path='/home' element={user ? <HomePage /> : <Navigate to='/login' />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
