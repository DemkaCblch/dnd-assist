import React from "react";
import { Character } from "../components/CharacterList";



interface Props {
  character: Character;
  onClose: () => void;
  onConfirm: () => void;
}

const ConfirmDeleteModal: React.FC<Props> = ({ character, onClose, onConfirm }) => {
  return (
    <div className="modal">
      <h2>Удалить персонажа?</h2>
      <p>Вы действительно хотите удалить {character.name}?</p>
      <button onClick={onConfirm}>Удалить</button>
      <button onClick={onClose}>Отмена</button>
    </div>
  );
};

export default ConfirmDeleteModal;
