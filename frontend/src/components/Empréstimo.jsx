import { useState } from "react";
import api from "../api";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN} from "../constants";

function Loan({ route }) {
    const [valor, setvalor] = useState("");
    const [duracao, setduracao] = useState("");
    const [salario, setsalario] = useState("");
    const [profissao, setprofissao] = useState("");
    const [documentos, setdocumentos] = useState("");
    const [tiposempr, settiposempr] = useState("");
    const [estado, setestado] = useState("por resolver");


    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        console.log({ valor, duracao, salario, profissao, tiposempr,estado,documentos });
        e.preventDefault();
        setLoading(true);
        setError("");  // Resetando o erro ao tentar submeter

        if (localStorage.getItem(ACCESS_TOKEN)) {
            return navigate("/Home");  
        }

        // Validação para garantir que os campos não estão vazios
        if (!valor || !duracao || !salario || !profissao || !tiposempr) {
            setError("Por favor, preencha todos os campos obrigatórios.");
            setLoading(false);
            return;
        }

        const loanData = {
            valor: parseFloat(valor),
            duracao: parseInt(duracao),
            salario: parseInt(salario),
            profissao: profissao.toLowerCase(),
            documentos: documentos,
            tiposempr: tiposempr,
            estado: estado

        };

        try {
            const response = await api.post("/Home/", loanData, {
                headers: {
                    "Content-Type": "application/json",
                },
            });
            
            navigate("/Home");  // Navega para Home

        } catch (error) {
            alert(error.response?.data?.message || "An error occurred.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            <h1>Página do Empréstimo</h1>
            <input
                className="form-input"
                type="number"
                value={valor}
                onChange={(e) => setvalor(e.target.value)}
                placeholder="Quantia do empréstimo"
                required
            />
            <input
                className="form-input"
                type="number"
                value={duracao}
                onChange={(e) => setduracao(e.target.value)}
                placeholder="Duração do empréstimo"
                required
            />
            <input
                className="form-input"
                type="number"
                value={salario}
                onChange={(e) => setsalario(e.target.value)}
                placeholder="Insira o seu salário mensal"
                required
            />
            <input
                className="form-input"
                type="text"
                value={profissao}
                onChange={(e) => setprofissao(e.target.value)}
                placeholder="Insira a sua profissão"
                required
            />
            <input
                className="form-input"
                type="file"
                onChange={(e) => setdocumentos(e.target.files[0])}
                accept="image/*"
                required
            />

            <select
                className="form-input"
                value={tiposempr}
                onChange={(e) => settiposempr(e.target.value)}
                required
            >
                <option value="">Selecione o Tipo de Empréstimo</option>
                <option value="CHAB">Crédito Habitacional</option>
                <option value="CAUT">Crédito Automotivo</option>
                <option value="CEST">Crédito Estudantil</option>
                <option value="CPES">Crédito Pessoal</option>
            </select>

            {error && <p style={{ color: "red" }}>{error}</p>}
            {loading && <LoadingIndicator />}

            <button
                className="form-button"
                type="submit"
                disabled={loading}
            >
                {loading ? "Enviando..." : "Enviar"}
            </button>
        </form>
    );
}

export default Loan;