import React, { useState, useEffect } from 'react';
import './Main.css';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import Lobby from './Lobby';

interface Room {
  id: BigInteger;
  name: string;
  room_status: string;
  master_token: string;
}

const Main = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [rooms, setRooms] = useState<Room[]>([]); 
  const [error, setError] = useState<string | null>(null); //
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [roomName, setRoomName] = useState<string>(''); //
  const [joinRoomName, setJoinRoomName] = useState<string>(''); // 
  const [isJoinModalOpen, setIsJoinModalOpen] = useState<boolean>(false); //  
  const [hoveredRoomId, setHoveredRoomId] = useState<BigInteger | null>(null);
  const [selectedRoomId, setSelectedRoomId] = useState<BigInteger | null>(null);
  const [characters, setCharacters] = useState<any[]>([]); // Список персонажей пользователя
  const [isCharacterModalOpen, setIsCharacterModalOpen] = useState<boolean>(false); // Статус окна выбора персонажей
  const [selectedCharacterId, setSelectedCharacterId] = useState<number | null>(null); // Выбранный персонаж




  const handleOpenJoinModal = () => {
    setIsJoinModalOpen(true); //
  };

  const handleCloseJoinModal = () => {
    setIsJoinModalOpen(false); //   
    setJoinRoomName(''); // 
  };

  const handleJoinRoomNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setJoinRoomName(e.target.value); 
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

    setIsJoinModalOpen(false); 
  };

  const handleCreateRoom = () => {
    setIsModalOpen(true); 
  };

  const handleCloseModal = () => {
    setIsModalOpen(false); 
  };

  const handleRoomNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRoomName(e.target.value); 
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
        setRoomName(''); 
        setIsModalOpen(false); //
          const selectedRoom = await response.json();
          const selectedRoomID = selectedRoom.id;
          navigate(`lobby/${selectedRoomID}`); 
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
        updatedRooms[index] = newRoom; 
      } else {
        updatedRooms.push(newRoom); 
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
          mergeRooms(data); 
        }
      } catch (err) {
        console.error('Ошибка обновления комнат:', err);
      }
    };
  
    fetchRooms();
    const interval = setInterval(fetchRooms, 10000);
  
    return () => clearInterval(interval);
  }, []);


  const handleRoomClick = (roomId: BigInteger) => {
    setSelectedRoomId(selectedRoomId === roomId ? null : roomId);
  };
  const openCharacterModal = async (roomId: BigInteger) => {
    const token = localStorage.getItem('authToken');
    const room = rooms.find((room) => room.id === roomId);
    if (!token) return;
  
    try {
      const response = await fetch('http://localhost:8000/api/get-character/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token}`,
        },
      });
  
      if (response.ok) {
        if (room && token === room.master_token) {
          // Если пользователь мастер комнаты, сразу направляем в комнату
          navigate(`lobby/${roomId}`);
        } else {
        const data = await response.json();
        setCharacters(data); // Устанавливаем список персонажей
        setSelectedRoomId(roomId); // Устанавливаем текущую комнату
        setIsCharacterModalOpen(true); // Открываем окно
        }
      }
    } catch (err) {
      console.error('Ошибка при загрузке персонажей:', err);
    }
  };

  const joinRoomWithCharacter = async () => {
    if (!selectedCharacterId || !selectedRoomId) return;
  
    const token = localStorage.getItem('authToken');
    if (!token) return;
  
    try {
      const response = await fetch(`http://localhost:8000/api/connect-room/${selectedRoomId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify({ character_id: selectedCharacterId }),
      });
  
      if (response.ok) {
        setIsCharacterModalOpen(false); // Закрываем окно
        navigate(`lobby/${selectedRoomId}`); // Переход в лобби
      } else {
        console.error('Ошибка при присоединении к комнате');
      }
    } catch (err) {
      console.error('Ошибка при отправке запроса:', err);
    }
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

      {isCharacterModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="modal-close-button" onClick={() => setIsCharacterModalOpen(false)}>
              ×
            </button>
            <h2>Выберите персонажа</h2>
            {characters.length > 0 ? (
              <ul>
                {characters.map((character) => (
                  <li
                    key={character.id}
                    onClick={() => setSelectedCharacterId(character.id)}
                    style={{
                      cursor: 'pointer',
                      margin: '10px 0',
                      padding: '5px',
                      backgroundColor: selectedCharacterId === character.id ? '#4CAF50' : '#f1f1f1',
                      color: selectedCharacterId === character.id ? 'white' : 'black',
                      borderRadius: '5px',
                    }}
                  >
                    {character.name} (Уровень: {character.character_stats.level})
                  </li>
                ))}
              </ul>
            ) : (
              <p>Нет доступных персонажей</p>
            )}
            <button
              onClick={joinRoomWithCharacter}
              style={{
                marginTop: '10px',
                padding: '10px 20px',
                backgroundColor: '#4CAF50',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
              disabled={!selectedCharacterId}
            >
              Присоединиться
            </button>
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
            {rooms.map((room) => (
              <li
                key={room.id.toString()}
                onClick={() => handleRoomClick(room.id)}
                className="room-item"
                style={{ cursor: 'pointer', marginBottom: '10px' }}
              >
                <div>
                  <strong>{room.name}</strong> - {room.room_status}
                </div>
                {selectedRoomId === room.id && (
                  <button
                    className="join-room-button"
                    onClick={() => openCharacterModal(room.id)}
                    style={{
                      marginTop: '5px',
                      padding: '5px 10px',
                      backgroundColor: '#4CAF50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer',
                    }}
                  >
                    Присоединиться
                  </button>
                )}

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
