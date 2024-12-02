import React, { useState, useEffect } from 'react';
import './Main.css';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import Lobby from './Lobby';

interface Room {
  id: BigInteger;
  name: string;
  room_status: string;
}

const Main = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [rooms, setRooms] = useState<Room[]>([]); // Список комнат
  const [loading, setLoading] = useState<boolean>(true); // Состояние загрузки
  const [error, setError] = useState<string | null>(null); // Ошибка при запросе
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false); // Состояние для модального окна
  const [roomName, setRoomName] = useState<string>(''); // Название комнаты
  const [joinRoomName, setJoinRoomName] = useState<string>(''); // Название комнаты для присоединения
  const [isJoinModalOpen, setIsJoinModalOpen] = useState<boolean>(false); // Модальное окно для присоединения

  const handleOpenJoinModal = () => {
    setIsJoinModalOpen(true); // Открываем модальное окно для присоединения
  };

  const handleCloseJoinModal = () => {
    setIsJoinModalOpen(false); // Закрываем модальное окно для присоединения
    setJoinRoomName(''); // Сбрасываем ввод
  };

  const handleJoinRoomNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setJoinRoomName(e.target.value); // Обновляем название комнаты для присоединения
  };

  const handleJoinRoomSubmit = async () => {
    if (!joinRoomName) {
      setError('Введите название комнаты для присоединения');
      return;
    }

    const token = localStorage.getItem('authToken');
    if (!token) return;

    try {
      const response = await fetch(`http://localhost:8000/api/rooms/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token}`,
        },
      });

      if (response.ok) {
        const room = await response.json();
        const selectedRoom = rooms.find((room: { name: string }) => room.name === joinRoomName);
        if(selectedRoom){
          console.log('Комната найдена:', room);

          // Переход в комнату
          navigate(`lobby/${selectedRoom.id}`);
        }
      } else if (response.status === 404) {
        setError('Комната с таким названием не найдена');
      } else {
        setError('Ошибка при поиске комнаты');
      }
    } catch (err) {
      console.error('Ошибка при запросе комнаты:', err);
      setError('Произошла ошибка. Попробуйте позже.');
    };

    setIsJoinModalOpen(false); // Закрываем модальное окно
  };

  const handleCreateRoom = () => {
    setIsModalOpen(true); // Открываем модальное окно
  };

  const handleCloseModal = () => {
    setIsModalOpen(false); // Закрываем модальное окно
  };

  const handleRoomNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRoomName(e.target.value); // Обновляем название комнаты
  };

  const handleSubmitRoom = async () => {
    if (!roomName) {
      setError('Введите название комнаты');
      return;
    }
  
    const token = localStorage.getItem('authToken');
    if (!token) return;
  
    try {
      const response = await fetch('http://localhost:8000/api/create-room/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify({ name: roomName }),
      });
  
      if (response.ok) {
        setRoomName(''); // Сбрасываем поле для названия
        setIsModalOpen(false); // Закрываем модальное окно
          const selectedRoom = await response.json();
          const selectedRoomID = selectedRoom.id;
          navigate(`lobby/${selectedRoomID}`); // Используем шаблонные строки
          console.log('ID созданной комнаты:', selectedRoomID);
      }
    } catch (err) {
      console.error('Ошибка при создании комнаты:', err);
      setError('Ошибка при создании комнаты');
    }
  };
  
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

  
  const handleJoinRoom = () => {
    isAuthenticated ? console.log('Присоединиться к комнате') : navigate('/login');
  };

  return (
    <div className="MainBase">
      {/* Модальное окно */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            {/* Кнопка закрытия */}
            <button className="modal-close-button" onClick={handleCloseModal}>
              ×
            </button>
            <h2>Создать новую комнату</h2>
            <input
              type="text"
              placeholder="Введите название комнаты"
              value={roomName}
              onChange={handleRoomNameChange}
            />
            <div className="modal-actions">
              <button onClick={handleSubmitRoom}>Создать</button>
            </div>
            {error && <p className="error">{error}</p>}
          </div>
        </div>
      )}

      {isJoinModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="modal-close-button" onClick={handleCloseJoinModal}>
              ×
            </button>
            <h2>Присоединиться к комнате</h2>
            <input
              type="text"
              placeholder="Введите название комнаты"
              value={joinRoomName}
              onChange={handleJoinRoomNameChange}
            />
            <div className="modal-actions">
              <button onClick={handleJoinRoomSubmit}>Присоединиться</button>
            </div>
            {error && <p className="error">{error}</p>}
          </div>
        </div>
      )}


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
        <button className="btn join-room" onClick={handleOpenJoinModal}>
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
