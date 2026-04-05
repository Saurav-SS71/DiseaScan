import { useRef, useState } from 'react'
import { Image } from 'lucide-react'

interface ImageUploadProps {
  onImageSelect: (file: File, preview: string) => void
  isDisabled: boolean
}

export function ImageUpload({ onImageSelect, isDisabled }: ImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileSelect = (file: File) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        onImageSelect(file, e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.currentTarget.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        setIsDragging(true)
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => !isDisabled && inputRef.current?.click()}
      className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors duration-200 ${
        isDisabled
          ? 'border-dark-600 bg-dark-800 text-dark-500 cursor-not-allowed'
          : isDragging
            ? 'border-blue-500 bg-blue-900 bg-opacity-20'
            : 'border-dark-600 hover:border-blue-500 hover:bg-dark-800'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="hidden"
        disabled={isDisabled}
      />
      <div className="flex flex-col items-center gap-2">
        <Image size={20} />
        <div className="text-sm">
          <p className="font-medium">Click to upload or drag image</p>
          <p className="text-xs text-dark-400">PNG, JPG, GIF up to 10MB</p>
        </div>
      </div>
    </div>
  )
}
