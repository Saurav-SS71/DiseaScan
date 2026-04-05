import { useState, useRef } from 'react'
import { Send } from 'lucide-react'
import { ImageUpload } from './ImageUpload'

interface InputBoxProps {
  onSendMessage: (text: string, imageFile?: File, imagePreview?: string) => void
  isLoading: boolean
}

export function InputBox({ onSendMessage, isLoading }: InputBoxProps) {
  const [text, setText] = useState('')
  const [selectedImage, setSelectedImage] = useState<{
    file: File
    preview: string
  } | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const trimmedText = text.trim()

    if (!trimmedText && !selectedImage) return

    if (selectedImage) {
      onSendMessage(
        trimmedText || 'Analyze this image',
        selectedImage.file,
        selectedImage.preview
      )
    } else {
      onSendMessage(trimmedText)
    }

    setText('')
    setSelectedImage(null)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleImageSelect = (file: File, preview: string) => {
    setSelectedImage({ file, preview })
  }

  const handleRemoveImage = () => {
    setSelectedImage(null)
  }

  return (
    <div className="border-t border-dark-700 p-4 bg-dark-900">
      <div className="space-y-4">
        {/* Image Preview */}
        {selectedImage && (
          <div className="flex gap-3 items-end">
            <div className="relative">
              <img
                src={selectedImage.preview}
                alt="Selected"
                className="h-20 w-20 object-cover rounded-lg"
              />
              <button
                onClick={handleRemoveImage}
                className="absolute -top-2 -right-2 bg-red-600 rounded-full w-6 h-6 flex items-center justify-center text-white text-sm hover:bg-red-700 transition-colors"
              >
                ×
              </button>
            </div>
            <span className="text-sm text-dark-300">Image selected</span>
          </div>
        )}

        {/* Image Upload Area (when no image selected) */}
        {!selectedImage && <ImageUpload onImageSelect={handleImageSelect} isDisabled={isLoading} />}

        {/* Input Area */}
        <div className="flex gap-3">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about the diagnosis or describe symptoms..."
            disabled={isLoading}
            className="flex-1 bg-dark-800 border border-dark-700 rounded-lg px-4 py-3 text-sm resize-none placeholder-dark-500 text-dark-100 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            rows={3}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || (!text.trim() && !selectedImage)}
            className="px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-dark-700 disabled:text-dark-500 rounded-lg transition-colors duration-200 flex items-center justify-center disabled:cursor-not-allowed"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
