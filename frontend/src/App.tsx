import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

// Import your page components
import HomePage from './pages/HomePage';
// import AboutPage from './pages/AboutPage';
// import ContactPage from './pages/ContactPage';

function App() {
  // const [count, setCount] = useState(0)

  return (
    <Router>
      <div className="min-h-screen bg-black">
        {/* Navbar */}
        <nav className="flex justify-center bg-slate-800 h-8 align-middle">
          <Link className="mx-4 text-white" to="/">Home</Link>
          <Link className="mx-4 text-white" to="/about">About</Link>
          <Link className="mx-4 text-white" to="/contact">Contact</Link>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/*
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
          */}
        </Routes>
      </div>
    </Router>
    /*
    <div className="min-h-screen bg-gradient-to-b from-white to-black">
      <div className="flex justify-center align-middle bg-slate-500 h-8">
        <a></a>

      </div>
      <div className="flex justify-center align-middle">
        <a className="flex justify-center align-middle" href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </div>
    */
  )
}

export default App
