import React, { useState } from 'react';
import './GameField.css';
import ReactDOM from 'react-dom';

interface Token {
  id: string;
  x: number;
  y: number;
  name: string;
  size: number; // Размер токена
}

const GameField: React.FC = () => {
  const [tokens, setTokens] = useState<Token[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTokenName, setNewTokenName] = useState('');
  const [newTokenX, setNewTokenX] = useState(0);
  const [newTokenY, setNewTokenY] = useState(0);
  const [newTokenSize, setNewTokenSize] = useState(1);
  const [gridWidth, setGridWidth] = useState(10); // Ширина игрового поля
  const [gridHeight, setGridHeight] = useState(10); // Высота игрового поля
  const [editingToken, setEditingToken] = useState<Token | null>(null);
  const [contextMenu, setContextMenu] = useState<{
    visible: boolean;
    x: number;
    y: number;
    tokenId: string | null;
  }>({ visible: false, x: 0, y: 0, tokenId: null });

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

  const showContextMenu = (event: React.MouseEvent<HTMLDivElement>, tokenId: string) => {
    event.preventDefault();
    setContextMenu({
      visible: true,
      x: event.clientX, 
      y: event.clientY,
      tokenId,
    });
  };
  
  const hideContextMenu = () => {
    setContextMenu({ visible: false, x: 0, y: 0, tokenId: null });
  };

  // Обработчик действий из контекстного меню
  const handleContextMenuAction = (action: string) => {
    if (contextMenu.tokenId) {
      const token = tokens.find((t) => t.id === contextMenu.tokenId);
  
      if (action === 'delete') {
        removeToken(contextMenu.tokenId);
      } else if (action === 'edit' && token) {
        setEditingToken(token);
      }
    }
    hideContextMenu();
  };

  const handleUpdateToken = () => {
    if (editingToken) {
      setTokens((prevTokens) =>
        prevTokens.map((token) =>
          token.id === editingToken.id ? editingToken : token
        )
      );
      setEditingToken(null);
    }
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
    <div className="game-container">
      {/* Панель с персонажами (сверху) */}
      <div className="player-panel">
        <h3>Панель персонажей (плейсхолдер)</h3>
        {/* Здесь будет логика отображения игроков */}
      </div>

      {/* Поле для игры и чат */}
      <div className="game-area">
        <div className="controls">
          <label>
            Ширина поля:
            <input
              type="number"
              value={gridWidth}
              min="5"
              max="50"
              onChange={(e) => setGridWidth(Number(e.target.value))}
            />
          </label>
          <label>
            Высота поля:
            <input
              type="number"
              value={gridHeight}
              min="5"
              max="50"
              onChange={(e) => setGridHeight(Number(e.target.value))}
            />
          </label>
        </div>

        <div onClick={hideContextMenu} className="game-field-container">
          <div
            className="game-field"
            style={{
              gridTemplateColumns: `repeat(${gridWidth}, 1fr)`,
              gridTemplateRows: `repeat(${gridHeight}, 1fr)`,
              width: `${gridWidth * 40}px`,
              height: `${gridHeight * 40}px`,
            }}
          >
            {Array.from({ length: gridHeight }).map((_, y) =>
              Array.from({ length: gridWidth }).map((_, x) => {
                const token = tokens.find((token) => token.x === x && token.y === y);

                return (
                  <div
                    key={`${x}-${y}`}
                    className="grid-cell"
                    data-x={x}
                    data-y={y}
                    onDragOver={allowDrop}
                    onDrop={handleDrop}
                    onContextMenu={(e) => e.preventDefault()}
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
                        onContextMenu={(event) => showContextMenu(event, token.id)}
                      >
                        <div className="token-content">{token.name}</div>
                        {contextMenu.visible && contextMenu.tokenId === token.id &&
                          ReactDOM.createPortal(
                            <div
                              className="context-menu"
                              style={{ top: contextMenu.y, left: contextMenu.x }}
                            >
                              <button onClick={() => handleContextMenuAction('delete')}>Удалить</button>
                              <button onClick={() => handleContextMenuAction('edit')}>Редактировать</button>
                            </div>,
                            document.body
                          )}
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
                    max={gridWidth - 1}
                    onChange={(e) => setNewTokenX(Number(e.target.value))}
                  />
                </label>
                <label>
                  Y:
                  <input
                    type="number"
                    value={newTokenY}
                    min="0"
                    max={gridHeight - 1}
                    onChange={(e) => setNewTokenY(Number(e.target.value))}
                  />
                </label>
                <label>
                  Размер:
                  <input
                    type="number"
                    value={newTokenSize}
                    min="1"
                    max={Math.min(gridWidth, gridHeight)}
                    onChange={(e) => setNewTokenSize(Number(e.target.value))}
                  />
                </label>
                <button onClick={handleAddToken}>Добавить</button>
              </div>
            </div>
          )}

          {editingToken && (
            <div className="modal">
              <div className="modal-content">
                <span className="close" onClick={() => setEditingToken(null)}>
                  &times;
                </span>
                <h3>Редактировать фигурку</h3>
                <label>
                  Имя:
                  <input
                    type="text"
                    value={editingToken.name}
                    onChange={(e) =>
                      setEditingToken({ ...editingToken, name: e.target.value })
                    }
                  />
                </label>
                <label>
                  X:
                  <input
                    type="number"
                    value={editingToken.x}
                    min="0"
                    max={gridWidth - 1}
                    onChange={(e) =>
                      setEditingToken({ ...editingToken, x: Number(e.target.value) })
                    }
                  />
                </label>
                <label>
                  Y:
                  <input
                    type="number"
                    value={editingToken.y}
                    min="0"
                    max={gridHeight - 1}
                    onChange={(e) =>
                      setEditingToken({ ...editingToken, y: Number(e.target.value) })
                    }
                  />
                </label>
                <label>
                  Размер:
                  <input
                    type="number"
                    value={editingToken.size}
                    min="1"
                    max={Math.min(gridWidth, gridHeight)}
                    onChange={(e) =>
                      setEditingToken({ ...editingToken, size: Number(e.target.value) })
                    }
                  />
                </label>
                <button onClick={handleUpdateToken}>Сохранить</button>
              </div>
            </div>
          )}
        </div>
        <div className="chat-panel">
        <h3>Чат (плейсхолдер)</h3>
        {/* Здесь будет логика чата */}
      </div>
      </div>

      {/* Блок для placeholder чата (справа экрана) */}
      
    </div>
  );
};

export default GameField;
