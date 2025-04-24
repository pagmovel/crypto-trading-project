// src/utils/helpers.ts

export function formatData(data: any): string {
    return JSON.stringify(data, null, 2);
}

export function log(message: string): void {
    console.log(`[LOG] ${new Date().toISOString()}: ${message}`);
}

export function calculatePercentageChange(oldValue: number, newValue: number): number {
    if (oldValue === 0) return 0;
    return ((newValue - oldValue) / oldValue) * 100;
}