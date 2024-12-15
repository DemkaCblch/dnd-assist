import React, { useState, useEffect } from 'react';
import './Main.css';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import Lobby from './Lobby';
import apiClient from '../apiClient';

interface Room {
  id: BigInteger;
  name: string;
  room_status: string;
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

 /* const handleJoinRoomSubmit = async () => {
    if (!joinRoomName) {
      setError('Введите название комнаты для присоединения');
      return;
    }

    try {
      const response = await apiClient.get('rooms/');
      const selectedRoom = response.data.find((room: Room) => room.name === joinRoomName);

      if (selectedRoom) {
        console.log('Комната найдена:', selectedRoom);
        navigate(`lobby/${selectedRoom.id}`);
      } else {
        setError('Комната с таким названием не найдена');
      }
    } catch (err) {
      console.error('Ошибка при запросе комнаты:', err);
      setError('Произошла ошибка. Попробуйте позже.');
    } finally {
      setIsJoinModalOpen(false);
    }
  }; */

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
  
    try {
      const response = await apiClient.post('create-room/', { name: roomName });
      setRoomName('');
      setIsModalOpen(false);
      const selectedRoomID = response.data.id;
      console.log('ID созданной комнаты:', selectedRoomID);
  
      // Подключение к WebSocket после создания комнаты
     /* const token = localStorage.getItem('authToken');
      if (token) {
        const ws = new WebSocket(`ws://localhost:8000/ws/room/${selectedRoomID}/?token=${token}`);
        ws.onopen = () => console.log('WebSocket соединение установлено для комнаты:', selectedRoomID);
        ws.onerror = (error) => console.error('Ошибка WebSocket:', error);
        ws.onclose = () => console.log('WebSocket соединение закрыто');
      }*/
      apiClient.post(`connect-room/${selectedRoomID}/`)
      navigate(`lobby/${selectedRoomID}`);
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
      try {
        const response = await apiClient.get('rooms/');
        mergeRooms(response.data);
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
    try {
      const { data } = await apiClient.get(`rooms/${roomId}/is_master/`);
  
      if (data.is_master) {

        const token = localStorage.getItem('authToken');
       await apiClient.post(`connect-room/${roomId}/`);
        navigate(`lobby/${roomId}`);
      } else {
        const response = await apiClient.get('get-character/');
        setCharacters(response.data);
        setSelectedRoomId(roomId);
        setIsCharacterModalOpen(true);
      }
    } catch (err) {
      console.error('Ошибка при проверке статуса мастера или загрузке персонажей:', err);
    }
  };
  
  

  const joinRoomWithCharacter = async () => {
    if (!selectedCharacterId || !selectedRoomId) return;
  
    try {
      const response = await apiClient.post(`connect-room/${selectedRoomId}/`, {
        character_id: selectedCharacterId,
      });
  
      if (response.status === 200) {
        setIsCharacterModalOpen(false);
  
        // Подключение к WebSocket после присоединения к комнате
        const token = localStorage.getItem('authToken');
        if (token) {
          /*const ws = new WebSocket(`ws://localhost:8000/ws/room/${selectedRoomId}/?token=${token}`);
          ws.onopen = () => console.log('WebSocket соединение установлено для комнаты:', selectedRoomId);
          ws.onerror = (error) => console.error('Ошибка WebSocket:', error);
          ws.onclose = () => console.log('WebSocket соединение закрыто');*/
        }
  
        navigate(`lobby/${selectedRoomId}`);
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

      {/* {isJoinModalOpen && (
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
      )}  */}

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
        {/*<button className="btn join-room" onClick={handleOpenJoinModal}>
          Присоединиться к комнате
        </button>*/}
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
