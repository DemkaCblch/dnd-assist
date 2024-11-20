import React from "react";
/*import "./CharacterList.css";*/

export interface Character {
  id: string;
  name: string;
  level: number;
  characterClass: string;
}

interface Props {
  characters: Character[];
  onDelete: (character: Character) => void;
}

const CharacterList: React.FC<Props> = ({ characters, onDelete }) => {
  return (
    <div className="character-list">
      {characters.map((char) => (
        <div key={char.id} className="character-card">
          <h3>{char.name}</h3>
          <p>Уровень: {char.level}</p>
          <p>Класс: {char.characterClass}</p>
          <button onClick={() => onDelete(char)}>Удалить</button>
        </div>
      ))}
    </div>
  );
};

export default CharacterList;
