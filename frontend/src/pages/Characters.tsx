import React, { useState, useEffect } from "react";
import "./Characters.css";
import apiClient from "../apiClient";
import { toast, ToastContainer } from "react-toastify";

interface CharacterStats {
  hp: number;
  race: string;
  mana: number;
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

interface EntityStats{
  hp: number;
  level: number;
  resistance: number;
  stability: number;
}

interface Entity{
  id: number;
  name: string;
  status: string;
  entity_stats: EntityStats;
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
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(
    null
  );
  const [entity, setEntity] = useState<Entity[]>([]);
  const [newEntity, setNewEntity] = useState<Entity>({
    id: 0,
    name: "",
    status: "Активен",
    entity_stats: {
      hp: 100,
      level: 1,
      resistance: 10,
      stability: 10,
    },
  });
  const [error, setError] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCreateEModalOpen, setIsCreateEModalOpen] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [newCharacter, setNewCharacter] = useState<Character>({
    id: 0,
    name: "",
    status: "Активен",
    character_stats: {
      hp: 100,
      race: "",
      level: 1,
      mana: 5,
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

    const fetchEntity = async () => {
      try {
        const response = await apiClient.get("/get-entity/");
        console.log("Ответ API при загрузке сущностей:", response.data);
    
        const entities = Array.isArray(response.data) ? response.data : [response.data];
        setEntity(entities); 
      } catch (err) {
        console.error(err);
        /*setError("Ошибка при загрузке существ");*/
        setEntity([]); 
      }
    };
    
  
    fetchUserProfile();
    fetchCharacters();
    fetchEntity();
  }, []);

  const handleCharacterClick = (character: Character) => {
    setSelectedCharacter(character);
  };
  const handleEntityClick = (entity: Entity) => {
    setSelectedEntity(entity);
  };

  const closeCharacterModal = () => {
    setSelectedCharacter(null);
  };

  const openCreateModal = () => {
    setIsCreateModalOpen(true);
  };

  const openCreateEModal = () => {
    setIsCreateEModalOpen(true);
  };

  const closeCreateEModal = () => {
    setIsCreateEModalOpen(false);
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
      toast.error("Ошибка при создании существа");
    }
  };
  const handleCreateEntity = async () => {
    try {
      const response = await apiClient.post("/create-entity/", newEntity);
      console.log("Ответ API:", response.data);
      setEntity([...entity, response.data]);
      closeCreateModal();
    } catch (err) {
      console.error(err);
      setError("Ошибка при создании существа");
    }
  };
  

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
  
    // Проверяем, если поле относится к статистике персонажа
    if (name in newCharacter.character_stats) {
      const isNumericField = [
        "hp", "level", "mana", "intelligence", "strength",
        "dexterity", "constitution", "wisdom", "resistance", 
        "stability", "charisma",
      ].includes(name);
  
      setNewCharacter((prev) => ({
        ...prev,
        character_stats: {
          ...prev.character_stats,
          [name]: isNumericField ? Number(value) : value, // Преобразуем числовые поля
        },
      }));
    }
    // Проверяем, если поле относится к статистике существа
    else if (name in newEntity.entity_stats) {
      const isNumericField = ["hp", "level", "resistance", "stability"].includes(name);
  
      setNewEntity((prev) => ({
        ...prev,
        entity_stats: {
          ...prev.entity_stats,
          [name]: isNumericField ? Number(value) : value, // Преобразуем числовые поля
        },
      }));
    }
    // Если поле - это имя персонажа
    else if (name === "name" && newCharacter) {
      setNewCharacter((prev) => ({
        ...prev,
        [name]: value, // Обновляем имя персонажа
      }));
    }
    // Если поле - это имя существа
    else if (name === "name" && newEntity) {
      setNewEntity((prev) => ({
        ...prev,
        [name]: value, // Обновляем имя существа
      }));
    }
  };
  
  
  
  

  return (
    <div className="profile">
      {userProfile && (
        <div className="user-info">
          <h1>Личный кабинет</h1>
        <img src={"default-avatar.jpg"} alt="User Avatar" />
        <p><strong>Имя пользователя:</strong> {userProfile.username}</p>
        <p><strong>Дата регистрации:</strong> {new Date(userProfile.date_joined).toLocaleDateString()}</p>
        </div>
      
      )}
      {error && <p className="error">{error}</p>}
      
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
        <button className="create-button" onClick={openCreateModal}>
          Создать персонажа
        </button>
      </div>
      <div className="characters-list">
        {entity.length > 0 ? (
          entity.map((e) => (
            <div
              key={e.id}
              className="character-item"
              onClick={() => handleEntityClick(e)}
            >
              <h2>{e.name}</h2>
              <p>Статус: {e.status}</p>
            </div>
          ))
        ) : (
          <p>У вас нет созданных существ</p>
          
        )}
        <button className="create-button" onClick={openCreateEModal}>
          Создать существо
        </button>
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
                Мана:
                <input
                  type="number"
                  name="mana"
                  placeholder="Введите ману"
                  value={newCharacter.character_stats.mana}
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
      {isCreateEModalOpen && (
        <div className="modal-overlay" onClick={closeCreateEModal}>
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()} // Остановка всплытия события
          >
            <button className="modal-close-button" onClick={closeCreateEModal}>
              ×
            </button>
            <h2>Создать существо</h2>
            <div className="entity-stats">
              <label>
                Имя существа:
                <input
                  type="text"
                  name="name"
                  placeholder="Введите имя"
                  value={newEntity.name}
                  onChange={handleChange}
                />
              </label>
              <label>
                HP:
                <input
                  type="number"
                  name="hp"
                  placeholder="Введите HP"
                  value={newEntity.entity_stats.hp}
                  onChange={handleChange}
                />
              </label>
              <label>
                Уровень:
                <input
                  type="number"
                  name="level"
                  placeholder="Введите уровень"
                  value={newEntity.entity_stats.level}
                  onChange={handleChange}
                />
              </label>
              <label>
                Сопротивляемость:
                <input
                  type="number"
                  name="resistance"
                  placeholder="Введите сопротивляемость"
                  value={newEntity.entity_stats.resistance}
                  onChange={handleChange}
                />
              </label>
              <label>
                Устойчивость:
                <input
                  type="number"
                  name="stability"
                  placeholder="Введите устойчивость"
                  value={newEntity.entity_stats.stability}
                  onChange={handleChange}
                />
              </label>
            </div>

            <button onClick={handleCreateEntity}>Создать</button>
          </div>
        </div>
      )}
      {selectedEntity && (
        <div className="modal-overlay" onClick={() => setSelectedEntity(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close-button"
              onClick={() => setSelectedEntity(null)}
            >
              ×
            </button>
            <h2>{selectedEntity.name}</h2>
            <p><strong>Статус:</strong> {selectedEntity.status}</p>
            <h3>Характеристики</h3>
            <ul>
              {Object.entries(selectedEntity.entity_stats).map(([key, value]) => (
                <li key={key}>
                  <strong>{key}:</strong> {value}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
     <ToastContainer position="top-right" autoClose={3000} hideProgressBar />
    </div>
  );
};

export default Profile;
