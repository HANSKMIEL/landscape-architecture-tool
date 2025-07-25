import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { parsePhoneNumber, isValidPhoneNumber } from 'libphonenumber-js'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

// Additional utility functions for the landscape architecture application
export function formatCurrency(amount, currency = 'EUR') {
  return new Intl.NumberFormat('nl-NL', {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

export function formatDate(date, locale = 'nl-NL') {
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date))
}

export function formatPhoneNumber(phone, defaultCountry = 'NL') {
  try {
    const phoneNumber = parsePhoneNumber(phone, defaultCountry)
    return phoneNumber.formatNational()
  } catch (error) {
    // Fallback to basic formatting for Dutch numbers
    const cleaned = phone.replace(/\D/g, '')
    if (cleaned.length === 10 && cleaned.startsWith('0')) {
      return cleaned.replace(/(\d{2})(\d{3})(\d{2})(\d{3})/, '$1 $2 $3 $4')
    }
    return phone
  }
}

export function validatePhoneNumber(phone, defaultCountry = 'NL') {
  try {
    return isValidPhoneNumber(phone, defaultCountry)
  } catch (error) {
    return false
  }
}

export function validateEmail(email) {
  // More robust email validation regex following RFC 5322 standard
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/
  return emailRegex.test(email) && email.length <= 254
}

export function validateDutchPostalCode(postalCode) {
  const dutchPostalCodeRegex = /^[1-9][0-9]{3}\s?[A-Z]{2}$/i
  return dutchPostalCodeRegex.test(postalCode)
}

export function generateId() {
  return Math.random().toString(36).substr(2, 9)
}

export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

export function truncateText(text, maxLength = 100) {
  if (text.length <= maxLength) return text
  return text.substr(0, maxLength) + '...'
}

export function capitalizeFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export function slugify(text) {
  return text
    .toString()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-')
    .replace(/^-+/, '')
    .replace(/-+$/, '')
}

