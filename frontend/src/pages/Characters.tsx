import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Characters.css'

const Profile = () => {
  interface Character {
    id: number;
    name: string;
    status: string;
    character_stats: {
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
    };
  }
  const [user, setUser] = useState<any>(null); 
  const [characters, setCharacters] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null); 
  const [isCharacterModalOpen, setIsCharacterModalOpen] = useState<boolean>(false); 
  const closeCharacterModal = () => {
    setIsCharacterModalOpen(false);
    setSelectedCharacter(null); 
  };

  const [isModalOpen, setIsModalOpen] = useState<boolean>(false); 
  const [newCharacter, setNewCharacter] = useState<any>({
    name: '',
    status: 'Активен',
    character_stats: {
      hp: 100,
      race: 'Человек',
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

  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserProfile = async () => {
      const token = localStorage.getItem('authToken');
      if (!token) return navigate('/login'); 

      try {
        const response = await fetch('http://localhost:8000/api/profile/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setUser(data);
        } else {
          setError('Ошибка при получении данных');
        }
      } catch (err) {
        setError('Произошла ошибка. Попробуйте позже.');
      }
    };

    const fetchUserCharacters = async () => {
      const token = localStorage.getItem('authToken');
      if (!token) return navigate('/login');

      try {
        const response = await fetch('http://localhost:8000/api/get-character/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setCharacters(data || []);
        } else {
          setError('Ошибка при получении персонажей');
        }
      } catch (err) {
        setError('Произошла ошибка. Попробуйте позже.');
      }
    };

    fetchUserProfile();
    fetchUserCharacters();
  }, [navigate]);

  const handleCharacterClick = async (characterId: number) => {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    try {
      const response = await fetch(`http://localhost:8000/api/characters/${characterId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedCharacter(data); 
        setIsCharacterModalOpen(true); 
      }
    } catch (error) {
      console.error('Ошибка при получении данных персонажа:', error);
    }
  };

  const handleCreateCharacter = async () => {
    const token = localStorage.getItem('authToken');
    if (!token) return navigate('/login'); 

    try {
      const response = await fetch('http://localhost:8000/api/create-character/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify(newCharacter),
      });

      if (response.ok) {
        const createdCharacter = await response.json();
        setCharacters([...characters, createdCharacter]); 
        setIsModalOpen(false); 
        setNewCharacter({
          name: '',
          status: 'Активен',
          character_stats: {
            hp: 100,
            race: 'Человек',
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
        }); // Сбрасываем форму
      } else {
        setError('Ошибка при создании персонажа');
      }
    } catch (err) {
      setError('Произошла ошибка при создании персонажа');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewCharacter({
      ...newCharacter,
      [e.target.name]: e.target.value,
    });
  };

  const handleStatsChange = (e: React.ChangeEvent<HTMLInputElement>, stat: string) => {
    setNewCharacter({
      ...newCharacter,
      character_stats: {
        ...newCharacter.character_stats,
        [stat]: parseInt(e.target.value, 10),
      },
    });
  };


  return (
    <div className="profile-page">
      <h1>Личный кабинет</h1>
      <div>
        <strong>Имя пользователя:</strong> {user?.username}
      </div>
      <div>
        <strong>Дата регистрации:</strong> {new Date(user?.date_joined).toLocaleDateString()}
      </div>

      <h2>Ваши персонажи</h2>
      <button onClick={() => setIsModalOpen(true)} className="btn create-character-btn">
        Создать персонажа
      </button>

      {characters.length > 0 ? (
        <ul>
          {characters.map((character) => (
            <li
              key={character.id}
              onClick={() => handleCharacterClick(character.id)} 
              className="character-item"
            >
              {character.name} - {character.status}
            </li>
          ))}
        </ul>
      ) : (
        <p>Нет доступных персонажей.</p>
      )}

      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="modal-close-button" onClick={() => setIsModalOpen(false)}>
              ×
            </button>
            <h2>Создать нового персонажа</h2>
            <form>
              <input
                type="text"
                name="name"
                value={newCharacter.name}
                onChange={handleChange}
                placeholder="Имя персонажа"
              />
              <input
                type="text"
                name="status"
                value={newCharacter.status}
                onChange={handleChange}
                placeholder="Статус персонажа"
              />
              <div className="character-stats">
                <h3>Характеристики</h3>
                <div className="stats-row">
                  <label>HP:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.hp}
                    onChange={(e) => handleStatsChange(e, 'hp')}
                    placeholder="HP"
                  />
                </div>
                <div className="stats-row">
                  <label>Уровень:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.level}
                    onChange={(e) => handleStatsChange(e, 'level')}
                    placeholder="Уровень"
                  />
                </div>
                <div className="stats-row">
                  <label>Интеллект:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.intelligence}
                    onChange={(e) => handleStatsChange(e, 'intelligence')}
                    placeholder="Интеллект"
                  />
                </div>
                <div className="stats-row">
                  <label>Сила:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.strength}
                    onChange={(e) => handleStatsChange(e, 'strength')}
                    placeholder="Сила"
                  />
                </div>
                <div className="stats-row">
                  <label>Ловкость:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.dexterity}
                    onChange={(e) => handleStatsChange(e, 'dexterity')}
                    placeholder="Ловкость"
                  />
                </div>
                <div className="stats-row">
                  <label>Выносливость:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.constitution}
                    onChange={(e) => handleStatsChange(e, 'constitution')}
                    placeholder="Выносливость"
                  />
                </div>
                <div className="stats-row">
                  <label>Мудрость:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.wisdom}
                    onChange={(e) => handleStatsChange(e, 'wisdom')}
                    placeholder="Мудрость"
                  />
                </div>
                <div className="stats-row">
                  <label>Сопротивление:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.resistance}
                    onChange={(e) => handleStatsChange(e, 'resistance')}
                    placeholder="Сопротивление"
                  />
                </div>
                <div className="stats-row">
                  <label>Устойчивость:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.stability}
                    onChange={(e) => handleStatsChange(e, 'stability')}
                    placeholder="Устойчивость"
                  />
                </div>
                <div className="stats-row">
                  <label>Харизма:</label>
                  <input
                    type="number"
                    value={newCharacter.character_stats.charisma}
                    onChange={(e) => handleStatsChange(e, 'charisma')}
                    placeholder="Харизма"
                  />
                </div>
              </div>
              <button type="button" onClick={handleCreateCharacter}>
                Создать персонажа
              </button>
            </form>

            {error && <p className="error">{error}</p>}
          </div>
        </div>
      )}
      {isCharacterModalOpen && selectedCharacter && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="modal-close-button" onClick={closeCharacterModal}>
              ×
            </button>
            <h2>Информация о персонаже: {selectedCharacter.name}</h2>
            <p><strong>Статус:</strong> {selectedCharacter.status}</p>
            <h3>Характеристики:</h3>
            <ul>
              <li><strong>Здоровье:</strong> {selectedCharacter.character_stats.hp}</li>
              <li><strong>Раса:</strong> {selectedCharacter.character_stats.race}</li>
              <li><strong>Уровень:</strong> {selectedCharacter.character_stats.level}</li>
              <li><strong>Интеллект:</strong> {selectedCharacter.character_stats.intelligence}</li>
              <li><strong>Сила:</strong> {selectedCharacter.character_stats.strength}</li>
              <li><strong>Ловкость:</strong> {selectedCharacter.character_stats.dexterity}</li>
              <li><strong>Конституция:</strong> {selectedCharacter.character_stats.constitution}</li>
              <li><strong>Мудрость:</strong> {selectedCharacter.character_stats.wisdom}</li>
              <li><strong>Сопротивление:</strong> {selectedCharacter.character_stats.resistance}</li>
              <li><strong>Стойкость:</strong> {selectedCharacter.character_stats.stability}</li>
              <li><strong>Харизма:</strong> {selectedCharacter.character_stats.charisma}</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
