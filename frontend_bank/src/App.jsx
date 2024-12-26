import react from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import BankLogin from "./pages/BankLogin"
import Home from "./pages/Home"
import NotFound from "./pages/NotFound"
import ProtectedRoute from "./components/ProtectedRoute"
import LoanStatusPage from "./pages/LoanStatusPage"

function Logout() {
  localStorage.clear()
  return <Navigate to="/BankLogin"/>
}


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<BankLogin/>}/>
        <Route path="/logout" element={<Logout/>}/>
        <Route path="/BankLogin" element={<BankLogin/>}/>
        <Route path="/Home" element= {<ProtectedRoute><Home/></ProtectedRoute>}/>
        <Route path="/loan_status_funcionarios" element={<LoanStatusPage/>}/>
        <Route path="*" element={<NotFound/>}></Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App