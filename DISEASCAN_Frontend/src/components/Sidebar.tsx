import { useState } from 'react'
import { Plus, MessageCircle, Trash2 } from 'lucide-react'

interface Chat {
  id: string
  title: string
  timestamp: number
}

interface SidebarProps {
  chats: Chat[]
  onNewChat: () => void
  onSelectChat: (id: string) => void
  onDeleteChat: (id: string) => void
  currentChatId: string | null
}

export function Sidebar({
  chats,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  currentChatId,
}: SidebarProps) {
  const [hoverId, setHoverId] = useState<string | null>(null)

  return (
    <div className="w-64 bg-dark-900 border-r border-dark-700 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-dark-700">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-800 hover:bg-dark-700 rounded-lg transition-colors duration-200"
        >
          <Plus size={18} />
          <span>New Chat</span>
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {chats.length === 0 ? (
          <div className="text-center text-dark-400 text-sm py-8">
            No previous chats
          </div>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.id}
              onMouseEnter={() => setHoverId(chat.id)}
              onMouseLeave={() => setHoverId(null)}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors duration-150 group ${
                currentChatId === chat.id
                  ? 'bg-dark-700'
                  : 'hover:bg-dark-800'
              }`}
              onClick={() => onSelectChat(chat.id)}
            >
              <MessageCircle size={16} className="flex-shrink-0 text-dark-400" />
              <span className="flex-1 text-sm truncate">{chat.title}</span>
              {hoverId === chat.id && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDeleteChat(chat.id)
                  }}
                  className="p-1 hover:bg-dark-600 rounded transition-colors duration-150"
                >
                  <Trash2 size={14} className="text-dark-400" />
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-dark-700 text-xs text-dark-400">
        <div>DiseaScan v1.0</div>
        <div>Disease Detection AI</div>
      </div>
    </div>
  )
}
