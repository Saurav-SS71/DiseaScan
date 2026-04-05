import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface ApiClient extends AxiosInstance {}

const apiClient: ApiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface PredictionResponse {
  predictions: Array<{
    label: string
    confidence: number
  }>
}

export interface ExplanationResponse {
  explanation: string
}

export const api = {
  async predictDisease(imageFile: File): Promise<PredictionResponse> {
    const formData = new FormData()
    formData.append('file', imageFile)

    try {
      const response = await apiClient.post<PredictionResponse>(
        '/predict',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      return response.data
    } catch (error) {
      console.error('Error predicting disease:', error)
      throw error
    }
  },

  async getExplanation(
    diseaseLabel: string,
    confidence: number
  ): Promise<ExplanationResponse> {
    try {
      const response = await apiClient.post<ExplanationResponse>(
        '/explain',
        {
          disease: diseaseLabel,
          confidence,
        }
      )
      return response.data
    } catch (error) {
      console.error('Error getting explanation:', error)
      throw error
    }
  },

  setBaseURL(url: string) {
    apiClient.defaults.baseURL = url
  },
}

export default apiClient
