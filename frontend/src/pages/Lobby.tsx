import React, { useEffect, useRef, useState } from "react";
import "./Lobby.css";
import { useNavigate, useParams } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import apiClient from "../apiClient";
import WebSocketService from "../Services/wsservice";
import { toast, ToastContainer } from "react-toastify";
interface Room {
  id: number;
  name: string;
  room_status: string;
}

const Lobby: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [room, setRoom] = useState<Room | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRoom = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await apiClient.get("/rooms/");
        const rooms = response.data;
        const selectedRoom = rooms.find(
          (room: { id: number }) => room.id === parseInt(id || "0", 10)
        );

        if (!selectedRoom) {
          throw toast.error("Комната не найдена");
        }

        setRoom(selectedRoom);
      } catch (err) {
        console.error(err);
        toast.error("Не удалось загрузить данные комнаты");
      } finally {
        setLoading(false);
      }
    };

    fetchRoom();
  }, [id]);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (!token || !id) return;

    const websocketUrl = `ws://localhost:8000/ws/room/${id}/?token=${token}`;
    const websocket = WebSocketService;
    websocket.connect(websocketUrl);

    websocket.getSocket()?.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
    
      if (message.type === "game_event") {
        console.log("Получено событие игры:", message.message);
        if (message.message === "Game started!") {
          console.log("Ожидаем данные о поле (room_data)...");
        }
      } else if (message.type === "room_data") {
        console.log("Получен room_data:", message.data);
        sessionStorage.setItem("gameData", JSON.stringify(message.data));
    
        navigate(`/field/${id}`);
      } else {
        console.log("Получено сообщение от WebSocket:", message);
      }
    });

    return () => {
      // Здесь закрывать соединение НЕ нужно
    };
  }, [id, navigate]);

  const handleStartGame = () => {
   /* if (room?.room_status !== "Waiting") {
      alert("Игра уже началась или завершена!");
      return;
    }*/
    WebSocketService.send({ action: "start_game" });
  };

  const handleLeaveLobby = () => {
    console.log("Покидаем лобби");
    WebSocketService.close();
    navigate("/");
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
          <div className="lobby-actions">
            <button
              className="btn start-game"
              onClick={handleStartGame}
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