import api from '@/services/api'
import type { AxiosResponse, AxiosError } from 'axios'

interface LoginResponse {
  user: any
  token?: string
}

interface ApiErrorResponse {
  message: string
  code: string
  response: {
    data: [{ [key: string]: string[] }]
  }
  [key: string]: any
}

interface AuthError {
  message: string
  code: string
  field?: string
  details?: { [key: string]: string[] }
}

export function isAuthError(error: unknown): error is AuthError {
  return typeof error === 'object' && error !== null && 'message' in error && 'code' in error;
}

export class AuthService {
  private static handleError(error: AxiosError<ApiErrorResponse>): AuthError {
    console.log('error', error)

    if (error.response) {
      const { data } = error.response

      // If we have field-specific errors in details
      if (data) {
        // Get the first field with errors
        const firstField = Object.keys(data)[0]
        if (firstField && data[firstField]?.length > 0) {
          return {
            message: data[firstField][0],
            code: data.code,
            field: firstField,
            details: data,
          }
        }
      }

      // Fallback to general message
      return {
        message: data.message || 'An error occurred',
        code: data.code || error.response.status.toString(),
        details: data,
      }
    } else if (error.request) {
      // Request made but no response
      return {
        message: 'No response from server',
        code: 'NETWORK_ERROR',
      }
    } else {
      // Request setup error
      return {
        message: error.message,
        code: 'REQUEST_ERROR',
      }
    }
  }

  public static async login(email: string, password: string): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>('/dj-rest-auth/login/', {
        email,
        password,
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as AxiosError<ApiErrorResponse>)
    }
  }

  public static async logout(): Promise<void> {
    try {
      await api.post('/dj-rest-auth/logout/')
    } catch (error) {
      throw this.handleError(error as AxiosError<ApiErrorResponse>)
    }
  }

  public static async signup(email: string, password: string, courseId?: number): Promise<void> {
    try {
      await api.post('/dj-rest-auth/registration/', {
        email,
        password1: password,
        password2: password,
        course_id: courseId,
      })
    } catch (error) {
      throw this.handleError(error as AxiosError<ApiErrorResponse>)
    }
  }

  public static async verifyEmail(key: string): Promise<AxiosResponse> {
    try {
      return await api.post('/dj-rest-auth/registration/verify-email/', { key })
    } catch (error) {
      throw this.handleError(error as AxiosError<ApiErrorResponse>)
    }
  }

  public static async passwordReset(email: string): Promise<AxiosResponse> {
    try {
      return await api.post('/dj-rest-auth/password/reset/', { email })
    } catch (error) {
      throw this.handleError(error as AxiosError<ApiErrorResponse>)
    }
  }

  public static async passwordResetConfirm(uid: string, token: string, password: string): Promise<AxiosResponse> {
    try {
      return await api.post('/dj-rest-auth/password/reset/confirm/', { uid, token, new_password1: password, new_password2: password })
    } catch (error) {
      throw this.handleError(error as AxiosError<ApiErrorResponse>)
    }
  }

  public static async fetchUser(): Promise<any> {
    try {
      const response = await api.get('/dj-rest-auth/user/')
      return response.data
    } catch (error) {
      throw this.handleError(error as AxiosError<ApiErrorResponse>)
    }
  }

  public static async changePassword(oldPassword: string, newPassword: string): Promise<AxiosResponse> {
    try {
      return await api.post('/dj-rest-auth/password/change/', {
        old_password: oldPassword,
        new_password1: newPassword,
        new_password2: newPassword,
      })
    } catch (error) {
      throw this.handleError(error as AxiosError<ApiErrorResponse>)
    }
  }
}
