import react from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Register from "./pages/Register"
import NotFound from "./pages/NotFound"
import Simulator from "./pages/Simulator"
import Home from "./pages/Home"
import BankLogin from "./pages/BankLogin"
import ProtectedRoute from "./components/ProtectedRoute"
import LoanStatusPage from "./pages/LoanStatusPage"


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


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Simulator/>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="/logout" element={<Logout/>}/>
        <Route path="/simulator" element={<Simulator/>}/>
        <Route path="/emprestimo" element={<Emprestimo/>}/>
        <Route path="/BankLogin" element={<BankLogin/>}/>
        <Route path="/Home" element= {<ProtectedRoute><Home/></ProtectedRoute>}/>
        <Route path="/loan_status" element={<ProtectedRoute><LoanStatusPage/></ProtectedRoute>}/>
        <Route path="*" element={<NotFound/>}></Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App