import useAuth from '../hooks/useAuth';
import { useLocation, useNavigate } from 'react-router-dom';
import './Login.css'
import React, { useState, FormEvent } from "react";

const loginUser = async (username: string, password: string) => {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/auth/token/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ password, username }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Ошибка при логине");
    }

    const data = await response.json();
    const token = data.auth_token;
    localStorage.setItem("authToken", token);
    return { success: true, token };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
};

const registerUser = async (username: string, password: string, email: string) => {
  try {
    console.log(JSON.stringify({ email, username, password }));
    const response = await fetch("http://127.0.0.1:8000/api/auth/users/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, username, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Ошибка при регистрации");
    }

    const data = await response.json();
    return { success: true};
  } catch (error: any) {
    return { success: false, error: error.message };
  }
};

const Login: React.FC = () => {
  const { setAuth } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [isRegistering, setIsRegistering] = useState<boolean>(false); // Состояние для переключения режима
  const [email, setEmail] = useState<string>("");

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    if (isRegistering) {
      // Логика для регистрации
      console.log("Режим регистрации");
      const result = await registerUser(username, password, email);
      if (result.success) {
        setIsRegistering(false); // Например, перенаправление на страницу приветствия
      } else {
        setError(result.error || "Ошибка регистрации");
      }
    } else {
      const result = await loginUser(username, password);
      if (result.success) {
        setAuth(true);
        navigate(from, { replace: true });
      } else {
        setError(result.error || "Ошибка логина");
      }
    }
  };

  const handleRegisterClick = () => {
    console.log("Перед переключением:", isRegistering); // Вывод текущего значения
    setIsRegistering(!isRegistering); // Переключаем состояние
    console.log("После переключения:", !isRegistering); // Вывод нового значения
  };

  const from = location.state?.from?.pathname || '/';

  return (
    <div className="LoginBase">
      <div>
        <form className="LoginWindow" onSubmit={handleLogin}>
          <div className="LoginText">Войти на сайт</div>
          <input
            className="LoginInput"
            type="text"
            placeholder="Логин"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            className="LoginInput"
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          
          {isRegistering && (
            <input
              className="LoginInput"
              type="email"
              placeholder="Электронная почта"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          )}

          <button className="LoginBtn" type={"submit"}>
            {isRegistering ? "Зарег." : "Войти"}
          </button>

          <button
            type="button"
            className="RegisterBtn"
            onClick={handleRegisterClick}
          >
            {isRegistering ? "Уже есть аккаунт? Войти" : "Регистрация"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
