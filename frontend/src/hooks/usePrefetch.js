/**
 * Hook for prefetching lazy-loaded components
 * Improves perceived performance by preloading components on hover
 */

import { useCallback } from 'react'

// Component prefetch functions
const prefetchFunctions = {
  dashboard: () => import('../components/Dashboard'),
  suppliers: () => import('../components/Suppliers'),
  plants: () => import('../components/Plants'),
  products: () => import('../components/Products'),
  clients: () => import('../components/Clients'),
  projects: () => import('../components/Projects'),
  'plant-recommendations': () => import('../components/PlantRecommendations'),
  reports: () => import('../components/Reports'),
  settings: () => import('../components/Settings'),
}

// Track which components have been prefetched
const prefetched = new Set()

export const usePrefetch = () => {
  const prefetch = useCallback((componentName) => {
    if (!componentName || prefetched.has(componentName)) {
      return
    }

    const prefetchFn = prefetchFunctions[componentName]
    if (prefetchFn) {
      prefetchFn()
        .then(() => {
          prefetched.add(componentName)
          console.debug(`Prefetched component: ${componentName}`)
        })
        .catch((error) => {
          console.warn(`Failed to prefetch component ${componentName}:`, error)
        })
    }
  }, [])

  const prefetchOnHover = useCallback((componentName) => {
    return {
      onMouseEnter: () => prefetch(componentName),
      onFocus: () => prefetch(componentName), // Also prefetch on keyboard navigation
    }
  }, [prefetch])

  return { prefetch, prefetchOnHover }
}

export default usePrefetch