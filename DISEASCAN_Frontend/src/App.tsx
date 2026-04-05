import { useState, useEffect, useCallback } from 'react'
import { Sidebar } from './components/Sidebar'
import { ChatWindow } from './components/ChatWindow'
import { InputBox } from './components/InputBox'
import { api } from './services/api'
import { Chat, Message } from './types'
import './index.css'

// Simple ID generator
const generateId = () => Math.random().toString(36).substring(2, 15)

// Mock explanation data for when API is not available
const mockExplanations: { [key: string]: string } = {
  'Healthy Skin': `This appears to be healthy skin. Characteristics include even tone, smooth texture, and absence of significant lesions or abnormalities. Continue maintaining good skincare practices with daily moisturizing, sun protection, and a balanced diet.`,

  'Eczema': `Eczema is a chronic inflammatory skin condition characterized by intense itching, redness, and dry patches. Common triggers include irritants, allergens, and stress. Treatment typically involves moisturizing regularly, avoiding harsh soaps, and using topical corticosteroids as prescribed.`,

  'Psoriasis': `Psoriasis is an autoimmune condition causing red, scaly patches on the skin. It's not contagious and often runs in families. Management includes topical treatments, phototherapy, and systemic medications depending on severity. Stress management is also important.`,

  'Acne': `Acne results from clogged pores due to excess sebum and bacteria. It's most common in teenagers but can occur at any age. Treatment options include topical retinoids, benzoyl peroxide, salicylic acid, and in severe cases, oral antibiotics or isotretinoin.`,

  'Melanoma': `Melanoma is a serious form of skin cancer requiring immediate medical attention. Risk factors include sun exposure, fair skin, and family history. Early detection is crucial. Seek professional dermatological evaluation and follow screening recommendations.`,

  'Vitiligo': `Vitiligo is a condition causing loss of skin pigmentation in patches. It's caused by destruction of melanocytes and is not contagious. Treatment options include topical corticosteroids, calcineurin inhibitors, and phototherapy. Psychological support is valuable.`,
}

export default function App() {
  const [chats, setChats] = useState<Chat[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Load chats from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('diseascan_chats')
    if (saved) {
      try {
        setChats(JSON.parse(saved))
      } catch (error) {
        console.error('Failed to load chats:', error)
      }
    }
  }, [])

  // Save chats to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('diseascan_chats', JSON.stringify(chats))
  }, [chats])

  const getCurrentChat = useCallback(() => {
    return chats.find((c) => c.id === currentChatId)
  }, [chats, currentChatId])

  const createNewChat = () => {
    const newChat: Chat = {
      id: generateId(),
      title: `Chat ${new Date().toLocaleDateString()}`,
      messages: [],
      timestamp: Date.now(),
    }
    setChats([newChat, ...chats])
    setCurrentChatId(newChat.id)
  }

  const deleteChat = (id: string) => {
    setChats(chats.filter((c) => c.id !== id))
    if (currentChatId === id) {
      setCurrentChatId(null)
    }
  }

  const selectChat = (id: string) => {
    setCurrentChatId(id)
  }

  const addMessage = (message: Message) => {
    setChats(
      chats.map((chat) => {
        if (chat.id === currentChatId) {
          return {
            ...chat,
            messages: [...chat.messages, message],
          }
        }
        return chat
      })
    )
  }

  const handleSendMessage = async (
    text: string,
    imageFile?: File,
    imagePreview?: string
  ) => {
    if (!currentChatId) {
      createNewChat()
    }

    // Add user message
    const userMessage: Message = {
      id: generateId(),
      sender: 'user',
      type: imageFile ? 'image' : 'text',
      content: text,
      imageUrl: imagePreview,
      timestamp: Date.now(),
    }

    addMessage(userMessage)

    // Update chat title if it's the first message
    const chat = getCurrentChat()
    if (chat && chat.messages.length === 0) {
      const title = text.slice(0, 30) || 'Image Analysis'
      setChats(
        chats.map((c) =>
          c.id === currentChatId ? { ...c, title } : c
        )
      )
    }

    if (imageFile) {
      setIsLoading(true)
      try {
        // Get predictions from backend
        const response = await api.predictDisease(imageFile)
        const predictions = response.predictions

        // Add prediction message
        const predictionMessage: Message = {
          id: generateId(),
          sender: 'assistant',
          type: 'prediction',
          predictions: predictions,
          timestamp: Date.now(),
        }

        addMessage(predictionMessage)

        // Get explanation for top prediction
        const topPrediction = predictions[0]
        let explanation =
          mockExplanations[topPrediction.label] ||
          `${topPrediction.label} detected with ${(topPrediction.confidence * 100).toFixed(1)}% confidence. This indicates the analyzed image contains characteristics associated with ${topPrediction.label}. Please consult with a healthcare professional for proper diagnosis and treatment recommendations.`

        // Try to get explanation from API
        try {
          const explanationResponse = await api.getExplanation(
            topPrediction.label,
            topPrediction.confidence
          )
          explanation = explanationResponse.explanation
        } catch (error) {
          // Use mock explanation if API fails
          console.log('Using mock explanation')
        }

        // Add explanation message
        const explanationMessage: Message = {
          id: generateId(),
          sender: 'assistant',
          type: 'text',
          content: explanation,
          timestamp: Date.now(),
        }

        addMessage(explanationMessage)
      } catch (error) {
        console.error('Error processing image:', error)

        // Add error message
        const errorMessage: Message = {
          id: generateId(),
          sender: 'assistant',
          type: 'text',
          content: `Sorry, I encountered an error while analyzing the image. Please make sure the backend API is running at ${import.meta.env.VITE_API_URL || 'http://localhost:8000'} and try again.`,
          timestamp: Date.now(),
        }

        addMessage(errorMessage)
      } finally {
        setIsLoading(false)
      }
    }
  }

  const currentChat = getCurrentChat()

  return (
    <div className="flex h-screen bg-dark-900">
      <Sidebar
        chats={chats}
        onNewChat={createNewChat}
        onSelectChat={selectChat}
        onDeleteChat={deleteChat}
        currentChatId={currentChatId}
      />

      <div className="flex-1 flex flex-col">
        {currentChat ? (
          <>
            <ChatWindow messages={currentChat.messages} isLoading={isLoading} />
            <InputBox
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <button
              onClick={createNewChat}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors duration-200"
            >
              Start New Chat
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
