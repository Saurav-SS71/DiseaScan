export type MessageSender = 'user' | 'assistant'

export interface Prediction {
  label: string
  confidence: number
}

export interface Message {
  id: string
  sender: MessageSender
  type: 'text' | 'image' | 'prediction'
  content?: string
  imageUrl?: string
  predictions?: Prediction[]
  explanation?: string
  timestamp: number
}

export interface Chat {
  id: string
  title: string
  messages: Message[]
  timestamp: number
}
