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
      body: JSON.stringify({ password , username }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Ошибка при логине");
    }

    const data = await response.json();
    const token = data.auth_token;
    localStorage.setItem("authToken", token); // Сохранение токена
    return { success: true, token };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
};


const Login: React.FC = () => {

  const { setAuth } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState<string>(""); // username — строка
  const [password, setPassword] = useState<string>(""); // password — строка
  const [error, setError] = useState<string>(""); // error — строка
  const handleLogin = async (e: FormEvent) => {
    e.preventDefault(); // Останавливаем отправку формы
    setError(""); // Сбрасываем ошибку

    const result = await loginUser(username, password);
    if (result.success) {
      setAuth(true);
      navigate(from, { replace: true }); // Перенаправление после успешного входа

    } else {
      setError(result.error || "Ошибка логина");
    }
  };


  const from = location.state?.from?.pathname || '/'
  return (
    <div className='LoginBase'>
      <div>
        <form className='LoginWindow' onSubmit={handleLogin}>
          <div className='LoginText'>Войти на сайт</div>
          <input
            className='LoginInput'
            type='text'
            placeholder='Логин'
            value={username}
            onChange={(e) => setUsername(e.target.value)} // e.target.value — строка
            required
          />

          {/* Поле для пароля */}
          <input
            className='LoginInput'
            type='password'
            placeholder='Пароль'
            value={password}
            onChange={(e) => setPassword(e.target.value)} // e.target.value — строка
            required
          />
          <button className='LoginBtn' type={'submit'} >Войти</button>
          </form>
          </div>
    </div>
  )
}

export default Login