/**
 * Utility functions for safely extracting error messages from API responses
 */

export const extractErrorMessage = (error: any): string => {
  // Handle null/undefined
  if (!error) return 'An error occurred';
  
  // Handle string errors
  if (typeof error === 'string') return error;
  
  // Handle number errors
  if (typeof error === 'number') return String(error);
  
  // Handle FastAPI/Pydantic validation errors
  if (error && typeof error === 'object') {
    // Array of validation errors
    if (Array.isArray(error)) {
      return error.map((err: any) => {
        if (typeof err === 'string') return err;
        if (typeof err === 'number') return String(err);
        if (err && typeof err === 'object') {
          // Handle Pydantic validation error format
          if (err.msg && err.loc) {
            const location = Array.isArray(err.loc) ? err.loc.join('.') : String(err.loc);
            return `${location}: ${err.msg}`;
          }
          // Handle simple error objects
          if (err.msg) return String(err.msg);
          if (err.message) return String(err.message);
          // Convert object to readable string
          try {
            return JSON.stringify(err);
          } catch {
            return String(err);
          }
        }
        return String(err);
      }).join(', ');
    }
    
    // Single validation error object with Pydantic format
    if (error.msg && error.loc) {
      const location = Array.isArray(error.loc) ? error.loc.join('.') : String(error.loc);
      return `${location}: ${String(error.msg)}`;
    }
    
    // Single validation error object
    if (error.msg) return String(error.msg);
    if (error.message) return String(error.message);
    
    // Nested detail object
    if (error.detail) {
      if (typeof error.detail === 'string') return error.detail;
      if (typeof error.detail === 'number') return String(error.detail);
      
      // Array of validation errors in detail
      if (Array.isArray(error.detail)) {
        return error.detail.map((err: any) => {
          if (typeof err === 'string') return err;
          if (typeof err === 'number') return String(err);
          if (err && typeof err === 'object') {
            // Handle Pydantic validation error format
            if (err.msg && err.loc) {
              const location = Array.isArray(err.loc) ? err.loc.join('.') : String(err.loc);
              return `${location}: ${String(err.msg)}`;
            }
            // Handle simple error objects
            if (err.msg) return String(err.msg);
            if (err.message) return String(err.message);
            // Convert object to readable string
            try {
              return JSON.stringify(err);
            } catch {
              return String(err);
            }
          }
          return String(err);
        }).join(', ');
      }
      
      // Single validation error in detail with Pydantic format
      if (error.detail.msg && error.detail.loc) {
        const location = Array.isArray(error.detail.loc) ? error.detail.loc.join('.') : String(error.detail.loc);
        return `${location}: ${String(error.detail.msg)}`;
      }
      
      // Single validation error in detail
      if (error.detail.msg) return String(error.detail.msg);
      if (error.detail.message) return String(error.detail.message);
      
      // Recursive call for nested detail objects
      if (typeof error.detail === 'object') {
        return extractErrorMessage(error.detail);
      }
    }
    
    // Fallback: convert object to string safely
    try {
      return JSON.stringify(error);
    } catch {
      return String(error);
    }
  }
  
  // Final fallback
  return String(error);
};

export const extractApiErrorMessage = (error: any): string => {
  // Extract from axios error structure
  if (error?.response?.data) {
    return extractErrorMessage(error.response.data.detail || error.response.data);
  }
  
  // Extract from direct error
  return extractErrorMessage(error);
};