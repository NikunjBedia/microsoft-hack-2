// useAxios.ts
import { useState } from 'react';
import axios from '../axios';
import { AxiosRequestConfig, AxiosResponse } from 'axios';

interface UseAxiosReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: (body?: any) => Promise<void>;  // Accept a dynamic body argument
}

function useAxios<T = unknown>(
  url: string,
  method: AxiosRequestConfig['method'] = 'GET',
  initialBody: any = null,  // Default initial body
  options: AxiosRequestConfig = {}
): UseAxiosReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async (body = initialBody) => {
    setLoading(true);
    setError(null);

    try {
      const response: AxiosResponse<T> = await axios({
        url,
        method,
        data: body,
        ...options,
      });
      setData(response.data);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, refetch: fetchData };
}

export default useAxios;
