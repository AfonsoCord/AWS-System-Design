import { useState } from "react";
import api from "../api";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, DURACAO, VALOR, USERNAME } from "../constants";

function Loan({ route }) {
    const [valor, setvalor] = useState(localStorage.getItem(VALOR) || "");
    const [duracao, setduracao] = useState(localStorage.getItem(DURACAO) || "");
    const [salario, setsalario] = useState("");
    const [profissao, setprofissao] = useState("");
    const [documentos, setdocumentos] = useState("");
    const [tiposempr, settiposempr] = useState("");
    const [estado, setestado] = useState("por resolver");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [isSubmitted, setIsSubmitted] = useState(false); // Estado para controlar se o formulário foi enviado
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        if (!valor || !duracao || !salario || !profissao || !tiposempr) {
            setError("Por favor, preencha todos os campos obrigatórios.");
            setLoading(false);
            return;
        }

        const loanData = {
            user: localStorage.getItem(USERNAME),
            valor: parseFloat(valor),
            duracao: parseInt(duracao),
            salario: parseInt(salario),
            profissao: profissao.toLowerCase(),
            documentos: documentos,
            tiposempr: tiposempr,
            estado: estado,
        };

        const access = localStorage.getItem(ACCESS_TOKEN);

        if (access) {
            try {
                const response = await api.post("/Home/", loanData, {
                    headers: {
                        Authorization: `Bearer ${access}`,
                        "Content-Type": "multipart/form-data",
                    },
                });
                alert(response.data?.message || "O seu empréstimo vai ser processado!");
                setIsSubmitted(true); // Indica que o formulário foi enviado com sucesso
            } catch (error) {
                console.error(error.response?.data || error.message);
                alert(error.response?.data?.message || "Ocorreu um erro.");
            } finally {
                setLoading(false);
            }
        }
    };

    const handleLoanStatus = () => {
        navigate("/loan_status");
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

            <button className="form-button" type="submit" disabled={loading}>
                {loading ? "Enviando..." : "Enviar"}
            </button>

            {/* Exibe o botão apenas se o formulário foi enviado */}
            {isSubmitted && (
                <button
                    type="button"
                    className="form-button"
                    onClick={handleLoanStatus}
                >
                    Ver estado dos seus empréstimos
                </button>
            )}
        </form>
    );
}

export default Loan;
