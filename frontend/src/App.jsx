import react from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Register from "./pages/Register"
import NotFound from "./pages/NotFound"
import Simul from "./pages/simular"
import Home from "./pages/Home"
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
  return <Simul />
}


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Simulacao/>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="/logout" element={<Logout/>}/>
        <Route path="/simulacao" element={<Simulacao/>}/>
        <Route path="/emprestimo" element={<Emprestimo/>}/>
        <Route path="*" element={<NotFound/>}></Route>
        <Route path="/Home" element= {<ProtectedRoute><Home/></ProtectedRoute>}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App