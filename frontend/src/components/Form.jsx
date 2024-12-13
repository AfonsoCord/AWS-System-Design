import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN, USERNAME} from "../constants";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";

function Form({ method }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [photo, setPhoto] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const name = method === "login" ? "Login" : "Register";

    const handlePhotoChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setPhoto(e.target.files[0]);
        }
    };

    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();

        const formData = new FormData();
        if (method === "login") {
            if (photo) {
                formData.append("photo", photo);
            } else {
                alert("Please upload a photo.");
                setLoading(false);
                return;
            }
        } else {
            formData.append("username", username);
            formData.append("password", password);
        }

        try {
            const res = await api.post('/login/', formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            if (method === "login") {
                localStorage.setItem(ACCESS_TOKEN, res.data.access_token);
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh_token);
                localStorage.setItem(USERNAME, res.data.username)
                navigate("/Home");
            } else {
                navigate("/login");
            }
        } catch (error) {
            if (error.response?.status === 400) {
                alert(error.response.data.message || "Login failed. Please try again.");
                window.location.reload();
            } else {
                alert(error.response?.data?.message || "An error occurred.");
        }} finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            <h1>{name}</h1>
            {method === "login" ? (
                <>
                    <input
                        className="form-input"
                        type="file"
                        accept="image/*"
                        onChange={handlePhotoChange}
                    />
                </>
            ) : (
                <>
                    <input
                        className="form-input"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Username"
                    />
                    <input
                        className="form-input"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                    />
                </>
            )}
            {loading && <LoadingIndicator />}
            <button className="form-button" type="submit">
                {name}
            </button>
        </form>
    );
}

export default Form;