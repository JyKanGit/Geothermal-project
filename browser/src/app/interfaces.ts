export interface dataPoint {
    date: Date;
    value: number;
}


export interface chartDataInfo {
    chartTitle: string;
    chartDataPoints: dataPoint[];
    lastUpdate: string;
    yAxisTitle: string;
}


export interface responseData {
    valid: boolean;
    data: chartDataInfo;
    message: Date;
}