import { describe, it, expect } from 'vitest'
import { formatRelativeDate, formatDuration, formatViewCount } from './format'

describe('formatDuration', () => {
  it('formats minutes:seconds', () => {
    expect(formatDuration('PT4M13S')).toBe('4:13')
  })

  it('formats hours:minutes:seconds with zero-padding', () => {
    expect(formatDuration('PT1H2M5S')).toBe('1:02:05')
  })

  it('returns null for missing/invalid input', () => {
    expect(formatDuration(null)).toBeNull()
    expect(formatDuration('')).toBeNull()
    expect(formatDuration('not-a-duration')).toBeNull()
  })

  it('handles duration with only seconds', () => {
    expect(formatDuration('PT45S')).toBe('0:45')
  })
})

describe('formatViewCount', () => {
  it('returns null for zero/falsy counts', () => {
    expect(formatViewCount(0)).toBeNull()
    expect(formatViewCount(null)).toBeNull()
    expect(formatViewCount(undefined)).toBeNull()
  })

  it('formats small counts as-is', () => {
    expect(formatViewCount(1)).toBe('1 vue')
    expect(formatViewCount(42)).toBe('42 vues')
  })

  it('formats thousands with k suffix', () => {
    expect(formatViewCount(1500)).toBe('1.5 k vues')
    expect(formatViewCount(2000)).toBe('2 k vues')
  })

  it('formats millions with M suffix', () => {
    expect(formatViewCount(2_500_000)).toBe('2.5 M de vues')
    expect(formatViewCount(3_000_000)).toBe('3 M de vues')
  })
})

describe('formatRelativeDate', () => {
  it('returns empty string for missing input', () => {
    expect(formatRelativeDate(null)).toBe('')
    expect(formatRelativeDate(undefined)).toBe('')
  })

  it('returns "à l\'instant" for very recent timestamps', () => {
    expect(formatRelativeDate(new Date().toISOString())).toBe("à l'instant")
  })

  it('formats a timestamp from a few hours ago', () => {
    const threeHoursAgo = new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
    expect(formatRelativeDate(threeHoursAgo)).toBe('il y a 3 heures')
  })

  it('formats a timestamp from a year ago', () => {
    const oneYearAgo = new Date(Date.now() - 400 * 24 * 60 * 60 * 1000).toISOString()
    expect(formatRelativeDate(oneYearAgo)).toBe('il y a 1 an')
  })
})
