import { useRef, useEffect } from 'react'
import { Message as MessageType } from '../types'
import { Message } from './Message'

interface ChatWindowProps {
  messages: MessageType[]
  isLoading: boolean
}

export function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const scrollEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-dark-900">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="text-6xl mb-4">🔬</div>
            <h1 className="text-3xl font-bold text-dark-100 mb-2">DiseaScan</h1>
            <p className="text-dark-400 max-w-md">
              Upload an image to detect diseases and get AI-powered insights
            </p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <Message key={index} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-md">
                  <div className="px-4 py-3 rounded-lg bg-dark-800 text-dark-100">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                        style={{ animationDelay: '0.1s' }}
                      />
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                        style={{ animationDelay: '0.2s' }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={scrollEndRef} />
      </div>
    </div>
  )
}
