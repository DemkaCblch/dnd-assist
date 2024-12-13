import React, { useState, useEffect } from "react";
import "./Characters.css";
import apiClient from "../apiClient";

interface CharacterStats {
  hp: number;
  race: string;
  level: number;
  intelligence: number;
  strength: number;
  dexterity: number;
  constitution: number;
  wisdom: number;
  resistance: number;
  stability: number;
  charisma: number;
}

interface Character {
  id: number;
  name: string;
  status: string;
  character_stats: CharacterStats;
}

interface UserProfile {
  username: string;
  date_joined: string;
}

const Profile = () => {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [newCharacter, setNewCharacter] = useState<Character>({
    id: 0,
    name: "",
    status: "Активен",
    character_stats: {
      hp: 100,
      race: "",
      level: 1,
      intelligence: 10,
      strength: 10,
      dexterity: 10,
      constitution: 10,
      wisdom: 10,
      resistance: 10,
      stability: 10,
      charisma: 10,
    },
  });

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (!token) return;

    const fetchUserProfile = async () => {
      try {
        const response = await apiClient.get("/profile/");
        setUserProfile(response.data);
      } catch (err) {
        console.error(err);
        setError("Ошибка при загрузке профиля");
      }
    };
  
    const fetchCharacters = async () => {
      try {
        const response = await apiClient.get("/get-character/");
        setCharacters(response.data);
      } catch (err) {
        console.error(err);
        setError("Ошибка при загрузке персонажей");
      }
    };
  
    fetchUserProfile();
    fetchCharacters();
  }, []);

  const handleCharacterClick = (character: Character) => {
    setSelectedCharacter(character);
  };

  const closeCharacterModal = () => {
    setSelectedCharacter(null);
  };

  const openCreateModal = () => {
    setIsCreateModalOpen(true);
  };

  const closeCreateModal = () => {
    setIsCreateModalOpen(false);
  };

  const handleCreateCharacter = async () => {
    try {
      const response = await apiClient.post("/create-character/", newCharacter);
      setCharacters([...characters, response.data]);
      closeCreateModal();
    } catch (err) {
      console.error(err);
      setError("Ошибка при создании персонажа");
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
  
    if (name in newCharacter.character_stats) {
      // Если поле числовое, преобразуем значение, иначе сохраняем как текст
      const isNumericField = ["hp", "level", "intelligence", "strength", "dexterity", "constitution", "wisdom", "resistance", "stability", "charisma"].includes(name);
  
      setNewCharacter((prev) => ({
        ...prev,
        character_stats: {
          ...prev.character_stats,
          [name]: isNumericField ? (value === "" ? "" : Number(value)) : value,
        },
      }));
    } else {
      setNewCharacter((prev) => ({
        ...prev,
        [name]: value, // Для обычных полей оставляем значение как есть
      }));
    }
  };
  
  

  return (
    <div className="profile">
      <h1>Личный кабинет</h1>
      {userProfile && (
        <div className="user-info">
          <p><strong>Имя пользователя:</strong> {userProfile.username}</p>
          <p><strong>Дата регистрации:</strong> {new Date(userProfile.date_joined).toLocaleDateString()}</p>
        </div>
      )}
      {error && <p className="error">{error}</p>}
      <button className="create-button" onClick={openCreateModal}>
        Создать персонажа
      </button>
      <div className="characters-list">
        {characters.length > 0 ? (
          characters.map((character) => (
            <div
              key={character.id}
              className="character-item"
              onClick={() => handleCharacterClick(character)}
            >
              <h2>{character.name}</h2>
              <p>Статус: {character.status}</p>
            </div>
          ))
        ) : (
          <p>У вас нет созданных персонажей</p>
        )}
      </div>

      {/* Модальное окно создания персонажа */}
      {isCreateModalOpen && (
        <div className="modal-overlay" onClick={closeCreateModal}>
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()} // Остановка всплытия события
          >
            <button className="modal-close-button" onClick={closeCreateModal}>
              ×
            </button>
            <h2>Создать персонажа</h2>
            <div className="character-stats">
              <label>
                Имя персонажа:
                <input
                  type="text"
                  name="name"
                  placeholder="Введите имя"
                  value={newCharacter.name}
                  onChange={handleChange}
                />
              </label>
              <label>
                HP:
                <input
                  type="number"
                  name="hp"
                  placeholder="Введите HP"
                  value={newCharacter.character_stats.hp}
                  onChange={handleChange}
                />
              </label>
              <label>
                Раса:
                 <input
                 type="text"
                 name="race"
                 placeholder="Введите расу"
                 value={newCharacter.character_stats.race}
                 onChange={handleChange}
               />
               
              </label>
              <label>
                Уровень:
                <input
                  type="number"
                  name="level"
                  placeholder="Введите уровень"
                  value={newCharacter.character_stats.level}
                  onChange={handleChange}
                />
              </label>
              <label>
                Интеллект:
                <input
                  type="number"
                  name="intelligence"
                  placeholder="Введите интеллект"
                  value={newCharacter.character_stats.intelligence}
                  onChange={handleChange}
                />
              </label>
              <label>
                Сила:
                <input
                  type="number"
                  name="strength"
                  placeholder="Введите силу"
                  value={newCharacter.character_stats.strength}
                  onChange={handleChange}
                />
              </label>
              <label>
                Ловкость:
                <input
                  type="number"
                  name="dexterity"
                  placeholder="Введите ловкость"
                  value={newCharacter.character_stats.dexterity}
                  onChange={handleChange}
                />
              </label>
              <label>
                Телосложение:
                <input
                  type="number"
                  name="constitution"
                  placeholder="Введите телосложение"
                  value={newCharacter.character_stats.constitution}
                  onChange={handleChange}
                />
              </label>
              <label>
                Мудрость:
                <input
                  type="number"
                  name="wisdom"
                  placeholder="Введите мудрость"
                  value={newCharacter.character_stats.wisdom}
                  onChange={handleChange}
                />
              </label>
              <label>
                Сопротивляемость:
                <input
                  type="number"
                  name="resistance"
                  placeholder="Введите сопротивляемость"
                  value={newCharacter.character_stats.resistance}
                  onChange={handleChange}
                />
              </label>
              <label>
                Устойчивость:
                <input
                  type="number"
                  name="stability"
                  placeholder="Введите устойчивость"
                  value={newCharacter.character_stats.stability}
                  onChange={handleChange}
                />
              </label>
              <label>
                Харизма:
                <input
                  type="number"
                  name="charisma"
                  placeholder="Введите харизму"
                  value={newCharacter.character_stats.charisma}
                  onChange={handleChange}
                />
              </label>
            </div>

            <button onClick={handleCreateCharacter}>Создать</button>
          </div>
        </div>
      )}

      {/* Модальное окно с информацией о персонаже */}
      {selectedCharacter && (
        <div className="modal-overlay" onClick={closeCharacterModal}>
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()} // Остановка всплытия события
          >
            <button className="modal-close-button" onClick={closeCharacterModal}>
              ×
            </button>
            <h2>{selectedCharacter.name}</h2>
            <p><strong>Статус:</strong> {selectedCharacter.status}</p>
            <h3>Характеристики</h3>
            <ul>
              {Object.entries(selectedCharacter.character_stats).map(
                ([key, value]) => (
                  <li key={key}>
                    <strong>{key}:</strong> {value}
                  </li>
                )
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
