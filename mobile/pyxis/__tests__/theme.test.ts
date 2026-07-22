/**
 * @format
 */

import { riskBand } from '../src/theme';

describe('riskBand', () => {
  it('classifies critical scores (>= 80)', () => {
    expect(riskBand(80).label).toBe('Critical');
    expect(riskBand(100).label).toBe('Critical');
  });

  it('classifies high scores (60-79)', () => {
    expect(riskBand(60).label).toBe('High');
    expect(riskBand(79).label).toBe('High');
  });

  it('classifies medium scores (35-59)', () => {
    expect(riskBand(35).label).toBe('Medium');
    expect(riskBand(59).label).toBe('Medium');
  });

  it('classifies low scores (< 35)', () => {
    expect(riskBand(0).label).toBe('Low');
    expect(riskBand(34).label).toBe('Low');
  });

  it('gives every band a distinct color', () => {
    const colors = [riskBand(90), riskBand(65), riskBand(40), riskBand(10)].map(b => b.color);
    expect(new Set(colors).size).toBe(4);
  });
});
