import React, { useEffect, useState } from 'react';
import './Lobby.css';
import { useNavigate, useParams } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

//interface Player {
  //id: number;
  //username: string;
//}

interface Room {
  id: number;
  name: string;
  room_status: string;
  //players: Player[];
  master_token_id: string | null;
}

const Lobby: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // Получаем ID комнаты из URL
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [room, setRoom] = useState<Room | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRoom = async () => {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('Пользователь не авторизован');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/api/rooms/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`Ошибка: ${response.status}`);
        }

        const rooms = await response.json();
        const selectedRoom = rooms.find((room: { id: number }) => room.id === parseInt(id || '0', 10));

        if (!selectedRoom) {
          throw new Error('Комната не найдена');
        }

        setRoom(selectedRoom);
      } catch (err) {
        setError('Не удалось загрузить данные комнаты');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };


    fetchRoom();
    const interval = setInterval(fetchRoom, 10000); // Обновляем данные комнаты каждые 10 секунд

    return () => clearInterval(interval);
  }, [id]);

  const handleStartGame = () => {
    if (!room) return;

    // Проверяем, является ли текущий пользователь мастером
    const token = localStorage.getItem('authToken');
    if (token === room.master_token_id) {
      console.log('Начинаем игру!');
      // Здесь можно отправить запрос на начало игры
    } else {
      alert('Только мастер комнаты может начать игру!');
    }
  };

  const handleLeaveLobby = () => {
    console.log('Покидаем лобби');
    navigate('/'); // Перенаправляем на главную страницу
  };

  return (
    <div className="Lobby">
      {loading ? (
        <p>Загрузка...</p>
      ) : error ? (
        <p className="error">{error}</p>
      ) : room ? (
        <>
          <header className="lobby-header">
            <h1>Комната: {room.name}</h1>
            <p>Статус: {room.room_status}</p>
          </header>
          <div className="players-list">
            <h2>Игроки:</h2>
            {/* <ul> 
              {room.players.map((player) => (
                <li key={player.id}>{player.username}</li>
              ))}
            </ul>*/}
          </div>
          <div className="lobby-actions">
            <button
              className="btn start-game"
              onClick={handleStartGame}
              disabled={localStorage.getItem('authToken') !== room.master_token_id}
            >
              Начать игру
            </button>
            <button className="btn leave-lobby" onClick={handleLeaveLobby}>
              Покинуть лобби
            </button>
          </div>
        </>
      ) : (
        <p>Комната не найдена</p>
      )}
    </div>
  );
};

export default Lobby;
