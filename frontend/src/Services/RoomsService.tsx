
import { Room } from "../entities/Room";

export class RoomService {
  private static API_BASE_URL = "http://localhost:8000/api";

  static async fetchRooms(authToken: string): Promise<Room[]> {
    const response = await fetch(`${this.API_BASE_URL}/rooms/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${authToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("Ошибка при получении списка комнат");
    }

    const data = await response.json();
    return data.map((room: any) => new Room(room.id, room.name, room.room_status, room.master_token));
  }

  static async createRoom(authToken: string, roomName: string): Promise<Room> {
    const response = await fetch(`${this.API_BASE_URL}/create-room/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${authToken}`,
      },
      body: JSON.stringify({ name: roomName }),
    });

    if (!response.ok) {
      throw new Error("Ошибка при создании комнаты");
    }

    const data = await response.json();
    return new Room(data.id, data.name, data.room_status, data.master_token);
  }

  static async joinRoom(authToken: string, roomId: BigInteger, characterId: number): Promise<void> {
    const response = await fetch(`${this.API_BASE_URL}/connect-room/${roomId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${authToken}`,
      },
      body: JSON.stringify({ character_id: characterId }),
    });

    if (!response.ok) {
      throw new Error("Ошибка при присоединении к комнате");
    }
  }
}
