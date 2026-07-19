import { expect, test } from '@playwright/test';

test('core investigation workflow is interactive', async ({ page }, testInfo) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Compliance command center' })).toBeVisible();

  if (testInfo.project.name === 'mobile-chromium') {
    await page.getByRole('button', { name: 'Toggle navigation' }).click();
  }

  await page.getByRole('button', { name: 'Case queue' }).click();
  await expect(page.getByRole('heading', { name: 'Case queue' })).toBeVisible();
  await page.getByRole('tab', { name: 'Critical' }).click();
  const caseControl = page.getByRole('button', { name: /CASE-1001/ });
  await expect(caseControl).toBeVisible();
  await caseControl.click();
  await expect(page.getByRole('dialog', { name: 'Nusantara Textiles' })).toBeVisible();
  await page.getByRole('button', { name: 'Open investigation' }).click();
  await expect(page.getByRole('heading', { name: 'Scenario arena', exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Transaction layering' })).toBeVisible();
});

test('overview renders at the target viewport', async ({ page }, testInfo) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Compliance command center' })).toBeVisible();
  await page.screenshot({
    path: testInfo.outputPath(`overview-${testInfo.project.name}.png`),
    fullPage: true,
  });
});
