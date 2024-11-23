import React, { useState, useEffect } from "react";
import CharacterList from "../components/CharacterList";
import CreateCharacterModal from "../components/CreateCharacterModal";
import ConfirmDeleteModal from "../components/ConfirmDeleteModal";
import { Character } from "../components/CharacterList";


const Chars:React.FC = () =>{
    const [characters, setCharacters] = useState<Character[]>([]);
    const [isCreateModalOpen, setCreateModalOpen] = useState(false);
    const [isDeleteModalOpen, setDeleteModalOpen] = useState(false);
    const [characterToDelete, setCharacterToDelete] = useState<Character | null>(null);
    useEffect(() => {
        fetch("/api/characters")
          .then((response) => response.json())
          .then((data) => setCharacters(data))
          .catch((error) => console.error("Ошибка загрузки персонажей:", error));
      }, []);
    const handleCreateCharacter = (newCharacter: Character) => {
        // Добавляем персонажа в базу данных и обновляем список
        fetch("/api/create-character", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newCharacter),
        })
          .then((response) => response.json())
          .then((createdCharacter) => setCharacters([...characters, createdCharacter]));
        setCreateModalOpen(false);
      };
      const handleDeleteCharacter = () => {
        if (!characterToDelete) return;
        // Удаляем персонажа из базы данных
        fetch(`/api/characters/${characterToDelete.id}`, { method: "DELETE" })
          .then(() => setCharacters(characters.filter((char) => char.id !== characterToDelete.id)));
        setDeleteModalOpen(false);
        setCharacterToDelete(null);
      };
      return (
        <div className="app">
          <h1>Выбор персонажа</h1>
          <button onClick={() => setCreateModalOpen(true)}>Создать персонажа</button>
          <CharacterList 
            characters={characters} 
            onDelete={(character) => {
              setCharacterToDelete(character);
              setDeleteModalOpen(true);
            }} 
          />
          {isCreateModalOpen && (
            <CreateCharacterModal 
              onClose={() => setCreateModalOpen(false)} 
              onCreate={handleCreateCharacter} 
            />
          )}
          {isDeleteModalOpen && (
            <ConfirmDeleteModal 
              character={characterToDelete!} 
              onClose={() => setDeleteModalOpen(false)} 
              onConfirm={handleDeleteCharacter} 
            />
          )}
        </div>
      );
};
export default Chars;