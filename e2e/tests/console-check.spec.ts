import { test, expect } from '@playwright/test'

const PAGES = ['/', '/notices', '/talk-record']

test('no console errors on key pages', async ({ page }) => {
  const errors: string[] = []
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text())
  })
  for (const path of PAGES) {
    await page.goto(path)
    await page.waitForLoadState('networkidle')
  }
  expect(errors).toEqual([])
})