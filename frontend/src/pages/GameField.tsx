import React, { useState } from 'react';
import './GameField.css';

interface Token {
  id: string;
  x: number;
  y: number;
}

const GRID_SIZE = 10; // Размер сетки (10x10)

const GameField: React.FC = () => {
  const [tokens, setTokens] = useState<Token[]>([
    { id: '1', x: 0, y: 0 }, // Пример фигурки
  ]);

  const moveToken = (id: string, x: number, y: number) => {
    setTokens((prevTokens) =>
      prevTokens.map((token) => (token.id === id ? { ...token, x, y } : token))
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

  return (
    <div className="game-field">
      {Array.from({ length: GRID_SIZE }).map((_, y) =>
        Array.from({ length: GRID_SIZE }).map((_, x) => (
          <div
            key={`${x}-${y}`}
            className="grid-cell"
            data-x={x}
            data-y={y}
            onDragOver={allowDrop}
            onDrop={handleDrop}
          >
            {tokens
              .filter((token) => token.x === x && token.y === y)
              .map((token) => (
                <div
                  key={token.id}
                  className="token"
                  draggable
                  onDragStart={(event) => handleDragStart(event, token.id)}
                >
                  ⚔️
                </div>
              ))}
          </div>
        ))
      )}
    </div>
    
  );
};

export default GameField;
