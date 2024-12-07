import react from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Register from "./pages/Register"
import Home from "./pages/Home"
import NotFound from "./pages/NotFound"
import ProtectedRoute from "./components/ProtectedRoute"

function Logout() {
  localStorage.clear()
  return <Navigate to="/login" />
}

function RegisterAndLogout() {
  localStorage.clear()
  return <Register />
}

function Emprestimo() {
  return <Navigate to="/emprestimo" />
}

function Simulacao() {
  return <Navigate to="/simulacao" />
}


function App() {
  return (
    <>
      <h1> Simulacao de empréstimo </h1>

      <div>
        <input type="number" placeholder="Valor do Empréstimo"/>
        <input type="number" placeholder="Duração do Empréstimo"/>
        <input type="number" placeholder="Duração do Empréstimo"/>
        <button> Simular </button>
      </div>
    </>
  )
}

export default App