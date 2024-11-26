import React, { useState, useEffect } from 'react';
import './Main.css';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

const Main = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const [rooms, setRooms] = useState<string[]>([]); // Список комнат
  const [ws, setWs] = useState<WebSocket | null>(null); // Хранение WebSocket-соединения

  useEffect(() => {
    // Устанавливаем соединение WebSocket
    const token = localStorage.getItem('authToken'); // Предполагаем, что токен хранится в localStorage
    const wsUrl = `ws://localhost:8000/ws/rooms/?token=${token}`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => console.log('WebSocket соединение установлено');
    socket.onmessage = (event) => {
      try {
          const data = JSON.parse(event.data);
          if (data.rooms) {
              setRooms(data.rooms); // Обновляем список комнат
          }
      } catch (error) {
          console.error('Ошибка обработки WebSocket данных:', error);
      }
  };
  
  socket.onerror = (error) => {
    console.error('WebSocket ошибка:', error);
  };
  socket.onclose = (event) => {
    console.warn('WebSocket закрыт:', event);
  };
  

    setWs(socket);

    // Закрываем соединение при размонтировании
    return () => {
      socket.close();
    };
  }, []);

  const handleCreateRoom = () => {
    isAuthenticated ? console.log("Создать комнату") : navigate('/login');
  };

  const handleJoinRoom = () => {
    isAuthenticated ? console.log("Присоединиться к комнате") : navigate('/login');
  };

  return (
    <div className="MainBase">
      <header className="header">
        <h1 className="title">Добро пожаловать на D&D-Assist</h1>
        <p className="description">
          Создавайте и играйте в Dungeons & Dragons с друзьями онлайн. Быстро, удобно, увлекательно!
        </p>
      </header>
      <div className="buttons-container">
        <button className="btn create-room" onClick={handleCreateRoom}>
          Создать комнату
        </button>
        <button className="btn join-room" onClick={handleJoinRoom}>
          Присоединиться к комнате
        </button>
      </div>
      <div className="rooms-list">
        <h2>Доступные комнаты:</h2>
        {rooms.length > 0 ? (
          <ul>
            {rooms.map((room, index) => (
              <li key={index}>{room}</li>
            ))}
          </ul>
        ) : (
          <p>Нет доступных комнат</p>
        )}
      </div>
    </div>
  );
};

export default Main;
