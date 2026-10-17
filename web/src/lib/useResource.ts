import { useEffect, useState } from 'react'

export type Resource<T> =
  | { status: 'loading'; data?: undefined; error?: undefined }
  | { status: 'ready'; data: T; error?: undefined }
  | { status: 'error'; data?: undefined; error: Error }

/** Load an async resource once per key. */
export function useResource<T>(load: () => Promise<T>, key = 'default'): Resource<T> {
  const [state, setState] = useState<Resource<T>>({ status: 'loading' })
  useEffect(() => {
    let alive = true
    setState({ status: 'loading' })
    load().then(
      (data) => alive && setState({ status: 'ready', data }),
      (error: Error) => alive && setState({ status: 'error', error }),
    )
    return () => {
      alive = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key])
  return state
}
