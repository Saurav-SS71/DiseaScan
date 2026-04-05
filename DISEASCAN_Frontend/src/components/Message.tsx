import { useState, useEffect } from 'react'
import { Message as MessageType } from '../types'

interface MessageProps {
  message: MessageType
}

export function Message({ message }: MessageProps) {
  const [displayedText, setDisplayedText] = useState('')
  const isUser = message.sender === 'user'

  useEffect(() => {
    if (message.sender === 'assistant' && message.type === 'text') {
      let index = 0
      const text = message.content as string
      const interval = setInterval(() => {
        if (index < text.length) {
          setDisplayedText(text.slice(0, index + 1))
          index++
        } else {
          clearInterval(interval)
        }
      }, 5)

      return () => clearInterval(interval)
    } else {
      setDisplayedText(message.content as string)
    }
  }, [message])

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-slide-in`}>
      <div
        className={`max-w-2xl px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-dark-800 text-dark-100 rounded-bl-none'
        }`}
      >
        {message.type === 'text' ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {displayedText}
            {message.sender === 'assistant' &&
              displayedText.length < (message.content as string).length && (
                <span className="animate-pulse">▊</span>
              )}
          </p>
        ) : message.type === 'image' ? (
          <div>
            <img
              src={message.imageUrl}
              alt="User uploaded"
              className="max-w-sm rounded-lg mb-2"
            />
            {message.content && (
              <p className="text-sm text-gray-200">{message.content}</p>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {/* Predictions Table */}
            <div className="space-y-2">
              <h3 className="font-semibold text-sm">Disease Predictions:</h3>
              <div className="space-y-1">
                {(message.predictions || []).map((pred, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between text-sm bg-dark-700 px-3 py-2 rounded"
                  >
                    <span>{pred.label}</span>
                    <span className="font-semibold text-blue-400">
                      {(pred.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Explanation */}
            {message.explanation && (
              <div className="mt-3 pt-3 border-t border-dark-600">
                <p className="text-sm leading-relaxed text-gray-300">
                  {message.explanation}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
