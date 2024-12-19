import React, { useState, useEffect } from 'react';
import './GameField.css';
import ReactDOM from 'react-dom';
import WebSocketService from '../Services/wsservice'; 

interface Token {
  id: string;
  x: number;
  y: number;
  name: string;
}

interface PlayerStats {
  hp: number;
  mana: number;
  race: string;
  intelligence: number;
  strength: number;
  dexterity: number;
  constitution: number;
  wisdom: number;
  charisma: number;
  level: number;
  resistance: number;
  stability: number;
}

interface Player {
  id: string;
  name: string;
  hp: number;
  maxHp: number;
  mana: number;
  maxMana: number;
  backpack: { items: { id: string; name: string; description: string }[] }
  stats: PlayerStats;
}

const GameField: React.FC = () => {
  const [tokens, setTokens] = useState<Token[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTokenX, setNewTokenX] = useState(0);
  const [newTokenY, setNewTokenY] = useState(0);
  const [gridWidth, setGridWidth] = useState(10);
  const [gridHeight, setGridHeight] = useState(10);
  const [editingToken, setEditingToken] = useState<Token | null>(null);
  const [contextMenu, setContextMenu] = useState<{ visible: boolean; x: number; y: number; tokenId: string | null }>({ visible: false, x: 0, y: 0, tokenId: null });

  const [backpackModalVisible, setBackpackModalVisible] = useState(false);
  const [currentBackpackItems, setCurrentBackpackItems] = useState<{ id: string; name: string; description: string }[]>([]);
  const [currentFigureId, setCurrentFigureId] = useState<string | null>(null);
  const [newItemName, setNewItemName] = useState('');
  const [newItemDesc, setNewItemDesc] = useState('');

  const [mongoRoomId, setMongoRoomId] = useState<string | null>(null);
  const [currentMove, setCurrentMove] = useState<string | null>(null);

  const [statsModalVisible, setStatsModalVisible] = useState(false);
  const [editingPlayerStats, setEditingPlayerStats] = useState<PlayerStats | null>(null);
  const [editingPlayerId, setEditingPlayerId] = useState<string | null>(null);

  const [enemyId, setEnemyId] = useState(''); 

  const [chatMessages, setChatMessages] = useState<{ name: string; message: string }[]>([]);
  const [chatInput, setChatInput] = useState('');





  useEffect(() => {
    const gameDataString = sessionStorage.getItem("gameData");
    if (!gameDataString) {
      console.warn("Нет данных игры.");
      return;
    }
    const gameData = JSON.parse(gameDataString);
    setMongoRoomId(gameData.id);
    
    if (gameData.table) {
      setGridWidth(gameData.table.length);
      setGridHeight(gameData.table.height);
    }

    if (gameData.current_move) {
      setCurrentMove(gameData.current_move);
    }

    const newTokens: Token[] = [];
    if (gameData.player_figures) {
      for (const pf of gameData.player_figures) {
        newTokens.push({
          id: pf.id,
          x: pf.posX,
          y: pf.posY,
          name: pf.name
        });
      }
    }
    if (gameData.entity_figures) {
      for (const ef of gameData.entity_figures) {
        newTokens.push({
          id: ef.id,
          x: ef.posX,
          y: ef.posY,
          name: ef.name,
        });
      }
    }
    setTokens(newTokens);

    const newPlayers: Player[] = [];
    if (gameData.player_figures) {
      for (const pf of gameData.player_figures) {
        const char = pf.character && pf.character[0];
        const stats = char && char.stats && char.stats[0];
        const backpack = pf.backpack || { items: [] };
        if (stats) {
          newPlayers.push({
            id: pf.id,
            name: pf.name,
            hp: stats.hp,
            maxHp: stats.hp,
            mana: stats.mana,
            maxMana: stats.mana,
            backpack: backpack,
            stats: {
              hp: stats.hp,
              mana: stats.mana,
              race: stats.race,
              intelligence: stats.intelligence,
              strength: stats.strength,
              dexterity: stats.dexterity,
              constitution: stats.constitution,
              wisdom: stats.wisdom,
              charisma: stats.charisma,
              level: stats.level,
              resistance: stats.resistance,
              stability: stats.stability
            }
          });
        }
      }
    }
    setPlayers(newPlayers);
  }, []);

  useEffect(() => {
    const socket = WebSocketService.getSocket();
    if (!socket) return;

    const onMessage = (event: MessageEvent) => {
      const message = JSON.parse(event.data);
      if (message.type === 'add_item') {
        const { figure_id, item_name, item_description, id } = message;
        setPlayers((prev) =>
          prev.map((p) => {
            if (p.id === figure_id) {
              return {
                ...p,
                backpack: {
                  ...p.backpack,
                  items: [...p.backpack.items, { id, name: item_name, description: item_description }]
                }
              };
            }
            return p;
          })
        );
      } else if (message.type === 'delete_item') {
        const { figure_id, id } = message;
        setPlayers((prev) =>
          prev.map((p) => {
            if (p.id === figure_id) {
              return {
                ...p,
                backpack: {
                  ...p.backpack,
                  items: p.backpack.items.filter((item) => item.id !== id)
                }
              };
            }
            return p;
          })
        );
      } else if (message.type === 'change_turn') {
 
        setCurrentMove(message.figure_id || "Master");
      } else if (message.type === 'change_position_figure') {

        setTokens((prevTokens) =>
          prevTokens.map((t) =>
            t.id === message.figure_id ? { ...t, x: message.posX, y: message.posY } : t
          )
        );
      } else if (message.type === 'change_character_stats') {
        const { figure_id, stats } = message;
    
        setPlayers((prev) =>
          prev.map((p) => {
            if (p.id === figure_id) {
              return {
                ...p,
                hp: stats.hp,
               // maxHp: stats.hp, // если нужно
                mana: stats.mana,
                //maxMana: stats.mana, // если нужно
                stats: { ...p.stats, ...stats }
              };
            }
            return p;
          })
        );
      }
      else if (message.type === 'add_entity') {
        const { entity_figure } = message;
      
        setTokens((prevTokens) => [
          ...prevTokens,
          {
            id: entity_figure.id,
            x: entity_figure.posX,
            y: entity_figure.posY,
            name: entity_figure.name,
          },
        ]);
      } else if (message.type === 'send_message') {
        const { name, message: msg } = message;
        setChatMessages((prev) => [...prev, { name, message: msg }]);
      }
      
    };

    socket.addEventListener('message', onMessage);
    return () => {
      socket.removeEventListener('message', onMessage);
    };
  }, []);

  useEffect(() => {
    if (backpackModalVisible && currentFigureId) {
      const player = players.find(p => p.id === currentFigureId);
      if (player) {
        setCurrentBackpackItems(player.backpack.items);
      }
    }
  }, [players, backpackModalVisible, currentFigureId]);

  

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

  const handleContextMenuAction = (action: string) => {
    if (contextMenu.tokenId) {
      const token = tokens.find((t) => t.id === contextMenu.tokenId);
      if (action === 'delete') {
        removeToken(contextMenu.tokenId);
      } else if (action === 'edit' && token) {
        setEditingToken(token);
      } else if (action === 'backpack') {
        const player = players.find(p => p.id === contextMenu.tokenId);
        if (player) {
          setCurrentFigureId(player.id);
          setCurrentBackpackItems(player.backpack.items);
          setBackpackModalVisible(true);
        }
      } else if (action === 'edit_stats') {
        const player = players.find(p => p.id === contextMenu.tokenId);
        if (player) {
          setStatsModalVisible(true);
          setEditingPlayerStats({ ...player.stats }); 
          setEditingPlayerId(player.id);
        }
      }
    }
    hideContextMenu();
  };

  const handleChangeTurnMaster = (targetFigureId: string) => {
    WebSocketService.send({
      "action":"change_turn",
      "figure_id": targetFigureId,
      "mongo_room_id": mongoRoomId 
    });
  };

  const handleChangeTurnPlayer = () => {
    WebSocketService.send({
      "action": "change_turn",
      mongo_room_id: mongoRoomId
    });
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
  
    if (!canMoveToken(tokenId)) {
      console.log("Вы не можете перемещать эту фигуру.");
      return;
    }
  

    // moveToken(tokenId, x, y);
  

    if (mongoRoomId) {
      WebSocketService.send({
        action: "change_position_figure",
        mongo_room_id: mongoRoomId,
        figure_id: tokenId,
        posX: x,
        posY: y
      });
    }
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

  const handleChangeCharacterStats = (figureId: string, stats: any) => {
    if (!mongoRoomId) return;
  
    WebSocketService.send({
      action: "change_character_stats",
      mongo_room_id: mongoRoomId,
      figure_id: figureId,
      stats: {
        hp: stats.hp,
        mana: stats.mana,
        race: stats.race,
        intelligence: stats.intelligence,
        strength: stats.strength,
        dexterity: stats.dexterity,
        constitution: stats.constitution,
        wisdom: stats.wisdom,
        charisma: stats.charisma,
        level: stats.level,
        resistance: stats.resistance,
        stability: stats.stability,
      },
    });
  };

  const renderBar = (current: number, max: number, color: string) => {
    const percentage = (current / max) * 100;
    return (
      <div className="stat-bar">
        <div
          style={{
            width: `${percentage}%`,
            backgroundColor: color,
            textAlign: 'center',
          }}
        >
          {current}/{max}
        </div>
      </div>
    );
  };

  // Функции для работы с рюкзаком
  const handleAddItemToBackpack = () => {
    if (!currentFigureId || !newItemName) return;
    WebSocketService.send({
      "action": "add_item",
      "figure_id": currentFigureId,
      "name": newItemName,
      "description": newItemDesc,
      "mongo_room_id": mongoRoomId 
    });
    setNewItemName('');
    setNewItemDesc('');
  };

  const handleDeleteItemFromBackpack = (itemId: string) => {
    if (!currentFigureId) return;
    WebSocketService.send({
      "action": "delete_item",
      "figure_id": currentFigureId,
      "id": itemId,
      "mongo_room_id": mongoRoomId 
    });
  };

  const canMoveToken = (figureId: string): boolean => {
    if (!figureId || !mongoRoomId) return false;
  

    if (currentMove === "Master") {

      return true;
    }

    return currentMove === figureId;
  };

  const handleSaveStats = () => {
    if (!editingPlayerId || !mongoRoomId || !editingPlayerStats) return;
    WebSocketService.send({
      action: "change_character_stats",
      mongo_room_id: mongoRoomId,
      figure_id: editingPlayerId,
      stats: editingPlayerStats
    });
    setStatsModalVisible(false);
  };

  const handleAddEnemy = () => {
    if (!mongoRoomId || !enemyId || newTokenX === null || newTokenY === null) {
      console.warn("Заполните все поля для добавления врага");
      return;
    }
  
    WebSocketService.send({
      action: "add_entity",
      mongo_room_id: mongoRoomId,
      entity_id: enemyId,
      posX: newTokenX,
      posY: newTokenY,
    });
  
    setEnemyId('');
    setNewTokenX(0);
    setNewTokenY(0);
    setIsModalOpen(false);
  };

  const handleSendChatMessage = () => {
    if (!mongoRoomId || !chatInput.trim()) return;
    WebSocketService.send({
      action: "chat_message",
      mongo_room_id: mongoRoomId,
      message: chatInput.trim()
    });
    setChatInput('');
  };
  

  return (
    <div className="game-container">
      <div className="player-panel">
        <h3>Панель персонажей</h3>
        <div className="players-list">
          {players.map((player) => (
            <div key={player.id} className="player-item">
              <p><strong>{player.name}</strong></p>
              <span>HP:</span>
              {renderBar(player.hp, player.maxHp, 'red')}
              <span>Mana:</span>
              {renderBar(player.mana, player.maxMana, 'blue')}
            </div>
          ))}
        </div>
      </div>

      <div className="game-area">
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

                        }}
                        draggable
                        onDragStart={(event) => handleDragStart(event, token.id)}
                        onContextMenu={(event) => {
                          event.preventDefault();
                          setContextMenu({
                            visible: true,
                            x: event.clientX,
                            y: event.clientY,
                            tokenId: token.id
                          });
                        }}
                      >
                        <div className="token-content">{token.name}</div>
                        {contextMenu.visible && contextMenu.tokenId === token.id &&
                          ReactDOM.createPortal(
                            <div className="context-menu" style={{ top: contextMenu.y, left: contextMenu.x }}>
                              <button onClick={() => handleContextMenuAction('delete')}>Удалить</button>
                              <button onClick={() => handleContextMenuAction('edit')}>Редактировать</button>
                              <button onClick={() => handleContextMenuAction('backpack')}>Рюкзак</button>
                              <button onClick={() => handleContextMenuAction('edit_stats')}>Статы</button>
                            </div>,
                            document.body
                          )
                        }
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
          
        </div>
        <div className="button-container">
          <button className="add-token-btn" onClick={() => setIsModalOpen(true)}>
            Добавить фигурку
          </button>
          {currentMove === "Master" && (
          <div className="turn-controls">
            <h4>Передать ход игроку:</h4>
            <select onChange={(e) => handleChangeTurnMaster(e.target.value)}>
              <option value="">Выберите игрока</option>
              {players.map((p) => (
                <option value={p.id} key={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          )}
          {players.some((p) => p.id === currentMove) && (
          <div className="turn-controls">
            <button onClick={handleChangeTurnPlayer}>Завершить ход</button>
          </div>
        )}
        </div>
        
        <div className="chat-panel">
          <h3>Чат</h3>
          <div className="chat-messages" style={{flex: '1', overflowY: 'auto', marginBottom: '10px'}}>
            {chatMessages.map((msg, index) => (
              <div key={index} style={{marginBottom: '5px'}}>
                <strong>{msg.name}:</strong> {msg.message}
              </div>
            ))}
          </div>
          <div className="chat-input" style={{display: 'flex', gap: '5px'}}>
            <input 
              type="text" 
              value={chatInput} 
              onChange={(e) => setChatInput(e.target.value)} 
              placeholder="Введите сообщение..." 
              style={{flex: '1', padding: '5px'}}
            />
            <button onClick={handleSendChatMessage}>Отправить</button>
          </div>
        </div>
      </div>

      {/* Модалка рюкзака */}
      {backpackModalVisible && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={() => setBackpackModalVisible(false)}>
              &times;
            </span>
            <h3>Рюкзак</h3>
            <ul>
              {currentBackpackItems.map((item) => (
                <li key={item.id}>
                  <strong>{item.name}</strong>: {item.description}
                  <button onClick={() => handleDeleteItemFromBackpack(item.id)}>Удалить</button>
                </li>
              ))}
            </ul>
            <h4>Добавить предмет:</h4>
            <label>
              Название:
              <input type="text" value={newItemName} onChange={(e) => setNewItemName(e.target.value)} />
            </label>
            <label>
              Описание:
              <input type="text" value={newItemDesc} onChange={(e) => setNewItemDesc(e.target.value)} />
            </label>
            <button onClick={handleAddItemToBackpack}>Добавить в рюкзак</button>
          </div>
        </div>
      )}
      {statsModalVisible && editingPlayerStats && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={() => setStatsModalVisible(false)}>
              &times;
            </span>
            <h3>Редактировать характеристики</h3>
            <label>
              HP: 
              <input 
                type="number" 
                value={editingPlayerStats.hp} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, hp: Number(e.target.value)})} 
              />
            </label>
            <label>
              Mana: 
              <input 
                type="number" 
                value={editingPlayerStats.mana} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, mana: Number(e.target.value)})} 
              />
            </label>
            <label>
              Race: 
              <input 
                type="text" 
                value={editingPlayerStats.race} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, race: e.target.value})} 
              />
            </label>
            <label>
              Intelligence: 
              <input 
                type="number" 
                value={editingPlayerStats.intelligence} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, intelligence: Number(e.target.value)})} 
              />
            </label>
            <label>
              Strength: 
              <input 
                type="number" 
                value={editingPlayerStats.strength} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, strength: Number(e.target.value)})} 
              />
            </label>
            <label>
              Dexterity: 
              <input 
                type="number" 
                value={editingPlayerStats.dexterity} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, dexterity: Number(e.target.value)})} 
              />
            </label>
            <label>
              Constitution: 
              <input 
                type="number" 
                value={editingPlayerStats.constitution} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, constitution: Number(e.target.value)})} 
              />
            </label>
            <label>
              Wisdom: 
              <input 
                type="number" 
                value={editingPlayerStats.wisdom} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, wisdom: Number(e.target.value)})} 
              />
            </label>
            <label>
              Charisma: 
              <input 
                type="number" 
                value={editingPlayerStats.charisma} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, charisma: Number(e.target.value)})} 
              />
            </label>
            <label>
              Level: 
              <input 
                type="number" 
                value={editingPlayerStats.level} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, level: Number(e.target.value)})} 
              />
            </label>
            <label>
              Resistance: 
              <input 
                type="number" 
                value={editingPlayerStats.resistance} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, resistance: Number(e.target.value)})} 
              />
            </label>
            <label>
              Stability: 
              <input 
                type="number" 
                value={editingPlayerStats.stability} 
                onChange={(e) => setEditingPlayerStats({...editingPlayerStats, stability: Number(e.target.value)})} 
              />
            </label>
            <button onClick={handleSaveStats}>Сохранить</button>
          </div>
        </div>
      )}
      {isModalOpen && (
            <div className="modal">
              <div className="modal-content">
                <span className="close" onClick={() => setIsModalOpen(false)}>
                  &times;
                </span>
                <h3>Добавить врага</h3>
                <label>
                  ID врага:
                  <input
                    type="text"
                    value={enemyId}
                    onChange={(e) => setEnemyId(e.target.value)}
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
                <button onClick={handleAddEnemy}>Добавить</button>
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
                <button onClick={handleUpdateToken}>Сохранить</button>
              </div>
            </div>
          )}
    </div>
  );
};

export default GameField;
