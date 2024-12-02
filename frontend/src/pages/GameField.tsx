import React, { useState } from 'react';
import './GameField.css';

interface Token {
  id: string;
  x: number;
  y: number;
  name: string;
  size: number; // Новый параметр для размера токена
}

const GRID_SIZE = 10;

const GameField: React.FC = () => {
  const [tokens, setTokens] = useState<Token[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTokenName, setNewTokenName] = useState('');
  const [newTokenX, setNewTokenX] = useState(0);
  const [newTokenY, setNewTokenY] = useState(0);
  const [newTokenSize, setNewTokenSize] = useState(1); // Новый параметр для размера

  const handleAddToken = () => {
    setTokens((prevTokens) => [
      ...prevTokens,
      {
        id: Date.now().toString(),
        x: newTokenX,
        y: newTokenY,
        name: newTokenName,
        size: newTokenSize,
      },
    ]);
    setIsModalOpen(false);
    setNewTokenName('');
    setNewTokenX(0);
    setNewTokenY(0);
    setNewTokenSize(1);
  };

  const moveToken = (id: string, x: number, y: number) => {
    setTokens((prevTokens) =>
      prevTokens.map((token) =>
        token.id === id ? { ...token, x, y } : token
      )
    );
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const tokenId = event.dataTransfer.getData('tokenId');
    const cell = event.target as HTMLDivElement;

    const x = parseInt(cell.dataset.x || '0', 10);
    const y = parseInt(cell.dataset.y || '0', 10);

    moveToken(tokenId, x, y);
  };

  const allowDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleDragStart = (event: React.DragEvent<HTMLDivElement>, id: string) => {
    event.dataTransfer.setData('tokenId', id);
  };

  const removeToken = (id: string) => {
    setTokens((prevTokens) => prevTokens.filter((token) => token.id !== id));
  };

  return (
    <div>
      <div className="game-field">
        {Array.from({ length: GRID_SIZE }).map((_, y) =>
         Array.from({ length: GRID_SIZE }).map((_, x) => {
          const token = tokens.find(
        (token) => token.x === x && token.y === y
      );

      return (
        <div
          key={`${x}-${y}`}
          className="grid-cell"
          data-x={x}
          data-y={y}
          onDragOver={allowDrop}
          onDrop={handleDrop}
        >
          {token && (
            <div
              key={token.id}
              className="token"
              style={{
                width: `${token.size * 100}%`,
                height: `${token.size * 100}%`,
                gridColumn: `span ${token.size}`,
                gridRow: `span ${token.size}`,
              }}
              draggable
              onDragStart={(event) => handleDragStart(event, token.id)}
            >
              <div className="token-content">
                {token.name}
                <button
                  className="remove-token-btn"
                  onClick={() => removeToken(token.id)}
                >
                  &times;
                </button>
              </div>
            </div>
          )}
        </div>
      );
    })
  )}
</div>
      <button className="add-token-btn" onClick={() => setIsModalOpen(true)}>
        Добавить фигурку
      </button>
      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={() => setIsModalOpen(false)}>
              &times;
            </span>
            <h3>Добавить новую фигурку</h3>
            <label>
              Имя:
              <input
                type="text"
                value={newTokenName}
                onChange={(e) => setNewTokenName(e.target.value)}
              />
            </label>
            <label>
              X:
              <input
                type="number"
                value={newTokenX}
                min="0"
                max={GRID_SIZE - 1}
                onChange={(e) => setNewTokenX(Number(e.target.value))}
              />
            </label>
            <label>
              Y:
              <input
                type="number"
                value={newTokenY}
                min="0"
                max={GRID_SIZE - 1}
                onChange={(e) => setNewTokenY(Number(e.target.value))}
              />
            </label>
            <label>
              Размер:
              <input
                type="number"
                value={newTokenSize}
                min="1"
                max={GRID_SIZE}
                onChange={(e) => setNewTokenSize(Number(e.target.value))}
              />
            </label>
            <button onClick={handleAddToken}>Добавить</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GameField;
