import { AfterContentChecked, AfterContentInit, Component, OnInit } from '@angular/core';
import { HttpGetService } from '../app/http-get.service'
import { chartDataInfo, dataPoint, responseData } from './interfaces';
import { formatDate } from '@angular/common';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})

export class AppComponent implements AfterContentInit{
  constructor(private getService: HttpGetService)
  {

  }

  loaded: boolean  = false;
  electricityPriceChart: chartDataInfo = {chartTitle: "", chartDataPoints: [], lastUpdate: "", yAxisTitle: ""};
  consumptionChart: chartDataInfo = {chartTitle: "", chartDataPoints: [], lastUpdate: "", yAxisTitle: ""};
  temperatureInChart: chartDataInfo = {chartTitle: "", chartDataPoints: [], lastUpdate: "", yAxisTitle: ""};
  temperatureOutChart: chartDataInfo = {chartTitle: "", chartDataPoints: [], lastUpdate: "", yAxisTitle: ""};
  temperatureSetChart: chartDataInfo = {chartTitle: "", chartDataPoints: [], lastUpdate: "", yAxisTitle: ""};

  show: boolean = true
  
  readonly timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  ngAfterContentInit(): void {
      this.electricityPriceChart = this.getChartData("/api/getElectricity");
      this.consumptionChart = this.getChartData("/api/getConsumption");
      this.temperatureInChart = this.getChartData("/api/getTemperature?id=in");
      this.temperatureOutChart = this.getChartData("/api/getTemperature?id=out");
      this.temperatureSetChart = this.getChartData("/api/getTemperature?id=set");
  }


  getChartData(url: string): chartDataInfo {
    let returnData: chartDataInfo = {chartTitle: "", chartDataPoints: [], lastUpdate: "", yAxisTitle: ""};
    this.getService.getData(url).subscribe(
      (response: responseData) => {
        if (!response.valid)
        {
          console.log("Response not valid, error=", response.message);
          return
        }
        returnData.chartTitle = response.data.chartTitle;
        returnData.lastUpdate = response.data.lastUpdate;
        returnData.yAxisTitle = response.data.yAxisTitle;
        for (const dateTime in response.data.chartDataPoints)
        {
            const newDataPoint: dataPoint = {date: new Date(dateTime), value: Number(response.data.chartDataPoints[dateTime])}
            returnData.chartDataPoints.push(newDataPoint)
        }
        
      },
      (error) => {
        console.error('Error fetching data:', error);
      }
    );
    return returnData;
  } 


  updateBtnClicked()
  {
    this.getService.getData("/api/updateApplication");
  }


  forceElectricityPriceUpdateClicked()
  {
    this.getService.getData("/api/forceElectricityUpdate").subscribe();
  }

  formatLastUpdate(date: string): string
  {
    return formatDate(new Date(date), "dd.M HH:mm:ss", "en-FI")
  }
}