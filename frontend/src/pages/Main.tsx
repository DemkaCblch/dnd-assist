import React, { useState, useEffect } from 'react';
import './Main.css';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

interface Room {
  name: string;
  room_status: string;
}

const Main = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [rooms, setRooms] = useState<Room[]>([]); // Список комнат
  const [loading, setLoading] = useState<boolean>(true); // Состояние загрузки
  const [error, setError] = useState<string | null>(null); // Ошибка при запросе

  const mergeRooms = (newRooms: Room[]) => {
    const updatedRooms = [...rooms];
  
    newRooms.forEach((newRoom) => {
      const index = updatedRooms.findIndex((room) => room.name === newRoom.name);
      if (index >= 0) {
        updatedRooms[index] = newRoom; // Обновляем существующую комнату
      } else {
        updatedRooms.push(newRoom); // Добавляем новую комнату
      }
    });
  
    setRooms(updatedRooms);
  };
  
  useEffect(() => {
    const fetchRooms = async () => {
      const token = localStorage.getItem('authToken');
      if (!token) return;
  
      try {
        const response = await fetch('http://localhost:8000/api/rooms/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${token}`,
          },
        });
  
        if (response.ok) {
          const data = await response.json();
          mergeRooms(data); // Обновляем список через слияние
        }
      } catch (err) {
        console.error('Ошибка обновления комнат:', err);
      }
    };
  
    fetchRooms();
    const interval = setInterval(fetchRooms, 10000);
  
    return () => clearInterval(interval);
  }, []);

  const handleCreateRoom = () => {
    isAuthenticated ? console.log('Создать комнату') : navigate('/login');
  };

  const handleJoinRoom = () => {
    isAuthenticated ? console.log('Присоединиться к комнате') : navigate('/login');
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
        {error ? (
          <p className="error">{error}</p>
        ) : rooms.length > 0 ? (
          <ul>
            {rooms.map((room, index) => (
              <li key={index}>
                <strong>{room.name}</strong> - {room.room_status}
              </li>
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
