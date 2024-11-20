import React, { useState } from "react";
import {Character} from './CharacterList';

interface Props {
  onClose: () => void;
  onCreate: (character: Character) => void;
}

const CreateCharacterModal: React.FC<Props> = ({ onClose, onCreate }) => {
  const [name, setName] = useState("");
  const [level, setLevel] = useState(1);
  const [characterClass, setCharacterClass] = useState("");

  const handleSubmit = () => {
    const newCharacter = { id: Date.now().toString(), name, level, characterClass };
    onCreate(newCharacter);
  };

  return (
    <div className="modal">
      <h2>Создать персонажа</h2>
      <input 
        type="text" 
        placeholder="Имя" 
        value={name} 
        onChange={(e) => setName(e.target.value)} 
      />
      <input 
        type="number" 
        placeholder="Уровень" 
        value={level} 
        onChange={(e) => setLevel(Number(e.target.value))} 
      />
      <input 
        type="text" 
        placeholder="Класс" 
        value={characterClass} 
        onChange={(e) => setCharacterClass(e.target.value)} 
      />
      <button onClick={handleSubmit}>Создать</button>
      <button onClick={onClose}>Закрыть</button>
    </div>
  );
};

export default CreateCharacterModal;
