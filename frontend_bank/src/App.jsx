import react from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import BankLogin from "./pages/BankLogin"
import Home from "./pages/Home"
import NotFound from "./pages/NotFound"
import ProtectedRoute from "./components/ProtectedRoute"

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
        <Route path="*" element={<NotFound/>}></Route>
        <Route path="/Home" element= {<ProtectedRoute><Home/></ProtectedRoute>}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App